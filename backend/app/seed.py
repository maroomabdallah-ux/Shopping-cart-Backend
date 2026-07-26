from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.session import engine
from app.features.products.model import Product
from app.features.users.model import User, UserRole
from app.features.users.security import hash_password

PRODUCTS = [
    {
        "title": "Samsung Galaxy S26 Ultra 512GB — Black",
        "description": "Privacy display, Galaxy AI camera and all-day durable battery.",
        "img": "https://m.media-amazon.com/images/I/61UnzIc+97L._AC_SX300_SY300_QL70_FMwebp_.jpg",
        "rate": 4.8,
        "reviews": 128,
        "price": 1239,
        "insteadOF": 1499,
        "badge": "Best seller",
    },
    {
        "title": "Samsung Galaxy A17 5G 128GB — Gray",
        "description": (
            "Large AMOLED display, high-resolution camera and expandable storage."
        ),
        "img": "https://m.media-amazon.com/images/I/61n9YE0kF3L._AC_SY300_SX300_QL70_FMwebp_.jpg",
        "rate": 4.5,
        "reviews": 86,
        "price": 200,
        "insteadOF": 279,
        "badge": "Great value",
    },
    {
        "title": "Moto G 5G 2025 128GB — Forest Gray",
        "description": (
            "Unlocked smartphone with a bright display and a crisp 50MP camera."
        ),
        "img": "https://m.media-amazon.com/images/I/8160OiLlJEL._AC_SY300_SX300_QL70_FMwebp_.jpg",
        "rate": 4.7,
        "reviews": 64,
        "price": 205,
        "insteadOF": 350,
        "badge": "New",
    },
    {
        "title": "Apple iPhone 16 Pro 256GB — Desert Titanium",
        "description": (
            "Premium titanium design, powerful A18 Pro chip and advanced camera "
            "controls."
        ),
        "img": "https://m.media-amazon.com/images/I/61JvFLHZ6NL._AC_SX679_.jpg",
        "rate": 4.9,
        "reviews": 214,
        "price": 1099,
        "insteadOF": 1249,
        "badge": "Premium pick",
    },
    {
        "title": "Google Pixel 9 Pro 256GB — Obsidian",
        "description": (
            "Helpful Google AI, a brilliant Super Actua display and pro-level cameras."
        ),
        "img": "https://m.media-amazon.com/images/I/71lJz6Z7RUL._AC_SX679_.jpg",
        "rate": 4.7,
        "reviews": 119,
        "price": 899,
        "insteadOF": 1049,
        "badge": "AI favorite",
    },
    {
        "title": "OnePlus 13 256GB — Midnight Ocean",
        "description": (
            "Ultra-fast performance, smooth AMOLED display and rapid all-day charging."
        ),
        "img": "https://m.media-amazon.com/images/I/71d5fMDvq9L._AC_SX679_.jpg",
        "rate": 4.6,
        "reviews": 92,
        "price": 799,
        "insteadOF": 899,
        "badge": "Fast charging",
    },
    {
        "title": "Samsung Galaxy Z Flip6 256GB — Blue",
        "description": (
            "Compact foldable design with Galaxy AI and a versatile FlexWindow display."
        ),
        "img": "https://m.media-amazon.com/images/I/71-D3MZfZIL._AC_SX679_.jpg",
        "rate": 4.5,
        "reviews": 73,
        "price": 949,
        "insteadOF": 1099,
        "badge": "Foldable",
    },
    {
        "title": "Xiaomi 14T Pro 512GB — Titan Gray",
        "description": (
            "Leica-powered photography, flagship performance and lightning-fast "
            "charging."
        ),
        "img": "https://m.media-amazon.com/images/I/71NkiJbYmBL._AC_SX679_.jpg",
        "rate": 4.6,
        "reviews": 58,
        "price": 699,
        "insteadOF": 799,
        "badge": "Camera pick",
    },
    {
        "title": "Nothing Phone (2a) 256GB — Milk",
        "description": (
            "Distinctive Glyph design, smooth OLED display and clean Android "
            "experience."
        ),
        "img": "https://m.media-amazon.com/images/I/71ChLWTbPqL._AC_SX679_.jpg",
        "rate": 4.4,
        "reviews": 81,
        "price": 349,
        "insteadOF": 429,
        "badge": "Unique design",
    },
]


def seed_products() -> None:
    with Session(engine) as session:
        if session.exec(select(Product.id).limit(1)).first() is not None:
            return
        session.add_all(Product(**data) for data in PRODUCTS)
        session.commit()


def seed_admin() -> None:
    settings = get_settings()
    email = settings.admin_email.strip().lower()
    with Session(engine) as session:
        if session.exec(select(User).where(User.email == email)).first():
            return
        session.add(
            User(
                name="Administrator",
                email=email,
                password_hash=hash_password(settings.admin_password),
                role=UserRole.ADMIN,
            )
        )
        session.commit()
