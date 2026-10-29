from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# --- Auth & User Schemas ---
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    is_blocked: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Category Schemas ---
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

# --- Product Schemas ---
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    price: float = Field(..., ge=0)
    description: str = Field(..., min_length=5)
    category_id: int
    image_url: Optional[str] = None
    rating: float = Field(default=4.5, ge=0, le=5)
    stock: int = Field(default=25, ge=0)

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    description: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str
    category_id: int
    image_url: Optional[str]
    rating: float
    reviews_count: int
    stock: int

    class Config:
        from_attributes = True

# --- Cart Schemas ---
class CartItemUpsert(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductResponse

    class Config:
        from_attributes = True

# --- Order Schemas ---
class OrderCreate(BaseModel):
    shipping_address: str = Field(..., min_length=10)
    payment_method: str = Field(default="Stripe", pattern="^(Stripe|Razorpay|COD)$")

class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(Pending|Shipped|Delivered)$")

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    payment_method: str
    payment_status: str
    shipping_address: str
    created_at: Optional[datetime]
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
