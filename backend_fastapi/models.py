from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="customer")
    is_blocked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())

    cart_items = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    image_url = Column(Text, nullable=True)
    rating = Column(Numeric(3, 2), default=4.50)
    reviews_count = Column(Integer, default=12)
    stock = Column(Integer, nullable=False, default=25)
    created_at = Column(DateTime, server_default=func.now())

    category = relationship("Category", back_populates="products")


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), nullable=False, default="Pending")  # Pending, Shipped, Delivered
    payment_method = Column(String(50), nullable=False, default="Stripe")
    payment_status = Column(String(30), nullable=False, default="Paid")
    shipping_address = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
