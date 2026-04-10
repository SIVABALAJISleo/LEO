import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from backend.core.database import SessionLocal, UsageMetric
from backend.core.logging import logger

class UsageMeteringMiddleware(BaseHTTPMiddleware):
    """
    SaaS Business Layer:
    Tracks usage metrics (requests) per tenant/user in the durable data layer.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Track successful business logic requests
        if response.status_code == 200 and request.url.path.startswith("/api/v1/"):
            # The token dependency in FastAPI populates request.state.user if we set it
            # For simplicity, we assume relevant metadata is attached to the request state
            user_data = getattr(request.state, "user", None)
            if user_data:
                from backend.core.database import SessionLocal
                db = SessionLocal()
                try:
                    record_usage(
                        db, 
                        user_data.get("tenant_id", "default"), 
                        user_data.get("uid", "unknown"), 
                        "request"
                    )
                finally:
                    db.close()

        return response

from backend.core.limits import TIER_LIMITS
import datetime

def check_subscription_limits(db, tenant_id: str, user_id: str, tier: str = "free") -> bool:
    """
    Enforces SaaS subscription limits by checking daily request volume.
    """
    limits = TIER_LIMITS.get(tier, TIER_LIMITS["free"])
    max_reqs = limits["requests_per_day"]
    
    # Count requests for today
    today = datetime.datetime.utcnow().date()
    count = db.query(UsageMetric).filter(
        UsageMetric.tenant_id == tenant_id,
        UsageMetric.metric_type == "request",
        UsageMetric.timestamp >= today
    ).count()
    
    if count >= max_reqs:
        logger.warning("subscription_limit_exceeded", tenant_id=tenant_id, tier=tier, count=count)
        return False
        
    return True

def record_usage(db, tenant_id: str, user_id: str, metric_type: str, value: int = 1):
    """Utility to persist usage spikes for billing/metering."""
    try:
        metric = UsageMetric(
            user_id=user_id,
            tenant_id=tenant_id,
            metric_type=metric_type,
            value=value
        )
        db.add(metric)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("usage_recording_failed", error=str(e), tenant_id=tenant_id)

def record_ai_usage(db, tenant_id: str, user_id: str, tokens: int, latency_ms: int):
    """Specialized helper for AI cost metering."""
    record_usage(db, tenant_id, user_id, "tokens", tokens)
    record_usage(db, tenant_id, user_id, "latency", latency_ms)
