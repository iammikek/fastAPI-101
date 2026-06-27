"""
Pytest fixtures shared across tests.
DATABASE_URL is set to in-memory SQLite in the project root conftest.py.
"""
# DATABASE_URL set in project root conftest.py before any test module loads

import pytest

from database import Base, SessionLocal, engine
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
