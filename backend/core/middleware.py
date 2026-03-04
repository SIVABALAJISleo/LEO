import os
import time
import logging
from redis import Redis
from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

# Basic Redis client configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    logger.error(f"Failed to connect to Redis for Rate Limiting: {e}")
    redis_client = None

def get_user_tier(user_id: str) -> str:
    """
    Mock checking the database for the user's Stripe tier.
    In a real system, this would query Postgres or Firestore.
    """
    if not redis_client:
        return "free"
        
    tier = redis_client.get(f"user:{user_id}:tier")
    return tier if tier else "free"

def get_tier_limits(tier: str) -> dict:
    if tier == "enterprise":
        return {"rpm": 1000, "daily_tokens": 1000000}
    elif tier == "pro":
        return {"rpm": 100, "daily_tokens": 50000}
    else: # free
        return {"rpm": 10,  "daily_tokens": 5000}

async def limit_and_quota_check(request: Request):
    """
    FastAPI Dependency to check both RPM (Rate Limiting) and Quotas (Tokens).
    """
    if not redis_client:
        # Fail open if Redis is down, or fail closed in strict environments
        return True

    # We assume token is verified earlier and injected or parsed from headers
    user_id = getattr(request.state, "user_id", "anonymous")
    client_ip = request.client.host if request.client else "unknown_ip"
    
    # 0. Global Anonymous IP Throttling (Defense against DDoS)
    ip_rate_key = f"ip_rate:{client_ip}:{int(time.time() / 60)}"
    ip_reqs = redis_client.incr(ip_rate_key)
    if ip_reqs == 1:
        redis_client.expire(ip_rate_key, 60)
        
    if ip_reqs > 300: # Strict 300 requests per minute per IP maximum
        logger.warning(f"DDoS Protection: Blocked IP {client_ip}")
        raise HTTPException(status_code=429, detail="Global IP rate limit exceeded.")

    tier = get_user_tier(user_id)
    limits = get_tier_limits(tier)
    
    # 1. Rate Limiting (Token Bucket / Sliding Window approximation)
    current_minute = int(time.time() / 60)
    rate_key = f"rate_limit:{user_id}:{current_minute}"
    
    current_requests = redis_client.incr(rate_key)
    if current_requests == 1:
        redis_client.expire(rate_key, 60) # Expire key after 1 minute

    if current_requests > limits["rpm"]:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {tier} tier ({limits['rpm']} RPM)."
        )

    # 2. Daily Quota Check
    current_day = int(time.time() / 86400)
    quota_key = f"quota:{user_id}:{current_day}"
    
    current_usage = redis_client.get(quota_key)
    current_usage = int(current_usage) if current_usage else 0
    
    if current_usage >= limits["daily_tokens"]:
        raise HTTPException(
            status_code=402,
            detail=f"Daily compute quota exhausted for {tier} tier. Upgrade your plan."
        )

    # Increment quota by an estimated token amount per request
    redis_client.incrby(quota_key, 500)
    if current_usage == 0:
        redis_client.expire(quota_key, 86400) # Expire at end of day

    return True
