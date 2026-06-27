"""
Pytest fixtures shared across tests.
DATABASE_URL is set to in-memory SQLite in the project root conftest.py.
"""
# DATABASE_URL set in project root conftest.py before any test module loads

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient

from config import get_settings
from database import Base, SessionLocal, engine
from main import app
from models import Item


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create tables for tests (mirrors app lifespan startup)."""
    Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def reset_db():
    """Clear items between tests so each test starts with an empty table."""
    yield
    db = SessionLocal()
    try:
        db.query(Item).delete()
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    """HTTP client with app lifespan enabled."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers():
    """Valid API key headers for protected endpoints."""
    return {"X-API-Key": get_settings().api_key}


@pytest.fixture
def create_item(client) -> Callable[..., dict[str, Any]]:
    """Factory for creating items via the API (Laravel factory equivalent)."""

    def _create_item(**overrides: Any) -> dict[str, Any]:
        payload = {"name": "Widget", "price": 9.99, **overrides}
        response = client.post("/items", json=payload)
        assert response.status_code == 201
        return response.json()

    return _create_item


@pytest.fixture
def sample_item(create_item) -> dict[str, Any]:
    """A single item created via POST /items."""
    return create_item()


@pytest.fixture
def db():
    """Database session for service-layer unit tests."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
