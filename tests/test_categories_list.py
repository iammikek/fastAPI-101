"""Integration tests for GET /categories."""


def test_list_categories_empty(client):
    """GET /categories returns empty list when no categories exist."""
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_get_category(client, create_category):
    """GET /categories/{id} returns a single category."""
    category = create_category(name="Books")
    response = client.get(f"/categories/{category['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Books"


def test_get_category_not_found(client):
    """GET /categories/{id} returns 404 for unknown ids."""
    response = client.get("/categories/999")
    assert response.status_code == 404
    assert response.json()["code"] == "CATEGORY_NOT_FOUND"
