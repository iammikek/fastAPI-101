"""Integration tests for request validation (422 responses)."""

import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "No price"},
        {"name": "Bad", "price": -1.0},
        {"name": "", "price": 1.0},
    ],
)
def test_create_item_validation_errors(client, auth_headers, payload):
    """POST /items returns 422 for invalid payloads."""
    response = client.post("/items", json=payload, headers=auth_headers)
    assert response.status_code == 422
