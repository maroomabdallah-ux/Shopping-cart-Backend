from datetime import datetime
from enum import StrEnum

from pydantic import Field
from sqlmodel import SQLModel


class OrderItemCreate(SQLModel):
    product_id: int
    quantity: int = Field(default=1, gt=0, le=99)


class OrderCreate(SQLModel):
    customer_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=30)
    address: str = Field(min_length=5, max_length=300)
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderStatusUpdate(SQLModel):
    status: OrderStatus


class OrderItemRead(SQLModel):
    product_id: int
    title: str
    price: float
    quantity: int


class OrderRead(SQLModel):
    id: int
    user_id: int | None
    customer_name: str
    phone: str
    address: str
    subtotal: float
    delivery: float
    total: float
    status: str
    payment_status: str
    created_at: datetime
    items: list[OrderItemRead]
