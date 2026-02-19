"""
Pytest fixtures shared across tests.
"""
import pytest

from main import items_db


@pytest.fixture(autouse=True)
def reset_items_db():
    """Clear the in-memory items list before each test so tests don't affect each other."""
    items_db.clear()
    yield
    items_db.clear()
