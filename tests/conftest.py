"""
Pytest fixtures shared across tests.
DATABASE_URL is set to in-memory SQLite in the project root conftest.py.
"""
# DATABASE_URL set in project root conftest.py before any test module loads

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient

from alembic import command
from alembic.config import Config
from app.config import get_settings
from app.database import SessionLocal
from app.models import Category, Item
from main import app


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    """Apply Alembic migrations (mirrors production database setup)."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
def reset_db():
    """Clear items and categories between tests."""
    yield
    db = SessionLocal()
    try:
        db.query(Item).delete()
        db.query(Category).delete()
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
def create_category(client, auth_headers) -> Callable[..., dict[str, Any]]:
    """Factory for creating categories via the API."""

    def _create_category(**overrides: Any) -> dict[str, Any]:
        payload = {"name": "Tools", **overrides}
        response = client.post("/categories", json=payload, headers=auth_headers)
        assert response.status_code == 201
        return response.json()

    return _create_category


@pytest.fixture
def create_item(client, auth_headers) -> Callable[..., dict[str, Any]]:
    """Factory for creating items via the API (Laravel factory equivalent)."""

    def _create_item(**overrides: Any) -> dict[str, Any]:
        payload = {"name": "Widget", "price": 9.99, **overrides}
        response = client.post("/items", json=payload, headers=auth_headers)
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
