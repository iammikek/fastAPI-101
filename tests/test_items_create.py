"""Integration tests for POST /items."""


def test_create_item(client, auth_headers):
    """POST /items creates an item and returns 201 with the created item."""
    response = client.post(
        "/items",
        headers=auth_headers,
        json={"name": "Widget", "description": "A nice widget", "price": 9.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] >= 1
    assert data["name"] == "Widget"
    assert data["description"] == "A nice widget"
    assert data["price"] == 9.99


def test_create_item_optional_description(client, auth_headers):
    """POST /items accepts missing description (optional field)."""
    response = client.post(
        "/items",
        headers=auth_headers,
        json={"name": "Thing", "price": 5.0},
    )
    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_item_with_category(client, auth_headers):
    """POST /items accepts category field."""
    response = client.post(
        "/items",
        headers=auth_headers,
        json={"name": "Gadget", "price": 15.0, "category": "Electronics"},
    )
    assert response.status_code == 201
    assert response.json()["category"] == "Electronics"


def test_create_item_without_api_key(client):
    """POST /items returns 401 when API key is missing."""
    response = client.post("/items", json={"name": "Thing", "price": 5.0})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"
