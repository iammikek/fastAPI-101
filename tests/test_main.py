"""
Tests for the FastAPI app using TestClient.
Run with: pytest tests/ -v
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    """GET / returns 200 and the hello message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI!"}


def test_health():
    """GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_items_empty():
    """GET /items returns empty list when no items exist."""
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items_with_pagination():
    """GET /items?skip=0&limit=2 returns only the requested slice."""
    for name, price in [("A", 1.0), ("B", 2.0), ("C", 3.0)]:
        client.post("/items", json={"name": name, "description": None, "price": price})
    response = client.get("/items?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "B"
    assert data[1]["name"] == "C"


def test_create_item():
    """POST /items creates an item and returns 201 with the created item."""
    response = client.post(
        "/items",
        json={"name": "Widget", "description": "A nice widget", "price": 9.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] >= 1  # SQLite autoincrement starts at 1
    assert data["name"] == "Widget"
    assert data["description"] == "A nice widget"
    assert data["price"] == 9.99


def test_create_item_optional_description():
    """POST /items accepts missing description (optional field)."""
    response = client.post("/items", json={"name": "Thing", "price": 5.0})
    assert response.status_code == 201
    assert response.json()["description"] is None


def test_get_item():
    """GET /items/{item_id} returns the item when it exists."""
    create = client.post("/items", json={"name": "Widget", "description": None, "price": 9.99})
    item_id = create.json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_get_item_not_found():
    """GET /items/{item_id} returns 404 when item does not exist."""
    response = client.get("/items/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_item_invalid_body():
    """POST /items returns 422 when required fields are missing."""
    response = client.post("/items", json={"name": "No price"})
    assert response.status_code == 422


def test_update_item_partial():
    """PATCH /items/{item_id} updates only provided fields."""
    create = client.post(
        "/items", json={"name": "Widget", "description": "Original", "price": 10.0}
    )
    item_id = create.json()["id"]
    response = client.patch(f"/items/{item_id}", json={"price": 5.99})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Widget"
    assert data["description"] == "Original"
    assert data["price"] == 5.99


def test_update_item_full():
    """PATCH /items/{item_id} can update all fields."""
    create = client.post("/items", json={"name": "Old", "description": None, "price": 1.0})
    item_id = create.json()["id"]
    response = client.patch(
        f"/items/{item_id}",
        json={"name": "New", "description": "Updated", "price": 2.5},
    )
    assert response.status_code == 200
    assert response.json() == {"id": item_id, "name": "New", "description": "Updated", "price": 2.5}


def test_update_item_not_found():
    """PATCH /items/{item_id} returns 404 when item does not exist."""
    response = client.patch("/items/99", json={"name": "Nope"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
