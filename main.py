"""
FastAPI learning project - minimal app to get started.
Run with: uvicorn main:app --reload
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from auth import verify_api_key
from config import get_settings
from database import Base, engine, get_db
from exceptions import ItemNotFoundError
from schemas import ItemCreate, ItemResponse, ItemStatsResponse, ItemUpdate
from services import ItemService

logger = logging.getLogger("app")


def configure_logging() -> None:
    """Configure application logging from settings."""
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on application startup."""
    configure_logging()
    logger.info("Starting application")
    Base.metadata.create_all(bind=engine)
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title="First FastAPI",
    description="A simple API to learn FastAPI basics",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log each request with method, path, status, and duration."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    log = logger.warning if response.status_code >= 400 else logger.info
    log(
        "%s %s %s %.1fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    """Return consistent 404 for missing items."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Item not found", "code": "ITEM_NOT_FOUND"},
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    """Return consistent 500 for database errors."""
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error", "code": "DB_ERROR"},
    )


@app.get("/")
def root():
    """Root endpoint - says hello."""
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Health check for Docker/load balancers; verifies database connectivity."""
    try:
        ItemService.check_database(db)
    except SQLAlchemyError as exc:
        logger.error("Health check failed: database unavailable")
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok", "database": "connected"}


@app.get("/items", response_model=list[ItemResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List items with optional pagination (query params: skip, limit)."""
    rows = ItemService.list_items(db, skip=skip, limit=limit)
    return [ItemResponse.model_validate(r) for r in rows]


@app.get("/items/stats/summary", response_model=ItemStatsResponse)
def get_items_stats(db: Session = Depends(get_db)):
    """Get statistics about items (uses service layer)."""
    return ItemService.get_stats(db)


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by id (path parameter)."""
    row = ItemService.get_by_id(db, item_id)
    return ItemResponse.model_validate(row)


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item (request body validated by Pydantic)."""
    row = ItemService.create(db, item)
    return ItemResponse.model_validate(row)


@app.patch("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an item (partial: only provided fields are updated)."""
    row = ItemService.update(db, item_id, item)
    return ItemResponse.model_validate(row)


@app.delete("/items/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Delete an item (requires API key authentication)."""
    ItemService.delete(db, item_id)
    logger.info("Deleted item id=%s", item_id)
    return None
