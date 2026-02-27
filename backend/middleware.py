import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("HYPER-Middleware")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60, window: int = 60):
        super().__init__(app)
        self.limit = limit # requests per window
        self.window = window # window in seconds
        self.requests = {} # ip -> [timestamps]

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host
        now = time.time()
        
        # Initialize or clean up old timestamps
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove timestamps older than the window
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window]
        
        if len(self.requests[client_ip]) >= self.limit:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
            
        self.requests[client_ip].append(now)
        return await call_next(request)
