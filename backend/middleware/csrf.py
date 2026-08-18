"""CSRF Protection Middleware configuration for FastAPI."""
import os
from fastapi import FastAPI
from starlette.middleware.csrf import CSRFMiddleware


def setup_csrf_protection(app: FastAPI) -> None:
    """Add CSRF protection middleware to FastAPI application."""
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-min32chars")
    is_production = os.getenv("APP_ENV", "dev").lower() in ("prod", "production")

    app.add_middleware(
        CSRFMiddleware,
        secret_key=secret_key,
        cookie_secure=is_production,
        cookie_httponly=True,
        cookie_samesite="strict",
    )
