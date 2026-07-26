from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.db.session import get_session
from app.features.products.model import Product
from app.features.products.schemas import ProductPage, ProductRead

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductPage)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=3, ge=1, le=50),
    search: str | None = Query(default=None, max_length=100),
    session: Session = Depends(get_session),
) -> ProductPage:
    filters = []
    if search and search.strip():
        term = f"%{search.strip()}%"
        filters.append(
            or_(
                Product.title.ilike(term),
                Product.description.ilike(term),
            )
        )

    count_statement = select(func.count()).select_from(Product)
    statement = select(Product).order_by(Product.id)
    for condition in filters:
        count_statement = count_statement.where(condition)
        statement = statement.where(condition)

    total = session.exec(count_statement).one()
    products = session.exec(
        statement.offset((page - 1) * page_size).limit(page_size)
    ).all()

    return ProductPage(
        items=[ProductRead.model_validate(product) for product in products],
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
