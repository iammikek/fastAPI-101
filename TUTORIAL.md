# FastAPI + Docker Tutorial

A step-by-step guide to the project we set up: a minimal FastAPI app running in Docker with all dependencies managed for you. Use this document to understand what each piece does and how to run or extend the project.

---

## What We Built

1. **A minimal FastAPI application** (`main.py`) with two endpoints
2. **Dependency list** (`requirements.txt`) for Python packages
3. **A Docker image** (`Dockerfile`) that runs the app in a container
4. **Docker Compose** (`docker-compose.yml`) for one-command run with hot reload
5. **A `.dockerignore`** so unnecessary files stay out of the image

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
└── TUTORIAL.md          # This file
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

## 8. Next Steps for Learning FastAPI

Now that the environment is ready, you can practice with small changes:

1. **Add a new route** – In `main.py`, add another `@app.get("/something")` and return a dict or string. Save and see it at http://localhost:8000/something (and in `/docs`).
2. **Path parameters** – Use `@app.get("/items/{item_id}")` and a function like `def get_item(item_id: int)`. FastAPI will parse and validate `item_id`.
3. **Query parameters** – Add optional args like `skip: int = 0` and `limit: int = 10` to your function; they appear as query params in the docs and in the URL.
4. **Request body** – Define a Pydantic model and use it as a parameter (e.g. `item: Item`); FastAPI will read JSON from the body and validate it.
5. **Different methods** – Use `@app.post("/items")`, `@app.put("/items/{id}")`, `@app.delete("/items/{id}")` and implement create/update/delete logic.

The official FastAPI docs are at [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) and match this style of app (async, type hints, automatic docs).

---

## 9. Quick Reference

| Goal | Command |
|------|--------|
| Start app (with reload) | `docker compose up --build` |
| Start in background | `docker compose up --build -d` |
| Stop background app | `docker compose down` |
| Rebuild after changing Dockerfile/requirements | `docker compose up --build` |
| View logs | `docker compose logs -f` |
| Run locally (no Docker) | `uvicorn main:app --reload` |

---

You’ve now seen how a minimal FastAPI app is structured, how dependencies are declared, how Docker and Docker Compose run it, and how to iterate on the code. Use this as a reference while you work through the FastAPI docs and add more endpoints and features.
