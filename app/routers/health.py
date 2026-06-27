"""Root and health check routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import ItemService

router = APIRouter(tags=["health"])


@router.get("/")
def root():
    """Root endpoint - says hello."""
    return {"message": "Hello from FastAPI!"}


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """Health check for Docker/load balancers; verifies database connectivity."""
    try:
        ItemService.check_database(db)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "connected"}
