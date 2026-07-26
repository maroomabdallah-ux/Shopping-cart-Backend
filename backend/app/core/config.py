from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Shopping Cart API"
    api_prefix: str = "/api"
    database_url: str = (
        "postgresql+psycopg://shopping_cart:shopping_cart@localhost:5433/shopping_cart"
    )
    frontend_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    secret_key: str = "change-this-secret-key-in-production"
    access_token_expire_minutes: int = 60
    admin_email: str = "admin@shop.local"
    admin_password: str = "Admin123!"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_url: str = "http://localhost:5173"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Shopping Cart"
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.frontend_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
