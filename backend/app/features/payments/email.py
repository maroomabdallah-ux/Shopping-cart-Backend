"""Payment confirmation email delivery."""

import logging
import smtplib
from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import formataddr
from html import escape

from sqlmodel import Session, select

from app.core.config import get_settings
from app.features.orders.model import Order, OrderItem
from app.features.users.model import User

logger = logging.getLogger(__name__)


def _build_message(
    recipient: str,
    order: Order,
    items: list[OrderItem],
    paid_amount: float,
) -> EmailMessage:
    settings = get_settings()
    rows = "\n".join(
        f"- {item.title} × {item.quantity}: "
        f"{item.price * item.quantity:.3f} JOD"
        for item in items
    )
    html_rows = "".join(
        "<tr>"
        f"<td>{escape(item.title)}</td>"
        f"<td>{item.quantity}</td>"
        f"<td>{item.price:.3f} JOD</td>"
        f"<td>{item.price * item.quantity:.3f} JOD</td>"
        "</tr>"
        for item in items
    )

    message = EmailMessage()
    message["Subject"] = f"Payment successful – order #{order.id}"
    message["From"] = formataddr(
        (settings.smtp_from_name, settings.smtp_from_email)
    )
    message["To"] = recipient
    message.set_content(
        f"""Hello {order.customer_name},

Your payment was completed successfully.

Order #{order.id}
{rows}

Subtotal: {order.subtotal:.3f} JOD
Delivery: {order.delivery:.3f} JOD
Amount paid: {paid_amount:.3f} JOD

Delivery address: {order.address}
Phone: {order.phone}
"""
    )
    message.add_alternative(
        f"""\
<!doctype html>
<html>
  <body style="font-family:Arial,sans-serif;color:#202124">
    <h2>Payment completed successfully</h2>
    <p>Hello {escape(order.customer_name)},</p>
    <p>Your payment for order <strong>#{order.id}</strong> was successful.</p>
    <table cellpadding="8" cellspacing="0" border="1"
           style="border-collapse:collapse;border-color:#ddd">
      <thead>
        <tr><th>Item</th><th>Quantity</th><th>Price</th><th>Total</th></tr>
      </thead>
      <tbody>{html_rows}</tbody>
    </table>
    <p>
      Subtotal: {order.subtotal:.3f} JOD<br>
      Delivery: {order.delivery:.3f} JOD<br>
      <strong>Amount paid: {paid_amount:.3f} JOD</strong>
    </p>
    <p>
      Delivery address: {escape(order.address)}<br>
      Phone: {escape(order.phone)}
    </p>
  </body>
</html>
""",
        subtype="html",
    )
    return message


def send_payment_confirmation(
    session: Session,
    order: Order,
    paid_amount: float,
) -> bool:
    """Send once after payment; an email failure never rolls back payment."""
    settings = get_settings()
    if order.payment_email_sent_at is not None:
        return True
    if not settings.smtp_host or not settings.smtp_from_email:
        logger.warning(
            "Payment email not sent for order %s: SMTP is not configured",
            order.id,
        )
        return False

    user = session.get(User, order.user_id)
    if user is None:
        logger.error("Payment email not sent: user for order %s not found", order.id)
        return False
    items = list(
        session.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all()
    )
    message = _build_message(user.email, order, items, paid_amount)

    try:
        if settings.smtp_use_ssl:
            smtp = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15)
        else:
            smtp = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15)
        with smtp:
            if settings.smtp_use_tls and not settings.smtp_use_ssl:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logger.exception("Payment email failed for order %s", order.id)
        return False

    order.payment_email_sent_at = datetime.now(UTC)
    session.add(order)
    session.commit()
    return True
