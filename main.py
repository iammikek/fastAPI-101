"""
FastAPI learning project - minimal app to get started.
Run with: uvicorn main:app --reload
"""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import verify_api_key
from database import Base, engine, get_db
from models import Item

# Create tables on startup (SQLite file is created here if missing)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="First FastAPI",
    description="A simple API to learn FastAPI basics",
    version="0.1.0",
)


class ItemCreate(BaseModel):
    """Schema for creating an item (request body)."""
    name: str
    description: str | None = None
    price: float


class ItemUpdate(BaseModel):
    """Schema for partial update (all fields optional)."""
    name: str | None = None
    description: str | None = None
    price: float | None = None


def item_to_dict(row: Item) -> dict:
    """Convert Item ORM row to JSON-serializable dict."""
    return {"id": row.id, "name": row.name, "description": row.description, "price": row.price}


@app.get("/")
def root():
    """Root endpoint - says hello."""
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health():
    """Health check for Docker/load balancers."""
    return {"status": "ok"}


@app.get("/items", response_model=list[dict])
def list_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List items with optional pagination (query params: skip, limit)."""
    rows = db.query(Item).offset(skip).limit(limit).all()
    return [item_to_dict(r) for r in rows]


@app.get("/items/{item_id}", response_model=dict)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by id (path parameter)."""
    row = db.get(Item, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_to_dict(row)


@app.post("/items", response_model=dict, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item (request body validated by Pydantic)."""
    row = Item(name=item.name, description=item.description, price=item.price)
    db.add(row)
    db.commit()
    db.refresh(row)
    return item_to_dict(row)


@app.patch("/items/{item_id}", response_model=dict)
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
    return item_to_dict(row)


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
