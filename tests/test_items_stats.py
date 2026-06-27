"""Integration tests for GET /items/stats/summary."""


def test_get_items_stats_empty(client):
    """GET /items/stats/summary returns stats for empty database."""
    response = client.get("/items/stats/summary")
    assert response.status_code == 200
    assert response.json() == {
        "total_items": 0,
        "average_price": 0.0,
        "min_price": None,
        "max_price": None,
    }


def test_get_items_stats(client, create_item):
    """GET /items/stats/summary returns statistics about items."""
    create_item(name="A", price=10.0)
    create_item(name="B", price=20.0)
    create_item(name="C", price=30.0)
    response = client.get("/items/stats/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 3
    assert data["average_price"] == 20.0
    assert data["min_price"] == 10.0
    assert data["max_price"] == 30.0
