"""
Simple API key authentication.
Uses a static API key from environment variable API_KEY (default: 'dev-key-123').
"""
import os

from fastapi import Header, HTTPException, status

API_KEY = os.getenv("API_KEY", "dev-key-123")


def verify_api_key(x_api_key: str | None = Header(None, description="API key for authentication")):
    """
    Dependency that verifies the API key from the X-API-Key header.
    Raises 401 if the key is missing or invalid.
    """
    if x_api_key is None or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
