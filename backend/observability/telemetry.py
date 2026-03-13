import logging
import json
import time
import uuid
from typing import Any, Dict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class StructuredLogger:
    def __init__(self, name: str = "hyper_saas"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)

    def info(self, message: str, extra: Dict[str, Any] = None):
        log_data = {
            "timestamp": time.time(),
            "level": "INFO",
            "message": message,
            ** (extra or {})
        }
        self.logger.info(json.dumps(log_data))

    def error(self, message: str, extra: Dict[str, Any] = None):
        log_data = {
            "timestamp": time.time(),
            "level": "ERROR",
            "message": message,
            ** (extra or {})
        }
        self.logger.error(json.dumps(log_data))

logger = StructuredLogger()

class TelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.perf_counter()
        
        logger.info(f"Incoming request", {
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id
        })
        
        response = await call_next(request)
        
        duration = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        
        logger.info(f"Request completed", {
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
            "request_id": request_id
        })
        
        return response
