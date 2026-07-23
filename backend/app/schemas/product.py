from sqlmodel import SQLModel


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
