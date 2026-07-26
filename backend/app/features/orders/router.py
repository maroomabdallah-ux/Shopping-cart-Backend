from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db.session import get_session
from app.features.orders.model import Order, OrderItem
from app.features.orders.schemas import (
    OrderCreate,
    OrderItemRead,
    OrderRead,
)
from app.features.products.model import Product
from app.features.users.dependencies import get_current_user
from app.features.users.model import User, UserRole

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> OrderRead:
    product_ids = {item.product_id for item in payload.items}
    products = session.exec(select(Product).where(Product.id.in_(product_ids))).all()
    products_by_id = {product.id: product for product in products}

    missing_ids = sorted(product_ids - products_by_id.keys())
    if missing_ids:
        raise HTTPException(
            status_code=400,
            detail={"message": "Some products do not exist", "ids": missing_ids},
        )

    subtotal = round(
        sum(
            products_by_id[item.product_id].price * item.quantity
            for item in payload.items
        ),
        2,
    )
    delivery = 0 if subtotal >= 50 else 5
    order = Order(
        user_id=current_user.id,
        customer_name=payload.customer_name,
        phone=payload.phone,
        address=payload.address,
        subtotal=subtotal,
        delivery=delivery,
        total=round(subtotal + delivery, 2),
    )
    session.add(order)
    session.flush()

    order_items = []
    for item in payload.items:
        product = products_by_id[item.product_id]
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            title=product.title,
            price=product.price,
            quantity=item.quantity,
        )
        session.add(order_item)
        order_items.append(order_item)

    session.commit()
    session.refresh(order)
    return build_order_response(order, order_items)


@router.get("", response_model=list[OrderRead])
def list_my_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[OrderRead]:
    orders = session.exec(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    ).all()
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


@router.get("/{order_id}", response_model=OrderRead)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> OrderRead:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role != UserRole.ADMIN and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    return build_order_response(order, list(items))


def build_order_response(
    order: Order,
    items: list[OrderItem],
) -> OrderRead:
    return OrderRead(
        **order.model_dump(),
        items=[
            OrderItemRead(
                product_id=item.product_id,
                title=item.title,
                price=item.price,
                quantity=item.quantity,
            )
            for item in items
        ],
    )
