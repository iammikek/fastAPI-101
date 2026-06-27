"""Integration tests for POST /categories."""


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
