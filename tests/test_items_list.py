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


def test_list_items_filter_by_min_price(client, create_item):
    """GET /items?min_price=10 returns items at or above the minimum price."""
    create_item(name="Cheap", price=5.0)
    create_item(name="Mid", price=10.0)
    create_item(name="Premium", price=25.0)
    response = client.get("/items?min_price=10")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"Mid", "Premium"}


def test_list_items_filter_by_max_price(client, create_item):
    """GET /items?max_price=10 returns items at or below the maximum price."""
    create_item(name="Cheap", price=5.0)
    create_item(name="Mid", price=10.0)
    create_item(name="Premium", price=25.0)
    response = client.get("/items?max_price=10")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"Cheap", "Mid"}


def test_list_items_filter_by_category(client, create_category, create_item):
    """GET /items?category_id= returns items in that category."""
    tools = create_category(name="Tools")
    books = create_category(name="Books")
    create_item(name="Hammer", price=10.0, category_id=tools["id"])
    create_item(name="Novel", price=12.0, category_id=books["id"])
    create_item(name="Wrench", price=15.0, category_id=tools["id"])
    response = client.get(f"/items?category_id={tools['id']}")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"Hammer", "Wrench"}


def test_list_items_filter_by_name_contains(client, create_item):
    """GET /items?name_contains=widget returns case-insensitive name matches."""
    create_item(name="Blue Widget", price=10.0)
    create_item(name="Red Gadget", price=12.0)
    create_item(name="green widget", price=15.0)
    response = client.get("/items?name_contains=widget")
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert names == {"Blue Widget", "green widget"}


def test_list_items_combined_filters(client, create_category, create_item):
    """GET /items supports combining multiple filters."""
    tools = create_category(name="Tools")
    books = create_category(name="Books")
    create_item(name="Budget Tool", price=8.0, category_id=tools["id"])
    create_item(name="Pro Tool", price=20.0, category_id=tools["id"])
    create_item(name="Budget Book", price=8.0, category_id=books["id"])
    response = client.get(
        f"/items?category_id={tools['id']}&min_price=10&max_price=25"
    )
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Pro Tool"


@pytest.mark.parametrize("query", ["limit=101", "skip=-1", "min_price=-1"])
def test_list_items_validation_errors(client, query):
    """GET /items returns 422 for invalid query params."""
    response = client.get(f"/items?{query}")
    assert response.status_code == 422
