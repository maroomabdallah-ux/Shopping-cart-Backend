"""User persistence model and roles."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str
    role: UserRole = Field(
        default=UserRole.USER,
        sa_column=Column(
            Enum(
                UserRole,
                values_callable=lambda roles: [role.value for role in roles],
                native_enum=False,
                length=20,
            ),
            nullable=False,
            default=UserRole.USER,
        ),
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
