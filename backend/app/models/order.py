from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_name: str = Field(max_length=100)
    phone: str = Field(max_length=30)
    address: str = Field(max_length=300)
    subtotal: float = Field(ge=0)
    delivery: float = Field(ge=0)
    total: float = Field(ge=0)
    status: str = Field(default="pending", max_length=30)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        index=True,
    )


class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    title: str = Field(max_length=200)
    price: float = Field(gt=0)
    quantity: int = Field(gt=0)
