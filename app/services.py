"""
Service layer: business logic separated from API routes.
"""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions import ItemNotFoundError
from app.models import Item
from app.schemas import ItemCreate, ItemUpdate


class ItemService:
    """Service class for item business logic."""

    @staticmethod
    def list_items(db: Session, skip: int, limit: int) -> list[Item]:
        """Return a paginated list of items."""
        return db.query(Item).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, item_id: int) -> Item:
        """Return an item by id or raise ItemNotFoundError."""
        row = db.get(Item, item_id)
        if row is None:
            raise ItemNotFoundError(item_id)
        return row

    @staticmethod
    def create(db: Session, item: ItemCreate) -> Item:
        """Create and persist a new item."""
        row = Item(
            name=item.name,
            description=item.description,
            price=item.price,
            category=item.category,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def update(db: Session, item_id: int, item: ItemUpdate) -> Item:
        """Partially update an item."""
        row = ItemService.get_by_id(db, item_id)
        data = item.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(row, field, value)
        db.commit()
        db.refresh(row)
        return row

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
