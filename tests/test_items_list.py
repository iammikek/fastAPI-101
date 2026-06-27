"""Integration tests for GET /items."""

import pytest


def test_list_items_empty(client):
    """GET /items returns empty list when no items exist."""
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items_with_pagination(client, create_item):
    """GET /items?skip=0&limit=2 returns only the requested slice."""
    for name, price in [("A", 1.0), ("B", 2.0), ("C", 3.0)]:
        create_item(name=name, price=price, description=None)
    response = client.get("/items?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "B"
    assert data[1]["name"] == "C"


@pytest.mark.parametrize("query", ["limit=101", "skip=-1"])
def test_list_items_validation_errors(client, query):
    """GET /items returns 422 for invalid pagination params."""
    response = client.get(f"/items?{query}")
    assert response.status_code == 422
