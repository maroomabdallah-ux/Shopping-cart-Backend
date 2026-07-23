from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_products_and_order_flow() -> None:
    with TestClient(app) as client:
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
