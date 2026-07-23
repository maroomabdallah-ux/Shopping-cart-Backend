# Shopping Cart API

FastAPI backend for the React shopping cart application.

## Included

- PostgreSQL database
- Nine initial products
- Alembic database migrations
- Product search and server-side pagination
- Order creation and retrieval
- CORS configuration for the Vite frontend
- Automatic OpenAPI documentation

## Run locally

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project:

```bash
pip install -e ".[dev]"
```

Create the local environment file:

```bash
cp .env.example .env
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Create the schema and insert the initial products:

```bash
alembic upgrade head
```

Start the API:

```bash
fastapi dev app/main.py
```

The API will be available at `http://127.0.0.1:8000`.

The default local database connection is:

```text
postgresql+psycopg://shopping_cart:shopping_cart@localhost:5433/shopping_cart
```

You can change it through `DATABASE_URL` in `.env`.

Do not create database tables from the React application or from FastAPI
startup. Schema changes belong in versioned Alembic migrations:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

## Useful URLs

- API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`
- Products: `http://127.0.0.1:8000/api/products?page=1&page_size=3`

## Endpoints

```text
GET  /health
GET  /api/products
GET  /api/products/{product_id}
POST /api/orders
GET  /api/orders/{order_id}
```

Product query parameters:

```text
page=1
page_size=3
search=samsung
```

Example order request:

```json
{
  "customer_name": "Ahmad",
  "phone": "0790000000",
  "address": "Amman, Jordan",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

## Tests and formatting

```bash
pytest
ruff check .
ruff format --check .
```
