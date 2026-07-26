from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_
from sqlmodel import Session, select

from app.db.session import get_session
from app.dependencies import require_admin
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.routers.orders import build_order_response
from app.schemas.order import OrderRead, OrderStatusUpdate
from app.schemas.product import (
    ProductCreate,
    ProductPage,
    ProductRead,
    ProductUpdate,
)
from app.schemas.user import UserRead

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/products", response_model=ProductPage)
def list_admin_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=100),
    session: Session = Depends(get_session),
) -> ProductPage:
    statement = select(Product)
    count_statement = select(func.count()).select_from(Product)
    if search and search.strip():
        term = f"%{search.strip()}%"
        condition = or_(Product.title.ilike(term), Product.description.ilike(term))
        statement = statement.where(condition)
        count_statement = count_statement.where(condition)
    total = session.exec(count_statement).one()
    products = session.exec(
        statement.order_by(Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return ProductPage(
        items=[ProductRead.model_validate(product) for product in products],
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    session: Session = Depends(get_session),
) -> Product:
    product = Product(**payload.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.patch("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    session: Session = Depends(get_session),
) -> Product:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product.sqlmodel_update(payload.model_dump(exclude_unset=True))
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
) -> Response:
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    has_orders = session.exec(
        select(OrderItem.id).where(OrderItem.product_id == product_id).limit(1)
    ).first()
    if has_orders is not None:
        raise HTTPException(
            status_code=409,
            detail="Product belongs to an order and cannot be deleted",
        )
    session.delete(product)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
) -> list[User]:
    return list(session.exec(select(User).order_by(User.created_at.desc())).all())


@router.get("/orders", response_model=list[OrderRead])
def list_orders(
    order_status: str | None = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
) -> list[OrderRead]:
    statement = select(Order).order_by(Order.created_at.desc())
    if order_status:
        statement = statement.where(Order.status == order_status)
    orders = session.exec(statement).all()
    return [
        build_order_response(
            order,
            list(
                session.exec(
                    select(OrderItem).where(OrderItem.order_id == order.id)
                ).all()
            ),
        )
        for order in orders
    ]


@router.patch("/orders/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    session: Session = Depends(get_session),
) -> OrderRead:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = payload.status.value
    session.add(order)
    session.commit()
    session.refresh(order)
    items = list(
        session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    )
    return build_order_response(order, items)
