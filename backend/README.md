# Shopping Cart API

FastAPI backend for the React shopping cart application.

## Included

- PostgreSQL database
- Nine initial products
- Alembic database migrations
- Product search and server-side pagination
- Order creation and retrieval
- JWT login and registration with `admin` and `user` roles
- Admin product CRUD, user listing, and order status management
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

The migration also creates the initial administrator using `ADMIN_EMAIL` and
`ADMIN_PASSWORD` from `.env`. Change both credentials and `SECRET_KEY` before
deploying.

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
GET  /api/orders
GET  /api/orders/{order_id}
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
GET  /api/admin/products
POST /api/admin/products
PATCH /api/admin/products/{product_id}
DELETE /api/admin/products/{product_id}
GET  /api/admin/users
GET  /api/admin/orders
PATCH /api/admin/orders/{order_id}/status
```

Send the JWT returned by login or registration as:

```text
Authorization: Bearer <access_token>
```

Admin order statuses are `pending`, `confirmed`, `processing`, `shipped`,
`delivered`, and `cancelled`.

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

## Activate the Python Virtual Environment

```bash
source /Users/apple/shoppingCartBackend/.venv/bin/activate
```

---

## Connect to the PostgreSQL Database (Docker)

```bash
docker exec -it shopping-cart-postgres psql -U shopping_cart -d shopping_cart
```

---

## List All Tables

```sql
\dt
```

Expected output:

```text
                List of relations
 Schema |      Name       | Type  |     Owner
--------+-----------------+-------+---------------
 public | alembic_version | table | shopping_cart
 public | order           | table | shopping_cart
 public | orderitem       | table | shopping_cart
 public | product         | table | shopping_cart
 public | user            | table | shopping_cart
```

---

## View All Products

```sql
SELECT * FROM product;
```

---

## View All Users

```sql
SELECT * FROM "user";
```

---

## View All Orders

```sql
SELECT * FROM "order";
```

---

## View All Order Items

```sql
SELECT * FROM orderitem;
```

---

## Exit PostgreSQL

```sql
\q
```
