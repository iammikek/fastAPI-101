"""Integration tests for PATCH /categories/{category_id}."""


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
