"""
Service layer: business logic separated from API routes.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Item


class ItemService:
    """Service class for item business logic."""

    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        Calculate statistics about items.
        Returns a dict with count, average price, min price, max price.
        """
        count = db.query(func.count(Item.id)).scalar()
        if count == 0:
            return {
                "total_items": 0,
                "average_price": 0.0,
                "min_price": None,
                "max_price": None,
            }

        avg_price = db.query(func.avg(Item.price)).scalar()
        min_price = db.query(func.min(Item.price)).scalar()
        max_price = db.query(func.max(Item.price)).scalar()

        return {
            "total_items": count,
            "average_price": round(float(avg_price), 2),
            "min_price": float(min_price),
            "max_price": float(max_price),
        }
