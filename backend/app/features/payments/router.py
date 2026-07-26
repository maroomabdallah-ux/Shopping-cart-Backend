from decimal import Decimal

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.session import get_session
from app.features.orders.model import Order, OrderItem
from app.features.users.dependencies import get_current_user
from app.features.users.model import User

router = APIRouter(prefix="/payments", tags=["payments"])


def _stripe() -> None:
    key = get_settings().stripe_secret_key
    if not key:
        raise HTTPException(status_code=503, detail="Stripe is not configured")
    stripe.api_key = key


def _minor_units(amount: float) -> int:
    # JOD has three decimal minor units.
    return int(Decimal(str(amount)) * 1000)


@router.post("/checkout/{order_id}")
def create_checkout_session(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    _stripe()
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if order.payment_status == "paid":
        raise HTTPException(status_code=409, detail="Order is already paid")

    items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).all()
    line_items = [
        {
            "price_data": {
                "currency": "jod",
                "product_data": {"name": item.title},
                "unit_amount": _minor_units(item.price),
            },
            "quantity": item.quantity,
        }
        for item in items
    ]
    if order.delivery:
        line_items.append(
            {
                "price_data": {
                    "currency": "jod",
                    "product_data": {"name": "Delivery"},
                    "unit_amount": _minor_units(order.delivery),
                },
                "quantity": 1,
            }
        )

    settings = get_settings()
    try:
        checkout = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            customer_email=current_user.email,
            client_reference_id=str(order.id),
            metadata={"order_id": str(order.id), "user_id": str(current_user.id)},
            success_url=(
                f"{settings.frontend_url}/?payment=success"
                "&session_id={CHECKOUT_SESSION_ID}#orders"
            ),
            cancel_url=f"{settings.frontend_url}/?payment=cancelled#orders",
        )
    except stripe.StripeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    order.stripe_checkout_session_id = checkout.id
    order.payment_status = "pending"
    session.add(order)
    session.commit()
    return {"checkout_url": checkout.url}


@router.post("/confirm/{checkout_session_id}")
def confirm_checkout_session(
    checkout_session_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict[str, str]:
    _stripe()
    order = session.exec(
        select(Order).where(
            Order.stripe_checkout_session_id == checkout_session_id,
            Order.user_id == current_user.id,
        )
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Payment session not found")
    checkout = stripe.checkout.Session.retrieve(checkout_session_id)
    if checkout.payment_status == "paid":
        order.payment_status = "paid"
        session.add(order)
        session.commit()
    return {"payment_status": order.payment_status}


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    settings = get_settings()
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.stripe_webhook_secret
        )
    except (ValueError, stripe.SignatureVerificationError) as error:
        raise HTTPException(status_code=400, detail="Invalid webhook") from error

    if event["type"] in {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
    }:
        checkout = event["data"]["object"]
        order = session.exec(
            select(Order).where(Order.stripe_checkout_session_id == checkout["id"])
        ).first()
        if order is not None and checkout.get("payment_status") == "paid":
            order.payment_status = "paid"
            session.add(order)
            session.commit()
    return {"received": True}
