"""
Pydantic schemas for request/response validation.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class CategoryCreate(BaseModel):
    """Schema for creating a category (request body)."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CategoryUpdate(BaseModel):
    """Schema for partial category update (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class CategoryResponse(BaseModel):
    """Schema for category responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None


class ItemCreate(BaseModel):
    """Schema for creating an item (request body)."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0, decimal_places=2)
    category_id: int | None = None


class ItemUpdate(BaseModel):
    """Schema for partial update (all fields optional)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    category_id: int | None = None


class ItemResponse(BaseModel):
    """Schema for item responses (API Resource equivalent)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: Decimal
    category_id: int | None
    category: CategoryResponse | None = None

    @field_serializer("price")
    def serialize_price(self, price: Decimal) -> float:
        return float(price)


class ItemStatsResponse(BaseModel):
    """Schema for item statistics summary."""

    total_items: int
    average_price: Decimal
    min_price: Decimal | None
    max_price: Decimal | None

    @field_serializer("average_price", "min_price", "max_price")
    def serialize_prices(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class ItemListFilters(BaseModel):
    """Optional query filters for GET /items (Laravel query scope equivalent)."""

    min_price: Decimal | None = Field(default=None, gt=0)
    max_price: Decimal | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, ge=1)
    name_contains: str | None = Field(default=None, min_length=1, max_length=255)


class ItemListResponse(BaseModel):
    """Paginated list of items (Laravel paginate() equivalent)."""

    items: list[ItemResponse]
    total: int
    skip: int
    limit: int


class CategoryListResponse(BaseModel):
    """Paginated list of categories."""

    items: list[CategoryResponse]
    total: int
    skip: int
    limit: int
