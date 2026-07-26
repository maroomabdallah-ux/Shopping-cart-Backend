from sqlmodel import Session

from app.core.config import get_settings
from app.db.session import engine
from app.features.orders.model import Order, OrderItem
from app.features.payments.email import send_payment_confirmation
from app.features.users.model import User


class FakeSMTP:
    sent_messages = []

    def __init__(self, host: str, port: int, timeout: int) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        return None

    def starttls(self) -> None:
        return None

    def login(self, username: str, password: str) -> None:
        return None

    def send_message(self, message) -> None:
        self.sent_messages.append(message)


def test_payment_confirmation_contains_order_and_is_sent_once(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    monkeypatch.setattr(settings, "smtp_from_email", "orders@example.com")
    monkeypatch.setattr(
        "app.features.payments.email.smtplib.SMTP",
        FakeSMTP,
    )
    FakeSMTP.sent_messages.clear()

    with Session(engine) as session:
        user = User(
            name="Email Customer",
            email="buyer@example.com",
            password_hash="unused",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        order = Order(
            user_id=user.id,
            customer_name=user.name,
            phone="0790000000",
            address="Amman, Jordan",
            subtotal=20,
            delivery=3,
            total=23,
            payment_status="paid",
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        session.add(
            OrderItem(
                order_id=order.id,
                product_id=1,
                title="Test product",
                price=10,
                quantity=2,
            )
        )
        session.commit()

        assert send_payment_confirmation(session, order, 23) is True
        assert send_payment_confirmation(session, order, 23) is True

        assert order.payment_email_sent_at is not None
        assert len(FakeSMTP.sent_messages) == 1
        message = FakeSMTP.sent_messages[0]
        assert message["To"] == "buyer@example.com"
        assert f"order #{order.id}" in str(message["Subject"]).lower()
        assert "Amount paid: 23.000 JOD" in message.get_body(
            preferencelist=("plain",)
        ).get_content()
        assert "Test product" in message.get_body(
            preferencelist=("plain",)
        ).get_content()
