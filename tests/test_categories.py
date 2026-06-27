"""Integration tests for category CRUD endpoints."""


def test_list_categories_empty(client):
    """GET /categories returns empty list when no categories exist."""
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == []


def test_create_category(client, auth_headers):
    """POST /categories creates a category and returns 201."""
    response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "Tools", "description": "Hand tools"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] >= 1
    assert data["name"] == "Tools"
    assert data["description"] == "Hand tools"


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


def test_update_category(client, create_category, auth_headers):
    """PATCH /categories/{id} updates category fields."""
    category = create_category(name="Old Name")
    response = client.patch(
        f"/categories/{category['id']}",
        headers=auth_headers,
        json={"name": "New Name", "description": "Updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["description"] == "Updated"


def test_delete_category(client, create_category, auth_headers):
    """DELETE /categories/{id} removes an unused category."""
    category = create_category(name="Temporary")
    response = client.delete(f"/categories/{category['id']}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/categories/{category['id']}").status_code == 404


def test_delete_category_in_use(client, create_category, create_item, auth_headers):
    """DELETE /categories/{id} returns 409 when items reference the category."""
    category = create_category(name="Tools")
    create_item(name="Hammer", price=10.0, category_id=category["id"])
    response = client.delete(f"/categories/{category['id']}", headers=auth_headers)
    assert response.status_code == 409
    assert response.json()["code"] == "CATEGORY_IN_USE"


def test_create_category_without_api_key(client):
    """POST /categories returns 401 when API key is missing."""
    response = client.post("/categories", json={"name": "Tools"})
    assert response.status_code == 401


def test_create_category_duplicate_name(client, create_category, auth_headers):
    """POST /categories returns 409 when the name is already taken."""
    create_category(name="foo")
    response = client.post(
        "/categories",
        headers=auth_headers,
        json={"name": "foo", "description": "duplicate"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "CATEGORY_NAME_EXISTS"
