"""Item CRUD and statistics routes."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import verify_api_key
from app.database import get_db
from app.schemas import ItemCreate, ItemResponse, ItemStatsResponse, ItemUpdate
from app.services import ItemService

logger = logging.getLogger("app")

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List items with optional pagination (query params: skip, limit)."""
    rows = ItemService.list_items(db, skip=skip, limit=limit)
    return [ItemResponse.model_validate(row) for row in rows]


@router.get("/stats/summary", response_model=ItemStatsResponse)
def get_items_stats(db: Session = Depends(get_db)):
    """Get statistics about items (uses service layer)."""
    return ItemService.get_stats(db)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by id (path parameter)."""
    row = ItemService.get_by_id(db, item_id)
    return ItemResponse.model_validate(row)


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Create a new item (requires API key authentication)."""
    row = ItemService.create(db, item)
    return ItemResponse.model_validate(row)


@router.patch("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item: ItemUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Update an item (requires API key authentication)."""
    row = ItemService.update(db, item_id, item)
    return ItemResponse.model_validate(row)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Delete an item (requires API key authentication)."""
    ItemService.delete(db, item_id)
    logger.info("Deleted item id=%s", item_id)
    return None
