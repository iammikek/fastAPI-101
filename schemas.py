"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel


class ItemCreate(BaseModel):
    """Schema for creating an item (request body)."""
    name: str
    description: str | None = None
    price: float
    category: str | None = None


class ItemUpdate(BaseModel):
    """Schema for partial update (all fields optional)."""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
