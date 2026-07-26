"""Product persistence model."""

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, max_length=200)
    description: str
    img: str
    rate: float = Field(ge=0, le=5)
    reviews: int = Field(default=0, ge=0)
    price: float = Field(gt=0)
    insteadOF: float = Field(gt=0)
    badge: str = Field(max_length=50)
