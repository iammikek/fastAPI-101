"""
SQLAlchemy ORM models.
"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    """Category table: id, name, description."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    items = relationship("Item", back_populates="category")


class Item(Base):
    """Item table: id, name, description, price, category_id."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)

    category = relationship("Category", back_populates="items")
