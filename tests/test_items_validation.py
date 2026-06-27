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
def test_create_item_validation_errors(client, payload):
    """POST /items returns 422 for invalid payloads."""
    response = client.post("/items", json=payload)
    assert response.status_code == 422
