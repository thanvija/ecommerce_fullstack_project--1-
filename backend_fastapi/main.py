from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from database import engine, Base, get_db
from models import User, Category, Product, Cart, Order, OrderItem
from schemas import (
    UserCreate, UserLogin, UserResponse,
    CategoryCreate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    CartItemUpsert, CartItemResponse,
    OrderCreate, OrderStatusUpdate, OrderResponse,
)
from security import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_admin,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Business APIs (FastAPI)",
    description="Customer & Admin REST APIs integrated with Django Auth & PostgreSQL/MySQL",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 1. AUTHENTICATION ENDPOINTS (Compatible with Django Auth JWT)
# ============================================================================
@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password=hash_password(payload.password),
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

@app.post("/api/auth/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Account has been blocked by administrator")
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

# ============================================================================
# 2. CUSTOMER MODULE: PRODUCT BROWSING, SEARCH, FILTER & DETAILS
# ============================================================================
@app.get("/api/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()

@app.get("/api/products", response_model=List[ProductResponse])
def list_products(
    search: Optional[str] = Query(default=None, description="Search by product name or description"),
    category_id: Optional[int] = Query(default=None, description="Filter by category_id"),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            (Product.name.ilike(pattern)) | (Product.description.ilike(pattern))
        )
    return query.order_by(Product.id.desc()).all()

@app.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ============================================================================
# 3. CUSTOMER MODULE: CART MANAGEMENT
# ============================================================================
@app.get("/api/cart", response_model=List[CartItemResponse])
def get_cart(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Cart).filter(Cart.user_id == current_user.id).all()

@app.post("/api/cart", response_model=CartItemResponse)
def add_or_update_cart(
    payload: CartItemUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Insufficient product stock")

    cart_item = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id, Cart.product_id == payload.product_id)
        .first()
    )
    if cart_item:
        cart_item.quantity = payload.quantity
    else:
        cart_item = Cart(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

@app.delete("/api/cart/{product_id}")
def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_item = (
        db.query(Cart)
        .filter(Cart.user_id == current_user.id, Cart.product_id == product_id)
        .first()
    )
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}

# ============================================================================
# 4. CUSTOMER MODULE: ORDER MANAGEMENT & PAYMENT
# ============================================================================
@app.post("/api/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0.0
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.product.name}",
            )
        total_amount += float(item.product.price) * item.quantity

    payment_status = "Pending (COD)" if payload.payment_method == "COD" else f"Paid via {payload.payment_method}"

    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status="Pending",
        payment_method=payload.payment_method,
        payment_status=payment_status,
        shipping_address=payload.shipping_address,
    )
    db.add(order)
    db.flush()

    for item in cart_items:
        item.product.stock -= item.quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.product.price,
        )
        db.add(order_item)
        db.delete(item)

    db.commit()
    db.refresh(order)
    return order

@app.get("/api/orders", response_model=List[OrderResponse])
def list_customer_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )

# ============================================================================
# 5. ADMIN MODULE: PRODUCT, CATEGORY, ORDER, USER & ANALYTICS MANAGEMENT
# ============================================================================
@app.post("/api/admin/categories", response_model=CategoryResponse, status_code=201)
def admin_create_category(
    payload: CategoryCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@app.put("/api/admin/categories/{category_id}", response_model=CategoryResponse)
def admin_update_category(
    category_id: int,
    payload: CategoryCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = payload.name
    category.description = payload.description
    db.commit()
    db.refresh(category)
    return category

@app.delete("/api/admin/categories/{category_id}")
def admin_delete_category(
    category_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}

@app.post("/api/admin/products", response_model=ProductResponse, status_code=201)
def admin_add_product(
    payload: ProductCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@app.put("/api/admin/products/{product_id}", response_model=ProductResponse)
def admin_update_product(
    product_id: int,
    payload: ProductUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

@app.delete("/api/admin/products/{product_id}")
def admin_delete_product(
    product_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}

@app.get("/api/admin/orders", response_model=List[OrderResponse])
def admin_list_all_orders(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.query(Order).order_by(Order.created_at.desc()).all()

@app.patch("/api/admin/orders/{order_id}/status", response_model=OrderResponse)
def admin_update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = payload.status
    if payload.status == "Delivered" and "COD" in order.payment_status:
        order.payment_status = "Paid (COD Collected)"
    db.commit()
    db.refresh(order)
    return order

@app.get("/api/admin/users", response_model=List[UserResponse])
def admin_list_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.created_at.desc()).all()

@app.patch("/api/admin/users/{user_id}/block", response_model=UserResponse)
def admin_toggle_block_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot block an admin user")
    user.is_blocked = not user.is_blocked
    db.commit()
    db.refresh(user)
    return user

@app.get("/api/admin/analytics")
def admin_reports_and_analytics(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_revenue = db.query(func.coalesce(func.sum(Order.total_amount), 0)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_users = db.query(func.count(User.id)).scalar()

    status_counts = (
        db.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )

    top_products = (
        db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("units_sold"),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    return {
        "total_revenue": float(total_revenue or 0),
        "total_orders": total_orders,
        "total_users": total_users,
        "orders_by_status": {status_name: count for status_name, count in status_counts},
        "top_selling_products": [
            {
                "product_id": p.id,
                "name": p.name,
                "units_sold": int(p.units_sold or 0),
                "revenue": float(p.revenue or 0),
            }
            for p in top_products
        ],
    }
