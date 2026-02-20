"""
Database connection and session management.
Uses SQLite by default; set DATABASE_URL for a different backend.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
# SQLite needs check_same_thread=False for FastAPI's async usage
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that yields a DB session; close after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
