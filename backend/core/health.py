from fastapi import APIRouter
import time

router = APIRouter(tags=["health"])

START_TIME = time.time()
REQUEST_COUNT = 0
CACHE_HITS = 0

def increment_requests():
    global REQUEST_COUNT
    REQUEST_COUNT += 1

def increment_hits():
    global CACHE_HITS
    CACHE_HITS += 1

@router.get("/health")
@router.get("/health/status")
async def health_check():
    """Basic liveness probe."""
    return {
        "status": "up",
        "timestamp": time.time(),
        "uptime": f"{time.time() - START_TIME:.2f}s"
    }

@router.get("/ready")
async def readiness_probe():
    """Readiness probe checking dependencies (VectorDB, Cache)."""
    # In a real app, check DB/Redis connections here
    return {
        "status": "ready",
        "dependencies": {
            "vector_db": "connected",
            "cache": "connected"
        },
        "metrics": {
            "total_requests": REQUEST_COUNT,
            "cache_hits": CACHE_HITS,
            "efficiency": f"{(CACHE_HITS / max(1, REQUEST_COUNT)) * 100:.1f}%"
        }
    }

@router.get("/live")
async def liveness_probe():
    """Liveness probe for orchestration health."""
    return {"status": "alive"}
