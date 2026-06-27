"""
SQLAlchemy ORM models.
"""

from sqlalchemy import Column, Integer, Numeric, String, Text

from database import Base


class Item(Base):
    """Item table: id, name, description, price, category."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100), nullable=True)
