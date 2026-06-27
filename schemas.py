"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    """Schema for creating an item (request body)."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: float = Field(gt=0)
    category: str | None = Field(default=None, max_length=100)


class ItemUpdate(BaseModel):
    """Schema for partial update (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, max_length=100)


class ItemResponse(BaseModel):
    """Schema for item responses (API Resource equivalent)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: float
    category: str | None


class ItemStatsResponse(BaseModel):
    """Schema for item statistics summary."""

    total_items: int
    average_price: float
    min_price: float | None
    max_price: float | None
