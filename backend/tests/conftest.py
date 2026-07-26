import os

os.environ["DATABASE_URL"] = "sqlite:///./test_shopping_cart.db"

import pytest
from sqlmodel import SQLModel

from app.db.session import engine
from app.seed import seed_admin, seed_products


@pytest.fixture(autouse=True)
def database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    seed_products()
    seed_admin()
    yield
    SQLModel.metadata.drop_all(engine)
