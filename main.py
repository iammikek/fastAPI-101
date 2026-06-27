"""
FastAPI learning project - minimal app to get started.
Run with: uvicorn main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from auth import verify_api_key
from database import Base, engine, get_db
from models import Item
from schemas import ItemCreate, ItemResponse, ItemStatsResponse, ItemUpdate
from services import ItemService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on application startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="First FastAPI",
    description="A simple API to learn FastAPI basics",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    """Root endpoint - says hello."""
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health():
    """Health check for Docker/load balancers."""
    return {"status": "ok"}


@app.get("/items", response_model=list[ItemResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List items with optional pagination (query params: skip, limit)."""
    rows = db.query(Item).offset(skip).limit(limit).all()
    return [ItemResponse.model_validate(r) for r in rows]


@app.get("/items/stats/summary", response_model=ItemStatsResponse)
def get_items_stats(db: Session = Depends(get_db)):
    """Get statistics about items (uses service layer)."""
    return ItemService.get_stats(db)


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by id (path parameter)."""
    row = db.get(Item, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse.model_validate(row)


@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item (request body validated by Pydantic)."""
    row = Item(
        name=item.name,
        description=item.description,
        price=item.price,
        category=item.category,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ItemResponse.model_validate(row)


@app.patch("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an item (partial: only provided fields are updated)."""
    row = db.get(Item, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    data = item.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return ItemResponse.model_validate(row)


@app.delete("/items/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    """Delete an item (requires API key authentication)."""
    row = db.get(Item, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(row)
    db.commit()
    return None
