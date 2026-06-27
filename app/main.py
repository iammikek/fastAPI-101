"""
FastAPI application factory.
Run with: uvicorn main:app --reload
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.exceptions import ItemNotFoundError
from app.routers import health, items

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
    """Application startup and shutdown."""
    configure_logging()
    logger.info("Starting application")
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    application = FastAPI(
        title="First FastAPI",
        description="A simple API to learn FastAPI basics",
        version="0.1.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.middleware("http")
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

    @application.exception_handler(ItemNotFoundError)
    async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
        """Return consistent 404 for missing items."""
        return JSONResponse(
            status_code=404,
            content={"detail": "Item not found", "code": "ITEM_NOT_FOUND"},
        )

    @application.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError):
        """Return consistent 500 for database errors."""
        logger.exception("Database error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Database error", "code": "DB_ERROR"},
        )

    application.include_router(health.router)
    application.include_router(items.router)
    return application


app = create_app()
