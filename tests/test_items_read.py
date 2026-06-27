"""Integration tests for GET /items/{item_id}."""


def test_get_item(client, sample_item):
    """GET /items/{item_id} returns the item when it exists."""
    response = client.get(f"/items/{sample_item['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_get_item_not_found(client):
    """GET /items/{item_id} returns 404 when item does not exist."""
    response = client.get("/items/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
