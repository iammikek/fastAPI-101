"""
SQLAlchemy ORM models.
"""
from sqlalchemy import Column, Float, Integer, String, Text

from database import Base


class Item(Base):
    """Item table: id, name, description, price."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
