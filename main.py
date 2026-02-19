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
