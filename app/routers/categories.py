"""Category CRUD routes."""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import verify_api_key
from app.database import get_db
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services import CategoryService

logger = logging.getLogger("app")

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List categories with pagination."""
    rows = CategoryService.list_categories(db, skip=skip, limit=limit)
    return [CategoryResponse.model_validate(row) for row in rows]


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category by id."""
    row = CategoryService.get_by_id(db, category_id)
    return CategoryResponse.model_validate(row)


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Create a new category (requires API key authentication)."""
    row = CategoryService.create(db, category)
    return CategoryResponse.model_validate(row)


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Update a category (requires API key authentication)."""
    row = CategoryService.update(db, category_id, category)
    return CategoryResponse.model_validate(row)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Delete a category when no items reference it (requires API key)."""
    CategoryService.delete(db, category_id)
    logger.info("Deleted category id=%s", category_id)
    return None
