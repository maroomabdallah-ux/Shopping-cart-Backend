from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.features.admin.router import router as admin_router
from app.features.orders.router import router as orders_router
from app.features.payments.router import router as payments_router
from app.features.products.router import router as products_router
from app.features.users.router import router as users_router

settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router, prefix=settings.api_prefix)
app.include_router(orders_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(admin_router, prefix=settings.api_prefix)
app.include_router(payments_router, prefix=settings.api_prefix)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
