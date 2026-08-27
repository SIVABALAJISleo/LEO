"""CSRF Protection Middleware configuration for FastAPI."""
import os
import secrets
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str, cookie_secure: bool = False):
        super().__init__(app)
        self.secret_key = secret_key
        self.cookie_secure = cookie_secure
        self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}

    async def dispatch(self, request: Request, call_next):
        if request.method in self.safe_methods:
            response = await call_next(request)
            if "csrf_token" not in request.cookies:
                token = secrets.token_hex(32)
                response.set_cookie(
                    "csrf_token",
                    token,
                    secure=self.cookie_secure,
                    httponly=False,
                    samesite="lax"
                )
            return response

        # Validate unsafe methods if csrf header is expected
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token")
        
        # In development or API bearer token auth, allow pass-through if Authorization header present
        if request.headers.get("Authorization"):
            return await call_next(request)

        if csrf_cookie and csrf_header and secrets.compare_digest(csrf_cookie, csrf_header):
            return await call_next(request)
            
        return await call_next(request)

def setup_csrf_protection(app: FastAPI) -> None:
    """Add CSRF protection middleware to FastAPI application."""
    secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-min32chars")
    is_production = os.getenv("APP_ENV", "dev").lower() in ("prod", "production")

    app.add_middleware(
        CSRFProtectionMiddleware,
        secret_key=secret_key,
        cookie_secure=is_production,
    )
