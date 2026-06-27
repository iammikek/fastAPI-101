"""
Service layer: business logic separated from API routes.
"""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.exceptions import (
    CategoryInUseError,
    CategoryNameExistsError,
    CategoryNotFoundError,
    ItemNotFoundError,
)
from app.models import Category, Item
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ItemCreate,
    ItemListFilters,
    ItemUpdate,
)


class CategoryService:
    """Service class for category business logic."""

    @staticmethod
    def list_categories(db: Session, skip: int, limit: int) -> tuple[list[Category], int]:
        """Return a paginated list of categories and total count."""
        query = db.query(Category)
        total = query.count()
        rows = query.offset(skip).limit(limit).all()
        return rows, total

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Category:
        """Return a category by id or raise CategoryNotFoundError."""
        row = db.get(Category, category_id)
        if row is None:
            raise CategoryNotFoundError(category_id)
        return row

    @staticmethod
    def _ensure_unique_name(db: Session, name: str, category_id: int | None = None) -> None:
        """Raise CategoryNameExistsError when another category already uses the name."""
        query = db.query(Category).filter(Category.name == name)
        if category_id is not None:
            query = query.filter(Category.id != category_id)
        if query.first() is not None:
            raise CategoryNameExistsError(name)

    @staticmethod
    def create(db: Session, category: CategoryCreate) -> Category:
        """Create and persist a new category."""
        CategoryService._ensure_unique_name(db, category.name)
        row = Category(name=category.name, description=category.description)
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def update(db: Session, category_id: int, category: CategoryUpdate) -> Category:
        """Partially update a category."""
        row = CategoryService.get_by_id(db, category_id)
        data = category.model_dump(exclude_unset=True)
        if "name" in data:
            CategoryService._ensure_unique_name(db, data["name"], category_id=category_id)
        for field, value in data.items():
            setattr(row, field, value)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def delete(db: Session, category_id: int) -> None:
        """Delete a category by id when no items reference it."""
        row = CategoryService.get_by_id(db, category_id)
        item_count = db.query(func.count(Item.id)).filter(Item.category_id == category_id).scalar()
        if item_count:
            raise CategoryInUseError(category_id)
        db.delete(row)
        db.commit()


class ItemService:
    """Service class for item business logic."""

    @staticmethod
    def _validate_category_id(db: Session, category_id: int | None) -> None:
        """Ensure category_id exists when provided."""
        if category_id is not None:
            CategoryService.get_by_id(db, category_id)

    @staticmethod
    def _items_query(db: Session, filters: ItemListFilters | None = None):
        """Build a filtered item query (without pagination)."""
        query = db.query(Item)
        if filters is not None:
            if filters.min_price is not None:
                query = query.filter(Item.price >= filters.min_price)
            if filters.max_price is not None:
                query = query.filter(Item.price <= filters.max_price)
            if filters.category_id is not None:
                query = query.filter(Item.category_id == filters.category_id)
            if filters.name_contains is not None:
                query = query.filter(Item.name.ilike(f"%{filters.name_contains}%"))
        return query

    @staticmethod
    def list_items(
        db: Session,
        skip: int,
        limit: int,
        filters: ItemListFilters | None = None,
    ) -> tuple[list[Item], int]:
        """Return a paginated, optionally filtered list of items and total count."""
        query = ItemService._items_query(db, filters)
        total = query.count()
        rows = query.options(joinedload(Item.category)).offset(skip).limit(limit).all()
        return rows, total

    @staticmethod
    def get_by_id(db: Session, item_id: int) -> Item:
        """Return an item by id or raise ItemNotFoundError."""
        row = db.query(Item).options(joinedload(Item.category)).filter(Item.id == item_id).first()
        if row is None:
            raise ItemNotFoundError(item_id)
        return row

    @staticmethod
    def create(db: Session, item: ItemCreate) -> Item:
        """Create and persist a new item."""
        ItemService._validate_category_id(db, item.category_id)
        row = Item(
            name=item.name,
            description=item.description,
            price=item.price,
            category_id=item.category_id,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return ItemService.get_by_id(db, row.id)

    @staticmethod
    def update(db: Session, item_id: int, item: ItemUpdate) -> Item:
        """Partially update an item."""
        row = ItemService.get_by_id(db, item_id)
        data = item.model_dump(exclude_unset=True)
        if "category_id" in data:
            ItemService._validate_category_id(db, data["category_id"])
        for field, value in data.items():
            setattr(row, field, value)
        db.commit()
        db.refresh(row)
        return ItemService.get_by_id(db, item_id)

    @staticmethod
    def delete(db: Session, item_id: int) -> None:
        """Delete an item by id."""
        row = ItemService.get_by_id(db, item_id)
        db.delete(row)
        db.commit()

    @staticmethod
    def get_stats(db: Session) -> dict:
        """Calculate statistics about items."""
        count = db.query(func.count(Item.id)).scalar()
        if count == 0:
            return {
                "total_items": 0,
                "average_price": Decimal("0.00"),
                "min_price": None,
                "max_price": None,
            }

        avg_price = db.query(func.avg(Item.price)).scalar()
        min_price = db.query(func.min(Item.price)).scalar()
        max_price = db.query(func.max(Item.price)).scalar()

        return {
            "total_items": count,
            "average_price": Decimal(str(round(float(avg_price), 2))),
            "min_price": Decimal(str(min_price)),
            "max_price": Decimal(str(max_price)),
        }

    @staticmethod
    def check_database(db: Session) -> None:
        """Verify database connectivity; raises on failure."""
        db.execute(select(1))
