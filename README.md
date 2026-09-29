# Getting Fast at FastAPI

A step-by-step guide to building a minimal FastAPI app with Docker, SQLite (local), PostgreSQL (Docker), and tests. This project demonstrates core FastAPI concepts: routing, path/query parameters, request bodies, database integration, and testing.

---

## What's Included

1. **A minimal FastAPI application** (`main.py`) with root, health, and items API
2. **Dependency list** (`requirements.txt`) for Python packages
3. **A Docker image** (`Dockerfile`) that runs the app in a container
4. **Docker Compose** (`docker-compose.yml`) for one-command run with hot reload
5. **A `.dockerignore`** so unnecessary files stay out of the image
6. **A persistent database** (SQLite + SQLAlchemy) for items (Step 10)
7. **A test framework** (pytest + FastAPI TestClient) for API tests (Step 11)
8. **A CI/CD pipeline** (GitHub Actions) for automated linting and testing (Step 12)
9. **API key authentication** (static key) for protecting endpoints (Step 13)
10. **Service layer** (controller-service pattern) separating business logic from routes (Step 14)
11. **Database schema changes** (adding fields) with notes on migrations (Step 15)
12. **Production best practices** (typed responses, validation rules, lifespan startup, secure auth) (Step 16)
13. **Mature app structure** (centralized config, full service layer, logging, exception handlers) (Step 17)
14. **Production structure** (`app/` package, APIRouter, Alembic migrations, CORS, auth on writes) (Step 18)
15. **Categories, filtering, and relationships** (Category CRUD, item query filters, startup migrations) (Step 19)
16. **Pagination metadata** on list endpoints (`{ items, total, skip, limit }`) (Step 20)
17. **Extended item stats** with per-category breakdown (Step 20.3 capstone)
18. **CategoryService unit tests** (`tests/test_category_service.py`) (Step 21.1)
19. **JWT authentication** – register, login, Bearer tokens on write endpoints (Step 22)
20. **Rate limiting** – IP-based limits on auth and write endpoints via slowapi (Step 23)
21. **PostgreSQL** – production database via Docker Compose (Step 24)

**Related learning projects:** See [learning-101](https://github.com/iammikek/learning-101) for the full catalogue.

By the end, you can start the API with a single command and edit code while it reloads automatically.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Dependencies: requirements.txt](#2-dependencies-requirementstxt)
3. [The FastAPI App: main.py](#3-the-fastapi-app-mainpy)
4. [The Dockerfile](#4-the-dockerfile)
5. [Docker Compose: docker-compose.yml](#5-docker-compose-docker-composeyml)
6. [.dockerignore](#6-dockerignore)
7. [How to Run Everything](#7-how-to-run-everything)
8. [Add an in-memory items list](#8-add-an-in-memory-items-list)
9. [Add a persistent database](#10-add-a-persistent-database)
10. [Add a test framework](#11-add-a-test-framework)
11. [Add a CI/CD pipeline](#12-add-a-cicd-pipeline)
12. [Add API key authentication](#13-add-api-key-authentication)
13. [Add a service layer (controller-service pattern)](#14-add-a-service-layer-controller-service-pattern)
14. [Add a new field to the items table](#15-add-a-new-field-to-the-items-table)
15. [Production best practices](#16-production-best-practices)
16. [Mature app structure](#17-mature-app-structure)
17. [Production structure](#18-production-structure)
18. [Categories, filtering, and relationships](#19-categories-filtering-and-relationships)
19. [Pagination metadata](#20-pagination-metadata)
20. [Next Steps for Learning FastAPI](#21-next-steps-for-learning-fastapi)
21. [JWT authentication](#22-jwt-authentication)
22. [Rate limiting](#23-rate-limiting)
23. [PostgreSQL](#24-postgresql)
24. [Quick Reference](#25-quick-reference)
25. [*-101 Family](https://github.com/iammikek/learning-101)
---

## Quick Start

**Pick one:** Docker **or** local uvicorn — both use port 8000, so don't run them at the same time.

### Option A: Docker (recommended)

```bash
cp .env.example .env   # optional
docker compose up --build
```

### Option B: Local Python

```bash
cp .env.example .env   # optional
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn main:app --reload
```

Migrations run automatically on startup — you don't need `alembic upgrade head` first.

### Tests

```bash
source .venv/bin/activate
pytest tests/ -v --cov=app
```

Then open:
- **http://localhost:8000** – API
- **http://localhost:8000/docs** – Interactive API docs (register + login, then **Authorize** with `Bearer <token>` for POST/PATCH/DELETE)

**Note:** Local Python uses **SQLite** by default (`DATABASE_URL=sqlite:///./app.db`). **Docker Compose** uses **PostgreSQL** (Step 24). See `.env.example` for variables. Docker Compose loads `.env` automatically via `env_file`.

---

## Project Structure

```
fastAPI-101/
├── main.py              # Uvicorn entry point (imports app from package)
├── app/                 # Application package (Step 18)
│   ├── main.py          # App factory, middleware, exception handlers
│   ├── config.py        # Typed settings via pydantic-settings
│   ├── database.py      # SQLAlchemy engine, session, get_db
│   ├── models.py        # ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── security.py      # Password hashing + JWT helpers (Step 22)
│   ├── auth.py          # JWT dependency (get_current_user)
│   ├── rate_limit.py    # slowapi limiter (Step 23)
│   ├── services.py      # Service layer (business logic)
│   ├── exceptions.py    # Application exceptions
│   └── routers/         # API route modules (Step 18)
│       ├── health.py    # GET /, GET /health
│       ├── auth.py      # POST /auth/register, /auth/login, GET /auth/me
│       ├── categories.py
│       └── items.py     # /items CRUD + stats
├── alembic/             # Database migrations (Step 18)
├── alembic.ini
├── requirements.txt     # Production Python dependencies
├── requirements-dev.txt # Dev/test/lint dependencies
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── conftest.py          # Root: set DATABASE_URL for tests
├── pyproject.toml
├── README.md
├── .github/workflows/ci.yml
└── tests/
    ├── conftest.py
    ├── test_app.py
    ├── test_items_*.py
    ├── test_categories_*.py
    ├── test_item_service.py
    ├── test_category_service.py
    ├── test_auth.py
    └── test_rate_limit.py
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
| `env_file: .env` | Load `API_KEY` and `DATABASE_URL` from a local `.env` file (Step 16). |
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
    env_file:
      - .env
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
# From the project root
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
docker build -t fastapi-101 .
docker run -p 8000:8000 fastapi-101
```

Here you don't get the volume mount or `--reload`; code changes require a rebuild and new container. Good for a quick test of the "production-style" image.

### Without Docker (local Python)

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn main:app --reload
```

Same app, same URLs. Migrations run automatically when the app starts (see Step 19.4).

**Restart the server:** press **Ctrl+C** in the terminal, then run `uvicorn main:app --reload` again. With `--reload`, code changes usually reload on their own; restart manually after editing `.env` or if the process gets stuck.

**`zsh: command not found: uvicorn`** — activate the venv first (`source .venv/bin/activate`). Uvicorn is installed in `.venv`, not globally.

**`Address already in use` (port 8000)** — something else is already bound to that port. Common causes:

| Cause | Fix |
|-------|-----|
| Docker still running | `docker compose down` |
| Old uvicorn still running | **Ctrl+C** in that terminal, or `lsof -i :8000` then `kill <PID>` |
| Want both Docker and local | Run local on another port: `uvicorn main:app --reload --port 8001` |

Don't run `docker compose up` and local `uvicorn` at the same time — they both default to port 8000.

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

1. Create tables on startup: `Base.metadata.create_all(bind=engine)` (so `app.db` and the `items` table exist). *In the current repo this runs in a lifespan hook — see Step 16.*
2. Use `Depends(get_db)` in routes that need a session.
3. Replace the in-memory list with `db.query(Item)` / `db.add` / `db.commit` / `db.refresh`.
4. Convert ORM rows to JSON responses (Step 16 uses `ItemResponse.model_validate(row)` instead of a manual dict helper).

**Copy-paste: full `main.py` (with persistent DB — simplified tutorial version)**

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
- **tests/conftest.py**: a session-scoped `create_tables` fixture runs `Base.metadata.create_all()` (mirrors app lifespan startup), and an autouse `reset_db` fixture deletes all rows from `items` after each test so each test starts with an empty table.

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

## 12. Add a CI/CD pipeline

This step adds **GitHub Actions** to automatically run linting and tests on every push and pull request. This catches issues before they reach the main branch.

### 12.1 What you'll use

| Tool | Purpose |
|------|---------|
| **GitHub Actions** | CI/CD platform built into GitHub; runs workflows defined in YAML files. |
| **ruff** | Fast Python linter that checks code style and catches errors. |
| **Workflow file** | `.github/workflows/ci.yml` defines when and how to run the pipeline. |

### 12.2 Add ruff to dependencies

Add ruff to `requirements.txt`:

```txt
# Linting
ruff==0.6.9
```

### 12.3 Configure ruff

Create `pyproject.toml` to configure ruff's rules and settings:

**Copy-paste: `pyproject.toml`**

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["main", "database", "models"]
```

- **`select`** – Enable rule categories: E (errors), F (pyflakes), I (import sorting), N (naming), W (warnings), UP (pyupgrade).
- **`line-length`** – Max line length (100 characters).
- **`target-version`** – Python version to target (3.12).

### 12.4 Create the GitHub Actions workflow

Create `.github/workflows/ci.yml` to define the pipeline:

**Copy-paste: `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run ruff linter
      run: |
        ruff check .
    
    - name: Run tests
      run: |
        pytest tests/ -v
```

**What this does:**

- **`on: push/pull_request`** – Triggers on pushes and PRs to `main`.
- **`runs-on: ubuntu-latest`** – Uses GitHub's Ubuntu runner.
- **`actions/checkout@v4`** – Checks out your code.
- **`actions/setup-python@v5`** – Sets up Python 3.12.
- **`ruff check .`** – Lints all Python files.
- **`pytest tests/ -v`** – Runs all tests.

### 12.5 How it works

1. **Push to GitHub** – When you push code or open a PR, GitHub Actions starts the workflow.
2. **Checkout code** – The runner gets your repository.
3. **Set up Python** – Python 3.12 is installed.
4. **Install dependencies** – `pip install -r requirements.txt` installs FastAPI, pytest, ruff, etc.
5. **Run linting** – `ruff check .` scans for style issues and errors.
6. **Run tests** – `pytest tests/ -v` runs your test suite.

If linting or tests fail, the workflow fails and you'll see a red X on the commit/PR. Fix the issues and push again.

### 12.6 View workflow runs

- Go to your repository on GitHub.
- Click the **"Actions"** tab.
- You'll see a list of workflow runs with their status (green checkmark = passed, red X = failed).
- Click a run to see detailed logs for each step.

### 12.7 Try it locally

Before pushing, you can run the same checks locally:

```bash
# Install ruff if not already installed
pip install ruff

# Run linting
ruff check .

# Run tests
pytest tests/ -v
```

---

## 13. Add API key authentication

This step adds **simple API key authentication** using FastAPI's dependency injection. You'll protect endpoints that require authentication (like DELETE) with a static API key passed in headers.

### 13.1 What you'll use

| Concept | Purpose |
|---------|---------|
| **Dependency injection** | FastAPI's `Depends()` lets you create reusable dependencies (like auth checks) that run before your route handler. |
| **APIKeyHeader** | Registers the `X-API-Key` header in OpenAPI so Swagger UI shows an **Authorize** button (Step 16). |
| **secrets.compare_digest** | Timing-safe comparison of API keys (Step 16). |
| **HTTPException** | Return 401 Unauthorized when authentication fails. |
| **Environment variable** | Store the API key in `API_KEY` env var (with a default for development). |

### 13.2 Create the authentication module

**Copy-paste: `auth.py`**

```python
"""
Simple API key authentication.
Uses a static API key from environment variable API_KEY (default: 'dev-key-123').
"""
import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY", "dev-key-123")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(x_api_key: str | None = Depends(api_key_header)):
    """
    Dependency that verifies the API key from the X-API-Key header.
    Raises 401 if the key is missing or invalid.
    """
    if x_api_key is None or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
```

- **`APIKeyHeader`** – Reads the header and registers it in OpenAPI docs for the Authorize button.
- **`secrets.compare_digest`** – Compares keys in constant time to reduce timing-attack risk.
- **`Depends(verify_api_key)`** – When used in a route, FastAPI calls `verify_api_key` first and only runs the route if it succeeds (doesn't raise an exception).

### 13.3 Protect an endpoint with authentication

Add a DELETE endpoint that requires the API key:

```python
from auth import verify_api_key

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
```

- **`Depends(verify_api_key)`** – The dependency runs first; if the API key is invalid, it raises 401 and the route handler never runs.
- **`status_code=204`** – DELETE typically returns 204 No Content (empty body).

### 13.4 Update Dockerfile

Add `auth.py` to the COPY command:

```dockerfile
COPY main.py database.py models.py auth.py .
```

### 13.5 Try it

1. Start the app: `docker compose up --build` or `uvicorn main:app --reload`.
2. Open **http://localhost:8000/docs**.
3. Try **DELETE /items/{item_id}** without the header – you'll get 401.
4. Click "Authorize" (lock icon) or add header manually:
   - Header name: `X-API-Key`
   - Value: `dev-key-123`
5. Try DELETE again – it should work (204).

### 13.6 Set API key in production

Create a `.env` file (copy from `.env.example`) or set environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and set your API key
API_KEY=your-secret-key-here
```

Or set it directly:

```bash
export API_KEY=your-secret-key-here
```

Or in `docker-compose.yml` (recommended — loads all vars from `.env`):

```yaml
env_file:
  - .env
environment:
  - PYTHONUNBUFFERED=1
```

Or set individual variables inline:

```yaml
environment:
  - PYTHONUNBUFFERED=1
  - API_KEY=your-secret-key-here
```

**Security note:** This is a simple static key for learning. For production, consider:
- JWT tokens for user authentication
- OAuth2 with password flow
- API key rotation
- Rate limiting

**Note:** `.env` files are gitignored (see `.gitignore`) so secrets don't get committed. Use `.env.example` to document what variables are needed.

---

## 14. Add a service layer (controller-service pattern)

This step introduces the **controller-service pattern**: separate business logic from API routes. Routes (controllers) handle HTTP concerns; service classes handle business logic.

### 14.1 What you'll use

| Concept | Purpose |
|---------|---------|
| **Service class** | Contains business logic (database operations, calculations, validations). |
| **Controller (route)** | Handles HTTP (request/response, status codes, exceptions). Calls service methods. |
| **Separation of concerns** | Routes stay thin; business logic is reusable and testable independently. |

### 14.2 Create the service class

Create `services.py` with a service class that contains business logic:

**Copy-paste: `services.py`**

```python
"""
Service layer: business logic separated from API routes.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Item


class ItemService:
    """Service class for item business logic."""

    @staticmethod
    def get_stats(db: Session) -> dict:
        """
        Calculate statistics about items.
        Returns a dict with count, average price, min price, max price.
        """
        count = db.query(func.count(Item.id)).scalar()
        if count == 0:
            return {
                "total_items": 0,
                "average_price": 0.0,
                "min_price": None,
                "max_price": None,
            }

        avg_price = db.query(func.avg(Item.price)).scalar()
        min_price = db.query(func.min(Item.price)).scalar()
        max_price = db.query(func.max(Item.price)).scalar()

        return {
            "total_items": count,
            "average_price": round(float(avg_price), 2),
            "min_price": float(min_price),
            "max_price": float(max_price),
        }
```

- **`@staticmethod`** – Methods don't need `self`; the class is a namespace for related functions.
- **Business logic** – The service handles calculations (count, average, min, max) using SQLAlchemy's `func`.
- **No HTTP concerns** – Returns plain Python dicts, not HTTP responses or exceptions.

### 14.3 Add a route that uses the service

Add a new endpoint in `main.py` that calls the service (register this route **before** `/items/{item_id}`):

```python
from schemas import ItemStatsResponse
from services import ItemService

@app.get("/items/stats/summary", response_model=ItemStatsResponse)
def get_items_stats(db: Session = Depends(get_db)):
    """Get statistics about items (uses service layer)."""
    return ItemService.get_stats(db)
```

**What this demonstrates:**

- **Thin controller** – The route is just 3 lines: import service, call method, return result.
- **Reusable logic** – `ItemService.get_stats()` can be called from other places (CLI, background jobs, other routes) without HTTP.
- **Separation** – HTTP concerns (route, status codes) stay in `main.py`; business logic (calculations) stays in `services.py`.

### 14.4 Update Dockerfile

Add `services.py` to the COPY command:

```dockerfile
COPY main.py database.py models.py auth.py services.py .
```

### 14.5 Try it

1. Start the app: `docker compose up --build` or `uvicorn main:app --reload`.
2. Create some items via **POST /items**.
3. Call **GET /items/stats/summary** – you'll get statistics about all items.
4. Check the response: `{"total_items": 3, "average_price": 20.0, "min_price": 10.0, "max_price": 30.0}` (extended with per-category breakdown in [Step 20.3](#203-extend-item-stats-summary-capstone))

### 14.6 Benefits of this pattern

- **Separation of concerns** – Routes handle HTTP; services handle business logic.
- **Reusability** – Service methods can be used by routes, CLI scripts, background tasks, etc.
- **Testability** – Test service logic without HTTP layer (faster, simpler).
- **Maintainability** – Business logic changes don't require touching route code.

**Note:** For simple apps, this might feel like overkill. As your app grows, this separation becomes valuable. You can gradually refactor existing endpoints to use services as needed.

---

## 15. Add a new field to the items table

This step shows how to add a new column to your database table. We'll add a `category` field to demonstrate the process.

### 15.1 Write a failing test first (TDD)

If you follow **test-driven development**, start with a feature test that describes the behaviour you want. The failure tells you what to build next.

**Copy-paste: add to `tests/test_items_create.py` (or a new file)**

```python
def test_create_item_with_category(client, auth_headers):
    """POST /items accepts category and returns it in the response."""
    response = client.post(
        "/items",
        headers=auth_headers,
        json={"name": "Laptop", "price": 999.99, "category": "Electronics"},
    )
    assert response.status_code == 201
    assert response.json()["category"] == "Electronics"
```

Run `pytest tests/test_items_create.py::test_create_item_with_category -v` — it should **fail** (field not implemented yet).

**TDD order (red → green):**

| Step | Action | Typical failure |
|------|--------|-----------------|
| 1 | Failing test (above) | Assertion or 422/500 |
| 2 | Add `category` to `ItemCreate` / `ItemResponse` | 422 if schema missing field |
| 3 | Update model + create logic to use `category` | `no such column: category` |
| 4 | **Migration** (Alembic) or recreate dev DB | DB accepts the column |
| 5 | Re-run test | Green |

The migration is not written speculatively — you add it when code tries to persist a column that does not exist yet (or when altering an existing production database). In Laravel terms: failing Pest test → migration → model → Form Request → controller.

The sections below follow the **implementation checklist** in dependency order. With TDD, you still apply them, but only after the failing test (and let each failure guide the next change).

### 15.2 What you need to update

When adding a new field, you need to update:
1. **A feature test** (optional but recommended) – describes the new behaviour; write it first if using TDD
2. **The SQLAlchemy model** (`models.py`) – defines the database column
3. **Pydantic schemas** (`schemas.py`) – `ItemCreate` and `ItemUpdate` for request validation
4. **The response schema** (`ItemResponse` in `schemas.py`) – includes the field in JSON responses
5. **The create endpoint** – passes the field when creating items
6. **A migration** (production) or recreate `app.db` / `test.db` (local dev) – see 15.7

### 15.3 Update the model

In `models.py`, add the new column to the `Item` class:

```python
class Item(Base):
    """Item table: id, name, description, price, category."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)  # New optional field
```

- **`nullable=True`** – Makes the field optional (can be `None`). **Important:** This means existing code continues to work without changes.
- **`String(100)`** – Limits the category to 100 characters.

### 15.4 Update Pydantic schemas

**Best practice:** Extract schemas to a separate `schemas.py` file for better organization:

**Copy-paste: `schemas.py`** (request and response schemas)

```python
"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    """Schema for creating an item (request body)."""
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    price: float = Field(gt=0)
    category: str | None = Field(default=None, max_length=100)


class ItemUpdate(BaseModel):
    """Schema for partial update (all fields optional)."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, max_length=100)


class ItemResponse(BaseModel):
    """Schema for item responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: float
    category: str | None
```

Then in `main.py`, import them:

```python
from schemas import ItemCreate, ItemResponse, ItemUpdate
```

**Note:** Because `category` is optional (`| None = None`), existing requests without `category` still work. This keeps earlier tutorial steps compatible.

**Why separate schemas?** Keeping Pydantic models in `schemas.py` separates validation logic from route handlers, making the codebase easier to navigate and maintain.

### 15.5 Update routes to use response schemas

Return `ItemResponse` instead of a manual dict helper:

```python
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
```

- **`model_config = ConfigDict(from_attributes=True)`** – Lets Pydantic read SQLAlchemy ORM objects directly.
- **`ItemResponse.model_validate(row)`** – Converts an ORM row to a typed response (replaces a manual `item_to_dict()` helper).

### 15.6 Update Dockerfile

Add `schemas.py` to the COPY command:

```dockerfile
COPY main.py database.py models.py auth.py services.py schemas.py .
```

### 15.7 Important: Database schema changes

**⚠️ Important:** `Base.metadata.create_all()` (now in the lifespan hook) only creates tables if they don't exist. It **does not** alter existing tables to add new columns.

**For development/testing:**
- Delete `app.db` and `test.db` files
- Restart the app – tables will be recreated with the new schema
- **Existing code continues to work** – because `category` is optional, requests without it still succeed

**For production:**
- Use **Alembic** (database migrations) to alter existing tables safely
- This is covered in "Next Steps" (Alembic)

**Why optional fields help:** By making new fields optional (`nullable=True`, `| None = None`), you can add them without breaking existing API clients or tutorial steps.

### 15.8 Try it

1. Delete existing database files: `rm app.db test.db` (if they exist).
2. Start the app: `docker compose up --build` or `uvicorn main:app --reload`.
3. Create an item with category:
   ```json
   POST /items
   {
     "name": "Laptop",
     "price": 999.99,
     "category": "Electronics"
   }
   ```
4. The response will include `"category": "Electronics"`.
5. Update the category: `PATCH /items/{id}` with `{"category": "Computers"}`.

---

## 16. Production best practices

This step refactors the app toward patterns you'll see in production APIs. If you're coming from Laravel, think of this as adding **API Resources**, **Form Request validation rules**, and **Service Provider boot logic**.

### 16.1 What you'll use

| Concept | Purpose | Laravel parallel |
|---------|---------|------------------|
| **Response schemas** | Typed JSON output; better OpenAPI docs | API Resources (`ItemResource`) |
| **Field constraints** | Validate input beyond "is it a string?" | Form Request rules (`gt:0`, `max:255`) |
| **Query bounds** | Cap pagination params | `$request->validate(['limit' => 'max:100'])` |
| **Lifespan hook** | Run startup logic when the app boots | `AppServiceProvider::boot()` |
| **APIKeyHeader** | Swagger Authorize button for API keys | Sanctum docs in Scribe |

### 16.2 Lifespan startup (instead of import-time side effects)

Move `Base.metadata.create_all()` from module import into a **lifespan** context manager so tables are created when the app starts, not when Python imports the file:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine


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
```

Tests mirror this with a session-scoped `create_tables` fixture in `tests/conftest.py`.

### 16.3 Typed response schemas

Add `ItemResponse` and `ItemStatsResponse` to `schemas.py` and use them as `response_model` on routes:

```python
class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    price: float
    category: str | None
```

In routes, return validated responses instead of manual dicts:

```python
return ItemResponse.model_validate(row)
```

Remove any `item_to_dict()` helper — Pydantic handles the conversion.

### 16.4 Input validation rules

Add constraints to request schemas using Pydantic `Field`:

```python
from pydantic import Field

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    category: str | None = Field(default=None, max_length=100)
```

Invalid payloads return **422 Unprocessable Entity** automatically (e.g. empty name, negative price).

### 16.5 Pagination bounds

Constrain query parameters on `GET /items`:

```python
from fastapi import Query

@app.get("/items", response_model=list[ItemResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    ...
```

### 16.6 Secure API key auth + OpenAPI

The current `auth.py` uses `APIKeyHeader` (Swagger **Authorize** button) and `secrets.compare_digest()` for timing-safe key comparison. See Step 13 for the full module.

### 16.7 Docker Compose loads `.env`

`docker-compose.yml` includes `env_file: .env` so `API_KEY` and `DATABASE_URL` are loaded automatically when running in Docker.

### 16.8 Current `main.py` (full app)

The repo's `main.py` reflects all of the above. Key patterns:

- **Lifespan** creates tables on startup
- **ItemResponse** / **ItemStatsResponse** on all item routes
- **Query bounds** on list pagination
- **Stats route** registered before `/items/{item_id}`
- **DELETE** protected with `Depends(verify_api_key)`

### 16.9 Try it

1. Start the app: `docker compose up --build` or `uvicorn main:app --reload`.
2. Open **http://localhost:8000/docs** — item schemas are fully typed; click **Authorize** to set `X-API-Key`.
3. Try **POST /items** with `{"name": "", "price": -1}` — expect **422**.
4. Try **GET /items?limit=101** — expect **422**.
5. Run tests: `pytest tests/ -v` (32 tests).

---

## 17. Mature app structure

This step adds patterns common in production FastAPI apps (and familiar from Laravel): centralized config, thin controllers, structured logging, and consistent error handling.

### 17.1 Centralized config (`config.py`)

Use **pydantic-settings** to load typed configuration from `.env`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    database_url: str = "sqlite:///./app.db"
    api_key: str = "dev-key-123"
    log_level: str = "INFO"
```

`database.py` and `auth.py` read from `get_settings()` instead of scattered `os.getenv()` calls.

### 17.2 Full service layer

All item CRUD logic lives in `ItemService`. Routes in `main.py` are thin controllers:

```python
@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    row = ItemService.create(db, item)
    return ItemResponse.model_validate(row)
```

### 17.3 Exception handlers

`exceptions.py` defines `ItemNotFoundError`. Global handlers in `main.py` return consistent JSON:

```json
{"detail": "Item not found", "code": "ITEM_NOT_FOUND"}
```

### 17.4 Request logging

An HTTP middleware logs method, path, status code, and duration. Log level is configurable via `LOG_LEVEL` in `.env`.

### 17.5 Health check with database ping

`GET /health` verifies database connectivity and returns:

```json
{"status": "ok", "database": "connected"}
```

Returns **503** if the database is unavailable.

### 17.6 Decimal for money

`price` uses `Numeric(10, 2)` in SQLAlchemy and `Decimal` in Pydantic schemas to avoid floating-point rounding issues.

### 17.7 Split dev and production dependencies

| File | Purpose |
|------|---------|
| `requirements.txt` | Production runtime (FastAPI, SQLAlchemy, pydantic-settings) |
| `requirements-dev.txt` | Dev tools (pytest, ruff, pytest-cov) |

Docker installs only `requirements.txt`. Local development and CI use `requirements-dev.txt`.

CI runs as two parallel jobs in `.github/workflows/ci.yml`:

| Job | Checks |
|-----|--------|
| **Lint** | `ruff check .`, `ruff format --check .` |
| **Test** | `pytest tests/ -v --cov=app` (80% coverage threshold) |

Shared setup (Python, pip cache, install) lives in `.github/actions/setup/`.

### 17.8 Try it

1. Copy `.env.example` to `.env` and optionally set `LOG_LEVEL=DEBUG`.
2. Install dev deps: `pip install -r requirements-dev.txt`
3. Start the app: `uvicorn main:app --reload` — watch request logs in the terminal.
4. Call **GET /health** — confirm `"database": "connected"`.
5. Run tests with coverage: `pytest tests/ -v --cov=app`

**Note:** If you have an existing `app.db` from before Step 17, delete it (`rm app.db`) so the `price` column is recreated as `Numeric`.

---

## 18. Production structure

This step reorganizes the project like a deployable FastAPI app (and familiar Laravel layout): code under an `app/` package, routes in modules, Alembic migrations, CORS, and auth on all write endpoints.

### 18.1 `app/` package layout

Application code lives under `app/` instead of the repo root. Uvicorn still starts via root `main.py`:

```python
from app.main import app
```

### 18.2 APIRouter modules

Routes split into focused modules (like Laravel route files):

| Module | Routes |
|--------|--------|
| `app/routers/health.py` | `GET /`, `GET /health` |
| `app/routers/items.py` | `/items` CRUD + stats |
| `app/routers/categories.py` | `/categories` CRUD |

Registered in `app/main.py` with `include_router()`.

### 18.3 Alembic migrations

Schema changes use **Alembic** instead of `create_all()` at startup:

```bash
alembic upgrade head          # apply migrations
alembic revision -m "message" # create new migration (after model changes)
```

Docker and docker-compose run `alembic upgrade head` before starting uvicorn. Tests apply migrations in `tests/conftest.py`.

### 18.4 Auth on all write endpoints

POST, PATCH, and DELETE require `X-API-Key` (like Laravel `middleware('auth:sanctum')` on a route group). GET endpoints remain public.

### 18.5 CORS

`CORSMiddleware` reads allowed origins from `CORS_ORIGINS` in `.env` (comma-separated).

### 18.6 Try it

1. `cp .env.example .env`
2. `alembic upgrade head` (or `docker compose up --build` — migrations run automatically)
3. `uvicorn main:app --reload`
4. In `/docs`, **Authorize** with your API key before POST/PATCH/DELETE
5. `pytest tests/ -v` (32 tests at this step)

---

## 19. Categories, filtering, and relationships

This step adds a second resource (`Category`), replaces the string `category` field on items with a foreign key, adds query filters on `GET /items`, runs Alembic migrations on local startup, and splits category tests by endpoint (matching the items test layout).

### 19.1 Category model and relationship

Categories live in their own table. Items reference them via `category_id` (Laravel `belongsTo` / `hasMany`):

| Laravel | FastAPI / SQLAlchemy |
|---------|----------------------|
| `Category hasMany Item` | `Category.items` relationship |
| `Item belongsTo Category` | `Item.category_id` FK + nested `category` in responses |

Migration `002_add_categories_table.py` creates `categories`, adds `category_id` to `items`, and drops the old string `category` column.

### 19.2 Category CRUD routes

New router at `app/routers/categories.py`:

| Method | Path | Auth |
|--------|------|------|
| GET | `/categories` | Public |
| GET | `/categories/{id}` | Public |
| POST | `/categories` | API key |
| PATCH | `/categories/{id}` | API key |
| DELETE | `/categories/{id}` | API key |

Deleting a category that still has items returns **409** (`CATEGORY_IN_USE`). Duplicate names return **409** (`CATEGORY_NAME_EXISTS`).

Items now use `category_id` in create/update payloads. Responses include nested category data:

```json
{
  "id": 1,
  "name": "Hammer",
  "category_id": 2,
  "category": { "id": 2, "name": "Tools", "description": null }
}
```

### 19.3 Item query filters

`GET /items` accepts optional filters (Laravel query scopes):

| Param | Example | Behavior |
|-------|---------|----------|
| `min_price` | `?min_price=10` | Price ≥ 10 |
| `max_price` | `?max_price=25` | Price ≤ 25 |
| `category_id` | `?category_id=2` | Items in that category |
| `name_contains` | `?name_contains=widget` | Case-insensitive name match |

Filters combine: `GET /items?category_id=2&min_price=10&max_price=25`

Validation lives in `ItemListFilters` (Pydantic); the service layer applies them to the SQLAlchemy query.

### 19.4 Migrations on local startup

Docker Compose already runs `alembic upgrade head` before uvicorn. Local `uvicorn main:app --reload` now does the same in the app lifespan hook — no more empty-database 500 errors when you forget to migrate.

### 19.5 Tests split by endpoint

Category tests mirror items (one file per route concern):

```
tests/test_categories_list.py
tests/test_categories_create.py
tests/test_categories_update.py
tests/test_categories_delete.py
```

### 19.6 Try it

1. Activate the venv: `source .venv/bin/activate`
2. Start the app: `uvicorn main:app --reload` (migrations run automatically)
3. In `/docs`, **Authorize** with your API key
4. `POST /categories` → `{ "name": "Tools" }`
5. `POST /items` → `{ "name": "Hammer", "price": 10.0, "category_id": 1 }`
6. `GET /items?category_id=1&min_price=5`
7. Run tests: `pytest tests/ -v` (50 tests)

**Note:** If you have an old `app.db` from before Step 19, delete it (`rm app.db`) and restart — the schema changed from string `category` to `category_id`.

---

## 20. Pagination metadata

List endpoints return pagination metadata alongside the data (Laravel `paginate()` equivalent):

```json
{
  "items": [ ... ],
  "total": 42,
  "skip": 0,
  "limit": 10
}
```

- **`total`** – total rows matching the query (before `skip`/`limit`)
- **`skip`** / **`limit`** – echo the request params so clients know where they are

Applies to `GET /items` (with filters) and `GET /categories`.

### 20.1 Paginated response schema

`ItemListResponse` and `CategoryListResponse` wrap the item/category list with metadata. The service layer returns `(rows, total)`; the router builds the response object.

### 20.2 Try it

1. Create several items via `POST /items`
2. `GET /items?skip=0&limit=2` — response includes `"total": N` for the full count
3. `GET /items?category_id=1&limit=5` — `total` reflects filtered count, not just the page size
4. Run tests: `pytest tests/ -v` (70 tests)

### 20.3 Extend item stats summary (capstone)

After categories exist (Step 19), extend **GET /items/stats/summary** with a per-category breakdown. This is a good capstone exercise: service-layer SQL, response schemas, and tests.

**New response fields:**

| Field | Purpose |
|-------|---------|
| `uncategorized_count` | Items with no `category_id` |
| `by_category` | Per-category `item_count` and `average_price` (sorted by category name) |

**Example response:**

```json
{
  "total_items": 4,
  "average_price": 15.0,
  "min_price": 5.0,
  "max_price": 30.0,
  "uncategorized_count": 1,
  "by_category": [
    {
      "category_id": 2,
      "category_name": "Books",
      "item_count": 1,
      "average_price": 15.0
    },
    {
      "category_id": 1,
      "category_name": "Tools",
      "item_count": 2,
      "average_price": 20.0
    }
  ]
}
```

**What to update:**

1. **`app/schemas.py`** – add `CategoryItemStats`; extend `ItemStatsResponse`
2. **`app/services.py`** – extend `ItemService.get_stats()` with a grouped SQLAlchemy query (`JOIN` + `GROUP BY`)
3. **`tests/test_items_stats.py`** – integration test with categories
4. **`tests/test_item_service.py`** – unit test for the service method

**TDD order:** write a failing test in `tests/test_items_stats.py`, then implement schema + service changes until green.

**Try it:**

1. Create categories and items (some with `category_id`, some without)
2. `GET /items/stats/summary` — confirm `by_category` and `uncategorized_count`
3. `pytest tests/test_items_stats.py -v`

---

## 21. Next Steps for Learning FastAPI

### 21.1 CategoryService unit tests

Add **`tests/test_category_service.py`** to test category business logic without the HTTP layer (mirrors `test_item_service.py`):

| Test | Covers |
|------|--------|
| `get_by_id` | Happy path and `CategoryNotFoundError` |
| `create` | Persist and `CategoryNameExistsError` |
| `update` | Partial update and duplicate name on rename |
| `delete` | Remove empty category and `CategoryInUseError` |
| `list_categories` | Pagination and total count |

Run: `pytest tests/test_category_service.py -v`

---

### 21.2 Pagination `meta` object (optional)

The app currently uses a **flat** paginated response (Step 20):

```json
{
  "items": [ ... ],
  "total": 42,
  "skip": 0,
  "limit": 10
}
```

An optional refactor — common in Laravel and many SPA APIs — nests pagination under **`meta`** and renames the list to **`data`**:

```json
{
  "data": [ ... ],
  "meta": {
    "total": 42,
    "skip": 0,
    "limit": 10,
    "current_page": 1,
    "last_page": 5
  }
}
```

| Laravel `paginate()` | This project (today) | Optional `meta` shape |
|----------------------|----------------------|------------------------|
| `data` | `items` | `data` |
| `meta.current_page`, `meta.last_page`, etc. | `total`, `skip`, `limit` at top level | `meta` object |

**Is it best practice?** It is a **widely used convention**, not a requirement. Flat `{ items, total, skip, limit }` is equally valid for a simple REST API. Choose `meta` if you want Laravel parity, a consistent envelope across list endpoints, or room to add `links` / page numbers later.

**When to skip it:** Low-traffic APIs, learning projects, or when clients already consume the flat shape.

**If you implement it later**, touch these files (no changes are made in the repo by default — this is documentation only):

1. **`app/schemas.py`** — shared `PaginationMeta` + generic or duplicated list wrappers (`data` + `meta`)
2. **`app/routers/items.py`** and **`app/routers/categories.py`** — build the new response shape
3. **`tests/test_items_list.py`**, **`tests/test_categories_list.py`** — assert `data` and `meta` keys

**Breaking change:** clients using `items` at the top level must switch to `data`. Update tests and README Step 20 examples together.

---

Further extensions now that filtering, categories, pagination metadata, extended item stats, service unit tests, JWT auth, rate limiting, and PostgreSQL are in place:

1. **[react-101](https://github.com/iammikek/react-101)** – React SPA frontend for this API (filters, pagination UI, JWT auth). See also [learning-101](https://github.com/iammikek/learning-101).
2. **Async SQLAlchemy** – Move to `async def` routes and `AsyncSession` for high concurrency.
3. **Pagination `meta` object** – Optional refactor to `{ "data": [...], "meta": { ... } }` (see [§21.2](#212-pagination-meta-object-optional)).

The official FastAPI docs are at [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) and match this style of app (async, type hints, automatic docs).

---

## 22. JWT authentication

This step replaces the static **API key** (Step 13) with **JWT Bearer tokens** for write endpoints. You'll add a `User` model, password hashing, login/register routes, and a `get_current_user` dependency — the FastAPI equivalent of Laravel Sanctum token auth.

| Laravel | FastAPI (this step) |
|---------|---------------------|
| `User` model + `Hash::make()` | `User` model + `bcrypt` in `security.py` |
| `Auth::attempt()` | `UserService.authenticate()` |
| Sanctum personal access token | JWT signed with `JWT_SECRET` |
| `Authorization: Bearer {token}` | `OAuth2PasswordBearer` + `get_current_user` |
| `auth:sanctum` middleware | `Depends(get_current_user)` on write routes |

Work through the files in order below. After each step, run tests or try the endpoint in `/docs`.

### 22.1 Add dependencies

Add to **`requirements.txt`**:

```
bcrypt==4.2.1
python-jose[cryptography]==3.3.0
python-multipart==0.0.20
```

- **`bcrypt`** – password hashing (never store plain passwords)
- **`python-jose`** – create and verify JWTs
- **`python-multipart`** – required for OAuth2 login form (`username` + `password`)

Install: `pip install -r requirements.txt`

### 22.2 Add JWT settings

Add to **`app/config.py`** and **`.env.example`**:

```python
jwt_secret: str = "change-me-in-production"
jwt_algorithm: str = "HS256"
jwt_expire_minutes: int = 60
```

Set a strong `JWT_SECRET` in production (like `APP_KEY` in Laravel).

### 22.3 Create `app/security.py`

New file for password hashing and JWT helpers:

- `hash_password()` / `verify_password()` – bcrypt
- `create_access_token(subject)` – encode JWT with `sub` = user email
- `decode_access_token(token)` – validate signature and expiry

### 22.4 Add the `User` model

Add to **`app/models.py`**:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
```

Create migration **`alembic/versions/003_add_users_table.py`**, then restart the app (migrations run on startup).

### 22.5 Add user schemas

Add to **`app/schemas.py`**:

- `UserCreate` – `email`, `password` (min 8 chars)
- `UserResponse` – `id`, `email` (never return password)
- `Token` – `access_token`, `token_type: "bearer"`

Add **`UserEmailExistsError`** to `app/exceptions.py` and a 409 handler in `app/main.py`.

### 22.6 Add `UserService`

Add to **`app/services.py`**:

| Method | Purpose |
|--------|---------|
| `get_by_email()` | Lookup for login and token validation |
| `create()` | Hash password, persist user |
| `authenticate()` | Verify email + password, return user or `None` |

### 22.7 Replace API key auth with JWT dependency

Rewrite **`app/auth.py`**:

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    # decode JWT → load user by email → raise 401 if invalid
```

On write routes in **`app/routers/items.py`** and **`app/routers/categories.py`**, replace:

```python
api_key: str = Depends(verify_api_key)
```

with:

```python
current_user: User = Depends(get_current_user)
```

GET routes stay public.

### 22.8 Create `app/routers/auth.py`

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/auth/register` | Create account (JSON body) |
| POST | `/auth/login` | OAuth2 form → JWT (`username` field = email) |
| GET | `/auth/me` | Current user profile (requires Bearer token) |

Register the router in **`app/main.py`**: `application.include_router(auth.router)`.

### 22.9 Update tests

**`tests/conftest.py`** – `auth_headers` fixture now:

1. `POST /auth/register`
2. `POST /auth/login` with form data
3. Returns `{"Authorization": "Bearer <token>"}`

Add **`tests/test_auth.py`** for register, login, duplicate email, and `/auth/me`.

Update existing tests that expected `"Invalid or missing API key"` — missing token now returns `"Not authenticated"` (OAuth2); invalid token returns `"Could not validate credentials"`.

Run: `pytest tests/ -v` (70 tests)

### 22.10 Try it in Swagger

1. `POST /auth/register` with `{ "email": "you@example.com", "password": "password123" }`
2. `POST /auth/login` — use **username** = email, **password** = your password
3. Copy `access_token` from the response
4. Click **Authorize** → paste `Bearer <token>` (or just the token; Swagger adds Bearer)
5. Try `POST /items` or `POST /categories`

**curl example:**

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"password123"}'

# Login (note: form-urlencoded, username = email)
curl -X POST http://localhost:8000/auth/login \
  -d "username=you@example.com&password=password123"

# Create item with token
curl -X POST http://localhost:8000/items \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Widget","price":9.99}'
```

---

## 23. Rate limiting

This step adds **IP-based rate limiting** with [slowapi](https://github.com/laurentS/slowapi) to protect auth and write endpoints from abuse (brute-force login, registration spam, write flooding).

| Laravel | FastAPI (this step) |
|---------|---------------------|
| `throttle:10,1` middleware | `@limiter.limit("10/minute")` on routes |
| `429 Too Many Requests` | `RateLimitExceeded` → custom 429 JSON |
| Per-user or per-IP | Per-IP via `get_remote_address` |

Work through the files in order below.

### 23.1 Add dependency

Add to **`requirements.txt`**:

```
slowapi==0.1.9
```

Install: `pip install -r requirements.txt`

### 23.2 Create `app/rate_limit.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

- **`get_remote_address`** – keys limits by client IP (from `request.client.host`)
- **In-memory storage** – fine for single-process dev; use Redis in multi-worker production

### 23.3 Wire into `app/main.py`

1. Attach limiter to app state: `application.state.limiter = limiter`
2. Add a **429** handler for `RateLimitExceeded`:

```json
{ "detail": "Rate limit exceeded", "code": "RATE_LIMIT_EXCEEDED" }
```

### 23.4 Apply limits to routes

slowapi requires `request: Request` in the route signature. Add `@limiter.limit(...)` above protected handlers:

| Endpoint group | Limit | Why |
|----------------|-------|-----|
| `POST /auth/register`, `POST /auth/login` | `10/minute` | Brute-force / registration spam |
| `POST`, `PATCH`, `DELETE` on items & categories | `60/minute` | Write flooding |

GET routes stay unlimited.

**Example:**

```python
@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), ...):
```

### 23.5 Tests

Most tests disable rate limiting via an autouse fixture in **`tests/conftest.py`** (`limiter.enabled = False`).

**`tests/test_rate_limit.py`** uses `@pytest.mark.rate_limit` to opt in and asserts **429** after exceeding limits:

- 11 login attempts → 429 on the 11th
- 11 registrations → 429 on the 11th
- 61 item creates → 429 on the 61st

Run: `pytest tests/test_rate_limit.py -v`

### 23.6 Try it

Restart the server after installing `slowapi`, then hammer an endpoint:

```bash
# 11 rapid login attempts — the 11th should return 429
for i in $(seq 1 11); do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/auth/login \
    -d "username=nobody@example.com&password=wrong"
done
```

Expect `401` for attempts 1–10, then `429`.

**Production note:** in-memory limits are per process. With multiple uvicorn workers or containers, use Redis-backed storage (`storage_uri="redis://..."`) so all workers share counters.

---

## 24. PostgreSQL

This step adds **PostgreSQL** for Docker-based development — production parity without changing your SQLAlchemy models or Alembic migrations. Local `uvicorn` keeps **SQLite** (zero setup); `docker compose up` uses **PostgreSQL** automatically.

| Laravel | FastAPI (this step) |
|---------|---------------------|
| `DB_CONNECTION=pgsql` in `.env` | `DATABASE_URL=postgresql+psycopg://...` |
| `php artisan migrate` | `alembic upgrade head` (runs on startup) |
| Separate MySQL/Postgres container | `db` service in `docker-compose.yml` |

### 24.1 Why two databases?

| Environment | Database | Why |
|-------------|----------|-----|
| Local Python (`uvicorn`) | SQLite (`app.db`) | No install, fast iteration |
| Docker Compose | PostgreSQL | Matches production; shared server process |
| Tests (pytest) | SQLite (`test.db`) | Fast, isolated, no Docker required |

Same **`app/models.py`** and **`alembic/versions/`** work on both — SQLAlchemy abstracts the engine.

### 24.2 Add the PostgreSQL driver

Add to **`requirements.txt`**:

```
psycopg[binary]==3.2.3
```

Use the **`postgresql+psycopg://`** URL scheme (psycopg v3 driver for SQLAlchemy 2.0).

Install: `pip install -r requirements.txt`

### 24.3 Update `docker-compose.yml`

Add a **`db`** service and point the API at it:

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: fastapi
      POSTGRES_PASSWORD: fastapi
      POSTGRES_DB: fastapi
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fastapi -d fastapi"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: .
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    command: sh -c "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
      - DATABASE_URL=postgresql+psycopg://fastapi:fastapi@db:5432/fastapi

volumes:
  postgres_data:
```

Key points:

- **`depends_on` + `healthcheck`** — API waits until Postgres accepts connections
- **`DATABASE_URL` in `environment`** — overrides `.env` SQLite URL when running in Docker
- **`postgres_data` volume** — data survives `docker compose down` (use `docker compose down -v` to wipe)

### 24.4 No model changes required

**`app/database.py`** already skips SQLite-only `check_same_thread` for non-SQLite URLs:

```python
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
```

Alembic reads `DATABASE_URL` from settings — the same migrations apply to both engines.

### 24.5 Start Docker

**Prerequisite:** Docker Desktop must be running. If you see:

```
Cannot connect to the Docker daemon at unix:///Users/mike/.docker/run/docker.sock.
```

Open **Docker Desktop** (`open -a Docker` on macOS) and wait until it reports **“Docker Desktop is running”**, then retry.

```bash
docker compose up --build
```

Stop local `uvicorn` first if it is already using port 8000.

### 24.6 Expected startup logs

A successful first run looks like this:

```
db-1  | ... LOG:  database system is ready to accept connections
Container fastapi-101-db-1 Healthy
api-1  | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
api-1  | INFO  [alembic.runtime.migration] Will assume transactional DDL.
api-1  | INFO  [alembic.runtime.migration] Running upgrade  -> 001, Create items table
api-1  | INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add categories table...
api-1  | INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, Add users table
api-1  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
api-1  | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
api-1  | ... INFO [app] Starting application
```

| Log line | Meaning |
|----------|---------|
| `database system is ready to accept connections` | PostgreSQL is up |
| `Container ... db ... Healthy` | API waited for DB before starting |
| `Context impl PostgresqlImpl` | Alembic is using **PostgreSQL** (not SQLite) |
| `Running upgrade -> 001, 002, 003` | Migrations applied on the Postgres database |
| `Uvicorn running on http://0.0.0.0:8000` | API is live at **http://localhost:8000** |
| `Starting application` | App lifespan finished (migrations + logging configured) |

On later runs you will **not** see `Running upgrade` again unless new migrations are added — that is normal.

### 24.7 Verify PostgreSQL

Work through these checks to confirm data is stored in Postgres.

**1. List tables in PostgreSQL**

```bash
docker compose exec db psql -U fastapi -d fastapi -c "\dt"
```

Expect `items`, `categories`, `users`, and `alembic_version`.

**2. Confirm the API container uses PostgreSQL**

```bash
docker compose exec api printenv DATABASE_URL
```

Expect: `postgresql+psycopg://fastapi:fastapi@db:5432/fastapi`

**3. Exercise the API (Swagger)**

1. Open **http://localhost:8000/docs**
2. `POST /auth/register` → `{ "email": "you@example.com", "password": "password123" }`
3. `POST /auth/login` → username = email, password = your password
4. **Authorize** with the Bearer token
5. `POST /items` → `{ "name": "Postgres Widget", "price": 9.99 }`

**4. Confirm rows in PostgreSQL**

```bash
docker compose exec db psql -U fastapi -d fastapi -c "SELECT id, email FROM users;"
docker compose exec db psql -U fastapi -d fastapi -c "SELECT id, name, price FROM items;"
```

You should see the user and item you just created.

**5. curl smoke test (optional)**

```bash
# Health check
curl -s http://localhost:8000/health

# Register
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"curl@example.com","password":"password123"}'

# Login and create an item (paste TOKEN from login response)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=curl@example.com&password=password123" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -X POST http://localhost:8000/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"curl item","price":5.00}'
```

Then re-run the `SELECT` queries — row counts should increase.

**6. Automated tests (still SQLite)**

pytest does **not** use Docker PostgreSQL. From the project root:

```bash
pytest tests/ -v
```

Expect **70 passed**. CI and local tests keep using `sqlite:///./test.db` for speed and simplicity.

**Local Python unchanged (SQLite):**

```bash
uvicorn main:app --reload   # still uses sqlite:///./app.db from .env
```

### 24.8 Tests stay on SQLite

**`conftest.py`** (project root) forces `DATABASE_URL=sqlite:///./test.db` before the app loads. CI and `pytest` do not need Docker or PostgreSQL — 70 tests run as before.

To test against PostgreSQL manually: set `DATABASE_URL` to the Docker URL and run `alembic upgrade head` before pytest (optional advanced exercise).

### 24.9 Production notes

- Use strong credentials and secrets management (not `fastapi:fastapi`)
- Managed Postgres (RDS, Supabase, Neon) — set `DATABASE_URL` to the cloud connection string
- Connection pooling (e.g. PgBouncer) at scale — out of scope for this learning project

---

## 25. Quick Reference

| Goal | Command |
|------|---------|
| Activate virtualenv | `source .venv/bin/activate` |
| Start app (Docker + PostgreSQL) | `docker compose up --build` |
| Start app (local + SQLite) | `source .venv/bin/activate && uvicorn main:app --reload` |
| Restart local server | **Ctrl+C**, then `uvicorn main:app --reload` |
| Stop Docker | `docker compose down` |
| Wipe PostgreSQL data | `docker compose down -v` |
| PostgreSQL shell | `docker compose exec db psql -U fastapi -d fastapi` |
| Port 8000 in use | Stop the other process (see [Without Docker](#without-docker-local-python)) |
| Start in background | `docker compose up --build -d` |
| Rebuild after changing Dockerfile/requirements | `docker compose up --build` |
| View logs | `docker compose logs -f` |
| Run migrations manually | `alembic upgrade head` (optional — app runs this on startup) |
| Run tests | `pytest tests/ -v --cov=app` |
| Run tests in Docker | `docker compose run --rm api sh -c "pip install -r requirements-dev.txt && pytest tests/ -v"` |
| Run linting locally | `ruff check . && ruff format --check .` |
| View CI runs | GitHub → Actions tab (parallel **Lint** and **Test** jobs) |

---

You've now seen how a minimal FastAPI app is structured, how dependencies are declared, how Docker and Docker Compose run it with PostgreSQL, how to add a persistent database (SQLite locally, PostgreSQL in Docker), tests, CI/CD, authentication (API key then JWT), rate limiting, production best practices, mature app structure, production layout with migrations, categories and filtering, pagination metadata, and service-layer tests. Use this as a reference while you work through the FastAPI docs and add more endpoints and features.

---

## 26. *-101 Family

Full family list, ports, and clone-with-submodules: **[learning-101](https://github.com/iammikek/learning-101)**. Site catalogue: [automica.io/learning-101](https://automica.io/learning-101.html).
