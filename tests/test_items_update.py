"""Integration tests for PATCH /items/{item_id}."""


def test_update_item_category(client, sample_item, auth_headers, create_category):
    """PATCH /items/{item_id} can update category_id."""
    category = create_category(name="Tools")
    item_id = sample_item["id"]
    response = client.patch(
        f"/items/{item_id}",
        headers=auth_headers,
        json={"category_id": category["id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == category["id"]
    assert data["category"]["name"] == "Tools"


def test_update_item_partial(client, create_item, auth_headers):
    """PATCH /items/{item_id} updates only provided fields."""
    item = create_item(name="Widget", description="Original", price=10.0)
    response = client.patch(
        f"/items/{item['id']}",
        headers=auth_headers,
        json={"price": 5.99},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Widget"
    assert data["description"] == "Original"
    assert data["price"] == 5.99


def test_update_item_full(client, create_item, auth_headers):
    """PATCH /items/{item_id} can update all fields."""
    item = create_item(name="Old", description=None, price=1.0)
    response = client.patch(
        f"/items/{item['id']}",
        headers=auth_headers,
        json={"name": "New", "description": "Updated", "price": 2.5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item["id"]
    assert data["name"] == "New"
    assert data["description"] == "Updated"
    assert data["price"] == 2.5
    assert "category_id" in data


def test_update_item_not_found(client, auth_headers):
    """PATCH /items/{item_id} returns 404 when item does not exist."""
    response = client.patch("/items/99", headers=auth_headers, json={"name": "Nope"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_without_api_key(client, sample_item):
    """PATCH /items/{item_id} returns 401 when API key is missing."""
    response = client.patch(f"/items/{sample_item['id']}", json={"name": "Nope"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"
