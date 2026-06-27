"""Integration tests for DELETE /items/{item_id} and API key auth."""


def test_delete_item_with_api_key(client, sample_item, auth_headers):
    """DELETE /items/{item_id} deletes item when API key is valid."""
    item_id = sample_item["id"]
    response = client.delete(f"/items/{item_id}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/items/{item_id}").status_code == 404


def test_delete_item_without_api_key(client, sample_item):
    """DELETE /items/{item_id} returns 401 when API key is missing."""
    response = client.delete(f"/items/{sample_item['id']}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_delete_item_invalid_api_key(client, sample_item):
    """DELETE /items/{item_id} returns 401 when API key is invalid."""
    response = client.delete(
        f"/items/{sample_item['id']}",
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_delete_item_not_found(client, auth_headers):
    """DELETE /items/{item_id} returns 404 when item does not exist."""
    response = client.delete("/items/99", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"
