"""
Simple API key authentication.
Uses a static API key from environment variable API_KEY (default: 'dev-key-123').
"""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(x_api_key: str | None = Depends(api_key_header)):
    """
    Dependency that verifies the API key from the X-API-Key header.
    Raises 401 if the key is missing or invalid.
    """
    api_key = get_settings().api_key
    if x_api_key is None or not secrets.compare_digest(x_api_key, api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
