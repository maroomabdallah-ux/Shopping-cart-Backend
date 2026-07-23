"""Create products, orders, and order items.

Revision ID: 20260723_01
Revises:
Create Date: 2026-07-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260723_01"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PRODUCTS = [
    ("Samsung Galaxy S26 Ultra 512GB — Black", "Privacy display, Galaxy AI camera and all-day durable battery.", "https://m.media-amazon.com/images/I/61UnzIc+97L._AC_SX300_SY300_QL70_FMwebp_.jpg", 4.8, 128, 1239, 1499, "Best seller"),
    ("Samsung Galaxy A17 5G 128GB — Gray", "Large AMOLED display, high-resolution camera and expandable storage.", "https://m.media-amazon.com/images/I/61n9YE0kF3L._AC_SY300_SX300_QL70_FMwebp_.jpg", 4.5, 86, 200, 279, "Great value"),
    ("Moto G 5G 2025 128GB — Forest Gray", "Unlocked smartphone with a bright display and a crisp 50MP camera.", "https://m.media-amazon.com/images/I/8160OiLlJEL._AC_SY300_SX300_QL70_FMwebp_.jpg", 4.7, 64, 205, 350, "New"),
    ("Apple iPhone 16 Pro 256GB — Desert Titanium", "Premium titanium design, powerful A18 Pro chip and advanced camera controls.", "https://m.media-amazon.com/images/I/61JvFLHZ6NL._AC_SX679_.jpg", 4.9, 214, 1099, 1249, "Premium pick"),
    ("Google Pixel 9 Pro 256GB — Obsidian", "Helpful Google AI, a brilliant Super Actua display and pro-level cameras.", "https://m.media-amazon.com/images/I/71lJz6Z7RUL._AC_SX679_.jpg", 4.7, 119, 899, 1049, "AI favorite"),
    ("OnePlus 13 256GB — Midnight Ocean", "Ultra-fast performance, smooth AMOLED display and rapid all-day charging.", "https://m.media-amazon.com/images/I/71d5fMDvq9L._AC_SX679_.jpg", 4.6, 92, 799, 899, "Fast charging"),
    ("Samsung Galaxy Z Flip6 256GB — Blue", "Compact foldable design with Galaxy AI and a versatile FlexWindow display.", "https://m.media-amazon.com/images/I/71-D3MZfZIL._AC_SX679_.jpg", 4.5, 73, 949, 1099, "Foldable"),
    ("Xiaomi 14T Pro 512GB — Titan Gray", "Leica-powered photography, flagship performance and lightning-fast charging.", "https://m.media-amazon.com/images/I/71NkiJbYmBL._AC_SX679_.jpg", 4.6, 58, 699, 799, "Camera pick"),
    ("Nothing Phone (2a) 256GB — Milk", "Distinctive Glyph design, smooth OLED display and clean Android experience.", "https://m.media-amazon.com/images/I/71ChLWTbPqL._AC_SX679_.jpg", 4.4, 81, 349, 429, "Unique design"),
]


def upgrade() -> None:
    product = op.create_table(
        "product",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("img", sa.String(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("reviews", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("insteadOF", sa.Float(), nullable=False),
        sa.Column("badge", sa.String(50), nullable=False),
        sa.CheckConstraint("rate >= 0 AND rate <= 5", name="ck_product_rate"),
        sa.CheckConstraint("reviews >= 0", name="ck_product_reviews"),
        sa.CheckConstraint("price > 0", name="ck_product_price"),
        sa.CheckConstraint('"insteadOF" > 0', name="ck_product_instead_of"),
    )
    op.create_index("ix_product_title", "product", ["title"])

    op.create_table(
        "order",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(30), nullable=False),
        sa.Column("address", sa.String(300), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("delivery", sa.Float(), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_order_created_at", "order", ["created_at"])

    op.create_table(
        "orderitem",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("order.id"), nullable=False),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("product.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
    )
    op.create_index("ix_orderitem_order_id", "orderitem", ["order_id"])
    op.create_index("ix_orderitem_product_id", "orderitem", ["product_id"])

    op.bulk_insert(
        product,
        [
            dict(
                title=row[0], description=row[1], img=row[2], rate=row[3],
                reviews=row[4], price=row[5], insteadOF=row[6], badge=row[7],
            )
            for row in PRODUCTS
        ],
    )


def downgrade() -> None:
    op.drop_table("orderitem")
    op.drop_table("order")
    op.drop_table("product")
