"""Integration tests for root and health endpoints."""


def test_root(client):
    """GET / returns 200 and the hello message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI!"}


def test_health(client):
    """GET /health returns 200 and confirms database connectivity."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}
