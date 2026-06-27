"""Integration tests for DELETE /categories/{category_id}."""


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
