"""Integration tests for GET /categories."""


def test_list_categories_empty(client):
    """GET /categories returns empty paginated result when no categories exist."""
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "skip": 0, "limit": 10}


def test_list_categories_with_pagination(client, create_category):
    """GET /categories?skip=0&limit=2 returns pagination metadata."""
    for name in ["A", "B", "C"]:
        create_category(name=name)
    response = client.get("/categories?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert data["skip"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "B"
    assert data["items"][1]["name"] == "C"


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
