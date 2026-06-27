"""Unit tests for ItemService (no HTTP layer)."""

from decimal import Decimal

import pytest

from app.exceptions import ItemNotFoundError
from app.schemas import CategoryCreate, ItemCreate, ItemListFilters, ItemUpdate
from app.services import CategoryService, ItemService


def test_get_by_id_returns_item(db, create_item):
    """get_by_id returns the item when it exists."""
    created = create_item(name="Gadget", price=12.50)
    item = ItemService.get_by_id(db, created["id"])
    assert item.name == "Gadget"
    assert float(item.price) == 12.50


def test_get_by_id_raises_when_missing(db):
    """get_by_id raises ItemNotFoundError for unknown ids."""
    with pytest.raises(ItemNotFoundError) as exc_info:
        ItemService.get_by_id(db, 999)
    assert exc_info.value.item_id == 999


def test_create_persists_item(db):
    """create adds an item to the database."""
    category = CategoryService.create(db, CategoryCreate(name="Tools"))
    item = ItemService.create(
        db,
        ItemCreate(name="New Item", price=Decimal("19.99"), category_id=category.id),
    )
    assert item.id is not None
    assert item.name == "New Item"
    assert item.category_id == category.id
    assert ItemService.get_by_id(db, item.id).name == "New Item"


def test_delete_removes_item(db, sample_item):
    """delete removes the item from the database."""
    item_id = sample_item["id"]
    ItemService.delete(db, item_id)
    with pytest.raises(ItemNotFoundError):
        ItemService.get_by_id(db, item_id)


def test_get_stats_empty(db):
    """get_stats returns zeros when no items exist."""
    stats = ItemService.get_stats(db)
    assert stats == {
        "total_items": 0,
        "average_price": Decimal("0.00"),
        "min_price": None,
        "max_price": None,
    }


def test_update_partial(db, sample_item):
    """update changes only provided fields."""
    updated = ItemService.update(
        db,
        sample_item["id"],
        ItemUpdate(price=Decimal("5.50")),
    )
    assert updated.name == "Widget"
    assert float(updated.price) == 5.50


def test_list_items_filters_by_category(db):
    """list_items applies category_id filter in the service layer."""
    tools = CategoryService.create(db, CategoryCreate(name="Tools"))
    CategoryService.create(db, CategoryCreate(name="Books"))
    ItemService.create(db, ItemCreate(name="A", price=Decimal("10.00"), category_id=tools.id))
    ItemService.create(db, ItemCreate(name="B", price=Decimal("12.00")))
    filters = ItemListFilters(category_id=tools.id)
    items = ItemService.list_items(db, skip=0, limit=10, filters=filters)
    assert [item.name for item in items] == ["A"]
