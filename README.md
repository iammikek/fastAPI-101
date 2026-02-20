# Getting Fast at FastAPI

A step-by-step guide to building a minimal FastAPI app with Docker, SQLite, and tests. This project demonstrates core FastAPI concepts: routing, path/query parameters, request bodies, database integration, and testing.

---

## What's Included

1. **A minimal FastAPI application** (`main.py`) with root, health, and items API
2. **Dependency list** (`requirements.txt`) for Python packages
3. **A Docker image** (`Dockerfile`) that runs the app in a container
4. **Docker Compose** (`docker-compose.yml`) for one-command run with hot reload
5. **A `.dockerignore`** so unnecessary files stay out of the image
6. **A persistent database** (SQLite + SQLAlchemy) for items (Step 10)
7. **A test framework** (pytest + FastAPI TestClient) for API tests (Step 11)

By the end, you can start the API with a single command and edit code while it reloads automatically.

---

## Quick Start

```bash
# Start the app
docker compose up --build

# Run tests
docker compose run --rm api pytest tests/ -v
```

Then open:
- **http://localhost:8000** – API
- **http://localhost:8000/docs** – Interactive API docs

---

## Project Structure

```
first-fastapi/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── database.py           # SQLAlchemy engine, session, get_db (Step 10)
├── models.py            # ORM models, e.g. Item (Step 10)
├── Dockerfile           # How to build the container image
├── docker-compose.yml   # How to run the container (with options)
├── .dockerignore        # Files to exclude from the Docker build
├── conftest.py          # Root: set DATABASE_URL for tests (Step 11)
├── README.md            # This file
└── tests/               # Test package (Step 11)
    ├── __init__.py
    ├── conftest.py      # Pytest fixtures (e.g. reset_db)
    └── test_main.py     # API tests with TestClient
```

---

## Dependencies: `requirements.txt`

**What it is:** A list of Python packages and (optionally) versions. `pip` uses it to install everything the app needs.

**What we put in it:**

| Package | Purpose |
|--------|---------|
| `fastapi` | Web framework: routing, validation, docs, async support |
| `uvicorn[standard]` | ASGI server that runs the FastAPI app; `[standard]` adds performance extras |

**Why versions?** Pinning versions (e.g. `fastapi==0.115.6`) makes builds reproducible. You can relax this later (e.g. `fastapi>=0.100`) if you prefer.

**Key idea:** All app dependencies live in one file. Anyone (or Docker) can run `pip install -r requirements.txt` and get the same environment.

**Copy-paste: `requirements.txt`**

```txt
# FastAPI and ASGI server
fastapi==0.115.6
uvicorn[standard]==0.32.1

# Database (Step 10)
sqlalchemy==2.0.36

# Testing (TestClient uses httpx)
pytest==8.3.4
httpx==0.28.1
```

---

## The FastAPI App: `main.py`

**What it is:** The actual web application. FastAPI uses this file and the `app` object to serve HTTP endpoints.

**Concepts used:**

- **`FastAPI()`** – Creates the app. We set `title`, `description`, and `version`; these show up in the auto-generated docs at `/docs`.
- **`@app.get("/")`** – Registers a function to handle `GET` requests to the root path.
- **Returning a dict** – FastAPI automatically converts it to JSON.

**Endpoints we defined:**

| Path | Method | Purpose |
|------|--------|--------|
| `/` | GET | Simple "hello" message |
| `/health` | GET | Health check (useful for Docker, load balancers, monitoring) |

**Try it:** After starting the app, open:

- **http://localhost:8000** – JSON response from `/`
- **http://localhost:8000/docs** – Interactive Swagger UI (try the endpoints from the browser)
- **http://localhost:8000/redoc** – Alternative API documentation

**Copy-paste: initial `main.py` (before Step 8)**

```python
"""
FastAPI learning project - minimal app to get started.
Run with: uvicorn main:app --reload
"""
from fastapi import FastAPI

app = FastAPI(
    title="First FastAPI",
    description="A simple API to learn FastAPI basics",
    version="0.1.0",
)


@app.get("/")
def root():
    """Root endpoint - says hello."""
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
def health():
    """Health check for Docker/load balancers."""
    return {"status": "ok"}
```

---

## The Dockerfile

**What it is:** Instructions for building a Docker *image*. The image is a snapshot of the OS, Python, dependencies, and your code. You then run that image as a *container*.

**Line by line:**

| Instruction | Meaning |
|-------------|---------|
| `FROM python:3.12-slim` | Start from the official Python 3.12 image; "slim" keeps the image smaller. |
| `WORKDIR /app` | Use `/app` inside the container as the current directory. |
| `COPY requirements.txt .` | Copy only the dependency file first (see below). |
| `RUN pip install --no-cache-dir -r requirements.txt` | Install dependencies; `--no-cache-dir` reduces image size. |
| `COPY main.py .` | Copy the application code. |
| `EXPOSE 8000` | Document that the app listens on port 8000 (does not publish it; `docker run -p` does). |
| `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]` | Default command when the container starts. `0.0.0.0` makes the server reachable from outside the container. |

**Why copy `requirements.txt` before `main.py`?** Docker builds in layers. If only `main.py` changes, Docker reuses the layer where `pip install` ran, so rebuilds are faster. This is a common pattern in Python Dockerfiles.

**Copy-paste: `Dockerfile`**

```dockerfile
# Use official Python slim image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy dependency file first (better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py database.py models.py .

# Expose port (uvicorn default)
EXPOSE 8000

# Run the app with uvicorn (host 0.0.0.0 so Docker can forward ports)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Docker Compose: `docker-compose.yml`

**What it is:** A way to define and run your app (and optionally other services) with one command. It uses the Dockerfile to build the image and then runs the container with the options we want.

**What we configured:**

| Key | Meaning |
|-----|---------|
| `build: .` | Build the image from the Dockerfile in the current directory. |
| `ports: "8000:8000"` | Map host port 8000 to container port 8000 so you can open http://localhost:8000. |
| `volumes: - .:/app` | Mount the current directory into `/app` in the container so code changes are visible inside the container. |
| `command: uvicorn ... --reload` | Run uvicorn with `--reload` so the server restarts when you change code. |
| `environment: PYTHONUNBUFFERED=1` | Makes Python output show up immediately in `docker compose` logs. |

**Result:** One command starts the API and gives you hot reload while you learn and edit `main.py`.

**Copy-paste: `docker-compose.yml`**

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      # Mount source for development (changes reflect after reload)
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    environment:
      - PYTHONUNBUFFERED=1
```

---

## `.dockerignore`

**What it is:** Like `.gitignore`, but for Docker builds. Files and directories listed here are not sent to the Docker daemon when you run `docker build` or `docker compose build`.

**What we excluded:**

- `.git` – version control data (not needed in the image)
- `.idea` – IDE settings (not needed in the image)
- `__pycache__`, `*.pyc` – Python bytecode (will be recreated in the container)
- `.env` – often holds secrets; avoid copying into the image by default
- `*.md` – documentation (optional; keeps the build context smaller)

**Why it matters:** Smaller build context and cleaner images; you also avoid accidentally baking secrets or junk into the image.

**Copy-paste: `.dockerignore`**

```
.git
.idea
__pycache__
*.pyc
.env
*.md
```

---

## How to Run Everything

### Using Docker Compose (recommended)

```bash
# From the project root (first-fastapi/)
docker compose up --build
```

- `up` – build (if needed), create, and start the container.
- `--build` – force a rebuild of the image (use when you change Dockerfile or requirements.txt).

Stop with `Ctrl+C`. To run in the background, add `-d`:

```bash
docker compose up --build -d
```

Then open:

- **http://localhost:8000** – API
- **http://localhost:8000/docs** – Interactive API docs

### Using Docker only (no Compose)

```bash
docker build -t first-fastapi .
docker run -p 8000:8000 first-fastapi
```

Here you don't get the volume mount or `--reload`; code changes require a rebuild and new container. Good for a quick test of the "production-style" image.

### Without Docker (local Python)

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Same app, same URLs. Useful if you want to debug or run without Docker.

---

## Add an in-memory items list

This step adds a small "items" API so you can practice **path parameters**, **query parameters**, and **request bodies** with a Pydantic model. Data is kept in an in-memory list (no database); it resets whenever the app restarts.

### 8.1 Concepts you'll use

| Concept | Where | Purpose |
|--------|--------|---------|
| **In-memory store** | A list (e.g. `items_db`) | Hold items for the lifetime of the process. |
| **Pydantic model** | `ItemCreate` | Define the shape of the JSON body and get validation for free. |
| **Path parameter** | `GET /items/{item_id}` | Get one item by position in the list. |
| **Query parameters** | `GET /items?skip=0&limit=10` | Paginate the list (optional, with defaults). |
| **POST + body** | `POST /items` with JSON | Create an item; FastAPI validates the body with the Pydantic model. |

### 8.2 Add the in-memory store and model

At the top of `main.py`, add the Pydantic model and the list:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ... existing app setup ...

# In-memory store for items (resets when the app restarts)
items_db: list[dict] = []


class ItemCreate(BaseModel):
    """Schema for creating an item (request body)."""
    name: str
    description: str | None = None
    price: float
```

- **`ItemCreate`** – Fields `name`, optional `description`, and `price`. FastAPI will reject requests whose body doesn't match (e.g. missing `name` or wrong types).
- **`items_db`** – A list of dicts. Each item we "create" is appended here; we use the index as `id`.

### 8.3 List items with query parameters

```python
@app.get("/items", response_model=list[dict])
def list_items(skip: int = 0, limit: int = 10):
    """List items with optional pagination (query params: skip, limit)."""
    return items_db[skip : skip + limit]
```

- **`skip`** and **`limit`** – No path in the decorator, so FastAPI treats them as **query parameters** (e.g. `/items?skip=0&limit=10`). Defaults make them optional.
- **`response_model=list[dict]`** – Documents the response type in the OpenAPI schema (and can validate/filter the response if you need it later).

### 8.4 Get one item by path parameter

```python
@app.get("/items/{item_id}", response_model=dict)
def get_item(item_id: int):
    """Get a single item by id (path parameter)."""
    if item_id < 0 or item_id >= len(items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]
```

- **`{item_id}`** in the path – FastAPI passes it as the **path parameter** and converts it to `int` (invalid values get a 422).
- **`HTTPException`** – Return a proper 404 when the index is out of range.

### 8.5 Create an item with POST and a request body

```python
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
```

- **`item: ItemCreate`** – FastAPI reads the JSON body and validates it with `ItemCreate`; invalid payloads get a 422 with error details.
- **`status_code=201`** – REST convention: 201 Created for a successful create.

### 8.6 Try it

1. Start the app (`docker compose up --build` or `uvicorn main:app --reload`).
2. Open **http://localhost:8000/docs**.
3. **POST /items** – Click "Try it out", use a body like:
   ```json
   { "name": "Widget", "description": "A nice widget", "price": 9.99 }
   ```
   Execute; you should get 201 and the created item with `id: 0`.
4. **GET /items** – Returns the list (optionally use `skip` and `limit` in the query).
5. **GET /items/0** – Returns the item you created. Try `/items/99` to see a 404.

The in-memory list ties these concepts together: you list with query params, get one with a path param, and create with a validated body. Data is lost on restart; a later step could add a real database.

### 8.7 Complete code: full `main.py` (with items API)

If you prefer to paste the whole file instead of applying 8.2–8.5 step by step, replace the contents of `main.py` with:

```python
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
```

---

## Add a persistent database

This step replaces the in-memory list with **SQLite** and **SQLAlchemy** so items survive restarts. You get a real table, sessions, and a `get_db` dependency.

### 10.1 What you'll use

| Piece | Purpose |
|-------|---------|
| **SQLite** | Single-file database; no separate server. Good for learning and small apps. |
| **SQLAlchemy** | ORM: define tables as Python classes, run queries with sessions. |
| **database.py** | Engine, `SessionLocal`, `Base`, and a `get_db()` dependency that yields a session per request. |
| **models.py** | ORM model(s), e.g. `Item`, mapped to the `items` table. |
| **Depends(get_db)** | FastAPI injects a DB session into each route that declares it. |

### 10.2 Add SQLAlchemy to dependencies

In `requirements.txt` add:

```txt
# Database
sqlalchemy==2.0.36
```

### 10.3 Create the database module

**Copy-paste: `database.py`**

```python
"""
Database connection and session management.
Uses SQLite by default; set DATABASE_URL for a different backend.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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
```

- **DATABASE_URL** – Default `sqlite:///./app.db` (file `app.db` in the current directory). Override with the env var for tests or production.
- **get_db** – Generator: yield one session per request; FastAPI calls it when a route uses `Depends(get_db)`.

### 10.4 Create the Item model

**Copy-paste: `models.py`**

```python
"""
SQLAlchemy ORM models.
"""
from sqlalchemy import Column, Integer, String, Float, Text
from database import Base


class Item(Base):
    """Item table: id, name, description, price."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
```

### 10.5 Wire the app to the database

In `main.py`:

1. Create tables on startup: `Base.metadata.create_all(bind=engine)` (so `app.db` and the `items` table exist).
2. Use `Depends(get_db)` in routes that need a session.
3. Replace the in-memory list with `db.query(Item)` / `db.add` / `db.commit` / `db.refresh`.
4. Convert ORM rows to dicts for JSON (e.g. a small `item_to_dict(row)` helper).

**Copy-paste: full `main.py` (with persistent DB)**

```python
"""
FastAPI learning project - minimal app to get started.
Run with: uvicorn main:app --reload
"""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

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
```

### 10.6 Run and try it

1. Start the app: `docker compose up --build` or `uvicorn main:app --reload`.
2. Create an item via **POST /items** (e.g. in `/docs`).
3. Restart the app; call **GET /items** again — the item is still there (stored in `app.db`).

Add `app.db` (and `*.db` if you like) to `.gitignore` so the DB file is not committed.

### 10.7 Tests with a separate DB

Tests should not use `app.db`. Set **DATABASE_URL** before the app (and `database`) is loaded so the app uses a test database:

- **Root `conftest.py`** (project root): set `os.environ["DATABASE_URL"] = "sqlite:///./test.db"` at the top. Pytest loads this before test modules, so `database.py` and `main` see the test URL when they are first imported.
- **tests/conftest.py**: add an autouse fixture that deletes all rows from `items` after each test (`reset_db`), so each test starts with an empty table.

That way the app under test uses `test.db`, and tests stay isolated. See the repo's `conftest.py` and `tests/conftest.py` for the exact snippets.

---

## Add a test framework

This step adds **pytest** and FastAPI's **TestClient** so you can test your API without starting a server. Tests run in process and hit your routes like real HTTP requests.

### 11.1 What you'll use

| Tool | Purpose |
|------|---------|
| **pytest** | Discovers and runs test functions; rich assertions and fixtures. |
| **TestClient** (from `fastapi.testclient`) | Calls your FastAPI app in process; same interface as `requests` (`.get()`, `.post()`, `.json()`, etc.). Requires **httpx** to be installed. |
| **conftest.py** | Pytest loads this automatically; we use it to set a test DB and reset data so tests stay independent. |

### 11.2 Add pytest to dependencies

Add pytest and httpx to `requirements.txt` (TestClient depends on httpx under the hood):

```txt
# Database (Step 10)
sqlalchemy==2.0.36

# Testing (TestClient uses httpx)
pytest==8.3.4
httpx==0.28.1
```

Reinstall if needed: `pip install -r requirements.txt` (or rebuild the Docker image if you run tests inside the container).

### 11.3 Create the test package and fixture

Create a `tests` directory and an empty package so Python (and pytest) treat it as a package. Use a root `conftest.py` to set `DATABASE_URL` to a test DB (e.g. `test.db`) before the app loads. In `tests/conftest.py`, add a fixture that clears the `items` table after each test so tests stay independent.

**Copy-paste: `tests/__init__.py`**

```python
# Tests package
```

See **Step 10.7** for how the test DB and reset fixture are set up. The repo's root `conftest.py` sets `DATABASE_URL`; `tests/conftest.py` defines a `reset_db` fixture that clears the `items` table after each test.

### 11.4 Write API tests with TestClient

Create `tests/test_main.py`. Import your app, create a `TestClient(app)`, and call `.get()`, `.post()`, etc. Assert on `response.status_code` and `response.json()`.

**Copy-paste: `tests/test_main.py`**

```python
"""
Tests for the FastAPI app using TestClient.
Run with: pytest tests/ -v
"""
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    """GET / returns 200 and the hello message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from FastAPI!"}


def test_health():
    """GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_items_empty():
    """GET /items returns empty list when no items exist."""
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items_with_pagination():
    """GET /items?skip=0&limit=2 returns only the requested slice."""
    client.post("/items", json={"name": "A", "description": None, "price": 1.0})
    client.post("/items", json={"name": "B", "description": None, "price": 2.0})
    client.post("/items", json={"name": "C", "description": None, "price": 3.0})
    response = client.get("/items?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "B"
    assert data[1]["name"] == "C"


def test_create_item():
    """POST /items creates an item and returns 201 with the created item."""
    response = client.post(
        "/items",
        json={"name": "Widget", "description": "A nice widget", "price": 9.99},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] >= 1  # DB autoincrement
    assert data["name"] == "Widget"
    assert data["description"] == "A nice widget"
    assert data["price"] == 9.99


def test_create_item_optional_description():
    """POST /items accepts missing description (optional field)."""
    response = client.post("/items", json={"name": "Thing", "price": 5.0})
    assert response.status_code == 201
    assert response.json()["description"] is None


def test_get_item():
    """GET /items/{item_id} returns the item when it exists."""
    create = client.post("/items", json={"name": "Widget", "description": None, "price": 9.99})
    item_id = create.json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Widget"


def test_get_item_not_found():
    """GET /items/{item_id} returns 404 when item does not exist."""
    response = client.get("/items/99")
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_create_item_invalid_body():
    """POST /items returns 422 when required fields are missing."""
    response = client.post("/items", json={"name": "No price"})
    assert response.status_code == 422
```

### 11.5 Run the tests

From the **project root** (so that `main` is importable):

```bash
pytest tests/ -v
```

- **`tests/`** – Directory (or file) to collect tests from.
- **`-v`** – Verbose: one line per test.

To run inside Docker (same Python version as the app):

```bash
docker compose run --rm api pytest tests/ -v
```

**Note:** The app uses Python 3.12 (e.g. `str | None`). Run tests with Python 3.10+ locally, or use the Docker command above.

### 11.6 What to try next

- Add a test for **PUT** or **DELETE** when you add those endpoints.
- Use **`response.raise_for_status()`** if you expect success and want a clear error when the status is 4xx/5xx.
- Use **pytest parametrize** to test several inputs in one test: `@pytest.mark.parametrize("item_id", [0, 1, 2])`.

---

## Next Steps for Learning FastAPI

Now that you have path params, query params, request bodies, a persistent DB, and tests in place, you can extend the app further:

1. **PATCH /items/{item_id}** – Update an item (body with optional fields). *Implemented in the repo: see `ItemUpdate` and `update_item` in `main.py`.*
2. **DELETE /items/{item_id}** – Remove an item from the database.
3. **Filtering** – Add query params like `min_price` or `name_contains` in `list_items`.
4. **Alembic** – Add schema migrations for the database instead of `create_all`.

### PATCH /items/{item_id} (optional body fields)

Use a Pydantic model with **all optional fields** and **`model_dump(exclude_unset=True)`** so only provided fields are updated:

```python
class ItemUpdate(BaseModel):
    """Schema for partial update (all fields optional)."""
    name: str | None = None
    description: str | None = None
    price: float | None = None

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
```

The official FastAPI docs are at [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) and match this style of app (async, type hints, automatic docs).

---

## Quick Reference

| Goal | Command |
|------|---------|
| Start app (with reload) | `docker compose up --build` |
| Start in background | `docker compose up --build -d` |
| Stop background app | `docker compose down` |
| Rebuild after changing Dockerfile/requirements | `docker compose up --build` |
| View logs | `docker compose logs -f` |
| Run locally (no Docker) | `uvicorn main:app --reload` |
| Run tests | `pytest tests/ -v` |
| Run tests in Docker | `docker compose run --rm api pytest tests/ -v` |

---

You've now seen how a minimal FastAPI app is structured, how dependencies are declared, how Docker and Docker Compose run it, how to add an in-memory list and a test framework, and how to iterate on the code. Use this as a reference while you work through the FastAPI docs and add more endpoints and features.
