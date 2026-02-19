# FastAPI + Docker Tutorial

A step-by-step guide to the project we set up: a minimal FastAPI app running in Docker with all dependencies managed for you. Use this document to understand what each piece does and how to run or extend the project.

---

## What We Built

1. **A minimal FastAPI application** (`main.py`) with root and health endpoints, plus an in-memory items API (added in Step 8)
2. **Dependency list** (`requirements.txt`) for Python packages
3. **A Docker image** (`Dockerfile`) that runs the app in a container
4. **Docker Compose** (`docker-compose.yml`) for one-command run with hot reload
5. **A `.dockerignore`** so unnecessary files stay out of the image
6. **A test framework** (pytest + FastAPI TestClient) for API tests (added in Step 9)

By the end, you can start the API with a single command and edit code while it reloads automatically.

---

## 1. Project Structure

```
first-fastapi/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile           # How to build the container image
├── docker-compose.yml   # How to run the container (with options)
├── .dockerignore        # Files to exclude from the Docker build
├── TUTORIAL.md          # This file
└── tests/               # Test package (Step 9)
    ├── __init__.py
    ├── conftest.py      # Pytest fixtures (e.g. reset items_db)
    └── test_main.py     # API tests with TestClient
```

---

## 2. Dependencies: `requirements.txt`

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

# Testing (TestClient uses httpx)
pytest==8.3.4
httpx==0.28.1
```

---

## 3. The FastAPI App: `main.py`

**What it is:** The actual web application. FastAPI uses this file and the `app` object to serve HTTP endpoints.

**Concepts used:**

- **`FastAPI()`** – Creates the app. We set `title`, `description`, and `version`; these show up in the auto-generated docs at `/docs`.
- **`@app.get("/")`** – Registers a function to handle `GET` requests to the root path.
- **Returning a dict** – FastAPI automatically converts it to JSON.

**Endpoints we defined:**

| Path | Method | Purpose |
|------|--------|--------|
| `/` | GET | Simple “hello” message |
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

## 4. The Dockerfile

**What it is:** Instructions for building a Docker *image*. The image is a snapshot of the OS, Python, dependencies, and your code. You then run that image as a *container*.

**Line by line:**

| Instruction | Meaning |
|-------------|--------|
| `FROM python:3.12-slim` | Start from the official Python 3.12 image; “slim” keeps the image smaller. |
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
COPY main.py .

# Expose port (uvicorn default)
EXPOSE 8000

# Run the app with uvicorn (host 0.0.0.0 so Docker can forward ports)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 5. Docker Compose: `docker-compose.yml`

**What it is:** A way to define and run your app (and optionally other services) with one command. It uses the Dockerfile to build the image and then runs the container with the options we want.

**What we configured:**

| Key | Meaning |
|-----|--------|
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

## 6. `.dockerignore`

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

## 7. How to Run Everything

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

Here you don’t get the volume mount or `--reload`; code changes require a rebuild and new container. Good for a quick test of the “production-style” image.

### Without Docker (local Python)

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Same app, same URLs. Useful if you want to debug or run without Docker.

---

## 8. Add an in-memory items list

This step adds a small “items” API so you can practice **path parameters**, **query parameters**, and **request bodies** with a Pydantic model. Data is kept in an in-memory list (no database); it resets whenever the app restarts.

### 8.1 Concepts you’ll use

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

- **`ItemCreate`** – Fields `name`, optional `description`, and `price`. FastAPI will reject requests whose body doesn’t match (e.g. missing `name` or wrong types).
- **`items_db`** – A list of dicts. Each item we “create” is appended here; we use the index as `id`.

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
3. **POST /items** – Click “Try it out”, use a body like:
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

## 9. Add a test framework

This step adds **pytest** and FastAPI’s **TestClient** so you can test your API without starting a server. Tests run in process and hit your routes like real HTTP requests.

### 9.1 What you’ll use

| Tool | Purpose |
|------|--------|
| **pytest** | Discovers and runs test functions; rich assertions and fixtures. |
| **TestClient** (from `fastapi.testclient`) | Calls your FastAPI app in process; same interface as `requests` (`.get()`, `.post()`, `.json()`, etc.). Requires **httpx** to be installed. |
| **conftest.py** | Pytest loads this automatically; we use it to reset `items_db` before each test so tests stay independent. |

### 9.2 Add pytest to dependencies

Add pytest and httpx to `requirements.txt` (TestClient depends on httpx under the hood):

```txt
# Testing (TestClient uses httpx)
pytest==8.3.4
httpx==0.28.1
```

Reinstall if needed: `pip install -r requirements.txt` (or rebuild the Docker image if you run tests inside the container).

### 9.3 Create the test package and fixture

Create a `tests` directory and an empty package so Python (and pytest) treat it as a package. Then add a fixture that clears the in-memory items list before (and after) each test so one test doesn’t affect another.

**Copy-paste: `tests/__init__.py`**

```python
# Tests package
```

**Copy-paste: `tests/conftest.py`**

```python
"""
Pytest fixtures shared across tests.
"""
import pytest

from main import items_db


@pytest.fixture(autouse=True)
def reset_items_db():
    """Clear the in-memory items list before each test so tests don't affect each other."""
    items_db.clear()
    yield
    items_db.clear()
```

- **`autouse=True`** – The fixture runs for every test in this package without having to name it.
- **`yield`** – Pytest runs the test between the code before and after `yield`; we clear again after the test for cleanliness.

### 9.4 Write API tests with TestClient

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
    assert data["id"] == 0
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
    client.post("/items", json={"name": "Widget", "description": None, "price": 9.99})
    response = client.get("/items/0")
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

### 9.5 Run the tests

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

### 9.6 What to try next

- Add a test for **PUT** or **DELETE** when you add those endpoints.
- Use **`response.raise_for_status()`** if you expect success and want a clear error when the status is 4xx/5xx.
- Use **pytest parametrize** to test several inputs in one test: `@pytest.mark.parametrize("item_id", [0, 1, 2])`.

---

## 10. Next Steps for Learning FastAPI

Now that you have path params, query params, request bodies, and tests in place, you can extend the app further:

1. **PUT or PATCH /items/{item_id}** – Update an item (body with optional fields).
2. **DELETE /items/{item_id}** – Remove an item from `items_db`.
3. **Filtering** – Add query params like `min_price` or `name_contains` in `list_items`.
4. **Database** – Replace `items_db` with SQLite (e.g. `sqlite3`) or an ORM to persist data.

The official FastAPI docs are at [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) and match this style of app (async, type hints, automatic docs).

---

## 11. Quick Reference

| Goal | Command |
|------|--------|
| Start app (with reload) | `docker compose up --build` |
| Start in background | `docker compose up --build -d` |
| Stop background app | `docker compose down` |
| Rebuild after changing Dockerfile/requirements | `docker compose up --build` |
| View logs | `docker compose logs -f` |
| Run locally (no Docker) | `uvicorn main:app --reload` |
| Run tests | `pytest tests/ -v` |
| Run tests in Docker | `docker compose run --rm api pytest tests/ -v` |

---

You’ve now seen how a minimal FastAPI app is structured, how dependencies are declared, how Docker and Docker Compose run it, and how to iterate on the code. Use this as a reference while you work through the FastAPI docs and add more endpoints and features.
