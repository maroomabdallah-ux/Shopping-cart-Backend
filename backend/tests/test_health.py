from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_products_and_order_flow() -> None:
    with TestClient(app) as client:
        register_response = client.post(
            "/api/auth/register",
            json={
                "name": "Test Customer",
                "email": "customer@example.com",
                "password": "Password123!",
            },
        )
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        products_response = client.get(
            "/api/products",
            params={"page": 1, "page_size": 3},
        )

        assert products_response.status_code == 200
        products_page = products_response.json()
        assert len(products_page["items"]) == 3
        assert products_page["total"] == 9
        assert products_page["pages"] == 3

        order_response = client.post(
            "/api/orders",
            headers=headers,
            json={
                "customer_name": "Test Customer",
                "phone": "0790000000",
                "address": "Amman, Jordan",
                "items": [
                    {
                        "product_id": products_page["items"][0]["id"],
                        "quantity": 2,
                    }
                ],
            },
        )

    assert order_response.status_code == 201
    order = order_response.json()
    assert order["status"] == "pending"
    assert order["items"][0]["quantity"] == 2
    assert order["total"] == order["subtotal"] + order["delivery"]


def test_admin_permissions_and_management() -> None:
    with TestClient(app) as client:
        user_response = client.post(
            "/api/auth/register",
            json={
                "name": "Normal User",
                "email": "user@example.com",
                "password": "Password123!",
            },
        )
        user_headers = {
            "Authorization": f"Bearer {user_response.json()['access_token']}"
        }
        assert client.get("/api/admin/users", headers=user_headers).status_code == 403

        admin_response = client.post(
            "/api/auth/login",
            json={"email": "admin@shop.local", "password": "Admin123!"},
        )
        assert admin_response.status_code == 200
        admin_headers = {
            "Authorization": f"Bearer {admin_response.json()['access_token']}"
        }
        users_response = client.get("/api/admin/users", headers=admin_headers)
        assert users_response.status_code == 200
        assert len(users_response.json()) == 2

        products = client.get("/api/products").json()["items"]
        order_response = client.post(
            "/api/orders",
            headers=user_headers,
            json={
                "customer_name": "Normal User",
                "phone": "0790000000",
                "address": "Amman, Jordan",
                "items": [{"product_id": products[0]["id"], "quantity": 1}],
            },
        )
        assert order_response.status_code == 201
        order_id = order_response.json()["id"]

        my_orders_response = client.get("/api/orders", headers=user_headers)
        assert my_orders_response.status_code == 200
        assert len(my_orders_response.json()) == 1
        assert my_orders_response.json()[0]["id"] == order_id

        orders_response = client.get("/api/admin/orders", headers=admin_headers)
        assert orders_response.status_code == 200
        assert len(orders_response.json()) == 1

        status_response = client.patch(
            f"/api/admin/orders/{order_id}/status",
            headers=admin_headers,
            json={"status": "confirmed"},
        )
        assert status_response.status_code == 200
        assert status_response.json()["status"] == "confirmed"

        create_response = client.post(
            "/api/admin/products",
            headers=admin_headers,
            json={
                "title": "Test Product",
                "description": "A product created by an admin",
                "img": "https://example.com/product.jpg",
                "rate": 4.2,
                "reviews": 10,
                "price": 25,
                "insteadOF": 30,
                "badge": "Test",
            },
        )
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]

        update_response = client.patch(
            f"/api/admin/products/{product_id}",
            headers=admin_headers,
            json={"price": 20},
        )
        assert update_response.status_code == 200
        assert update_response.json()["price"] == 20

        delete_response = client.delete(
            f"/api/admin/products/{product_id}",
            headers=admin_headers,
        )
        assert delete_response.status_code == 204
