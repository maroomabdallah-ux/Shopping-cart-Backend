from pydantic import Field
from sqlmodel import SQLModel


class ProductCreate(SQLModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=2)
    img: str = Field(min_length=5)
    rate: float = Field(default=0, ge=0, le=5)
    reviews: int = Field(default=0, ge=0)
    price: float = Field(gt=0)
    insteadOF: float = Field(gt=0)
    badge: str = Field(min_length=1, max_length=50)


class ProductUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, min_length=2)
    img: str | None = Field(default=None, min_length=5)
    rate: float | None = Field(default=None, ge=0, le=5)
    reviews: int | None = Field(default=None, ge=0)
    price: float | None = Field(default=None, gt=0)
    insteadOF: float | None = Field(default=None, gt=0)
    badge: str | None = Field(default=None, min_length=1, max_length=50)


class ProductRead(SQLModel):
    id: int
    title: str
    description: str
    img: str
    rate: float
    reviews: int
    price: float
    insteadOF: float
    badge: str


class ProductPage(SQLModel):
    items: list[ProductRead]
    page: int
    page_size: int
    total: int
    pages: int
