"""
FastAPI learning project - minimal app to get started.
Run with: uvicorn main:app --reload
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="First FastAPI",
    description="A simple API to learn FastAPI basics",
    version="0.1.0",
)

# In-memory store for items (resets when the app restarts)
items_db: list[dict] = []


class ItemCreate(BaseModel):
    """Schema for creating an item (request body)."""
    name: str
    description: str | None = None
    price: float


@app.get("/")
def root():
    """Root endpoint - says hello."""
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health():
    """Health check for Docker/load balancers."""
    return {"status": "ok"}


@app.get("/items", response_model=list[dict])
def list_items(skip: int = 0, limit: int = 10):
    """List items with optional pagination (query params: skip, limit)."""
    return items_db[skip : skip + limit]


@app.get("/items/{item_id}", response_model=dict)
def get_item(item_id: int):
    """Get a single item by id (path parameter)."""
    if item_id < 0 or item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.post("/items", response_model=dict, status_code=201)
def create_item(item: ItemCreate):
    """Create a new item (request body validated by Pydantic)."""
    new_item = {
        "id": len(items_db),
        "name": item.name,
        "description": item.description,
        "price": item.price,
    }
    items_db.append(new_item)
    return new_item
