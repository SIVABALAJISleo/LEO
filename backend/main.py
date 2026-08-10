"""
backend/main.py
LEO: Production-Grade Semantic Compute Orchestration API
"""
import logging
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.core.database import init_db

# Initialize SQLite database schema on start
init_db()

# Import OpenAI drop-in gateway and Telemetry instrumentor
from backend.gateway.openai_gateway import router as openai_router
from backend.routers.memory import router as memory_router
from backend.observability.telemetry import TelemetryInstrumentor
from backend.api_v2_bypass import router as bypass_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LEO AI V43 – Software-First Intelligence Platform",
    description="Intelligence-per-Watt · Local-First · CPU+iGPU Optimised · 20-Layer Architecture",
    version="43.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
# In development, accept all origins so Cloudflare/ngrok tunnel URLs work.
# In production, set ALLOWED_ORIGINS to a comma-separated list of allowed domains.
if _raw_origins.strip():
    _allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
else:
    # Default: allow local dev hosts and any HTTPS tunnel (wildcard for *.trycloudflare.com, *.ngrok-free.app, etc.)
    _allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=_allowed_origins != ["*"],  # credentials not compatible with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from backend.security.middlewares import SecurityHeadersMiddleware, PayloadSizeLimitMiddleware, GlobalRateLimitMiddleware
# Note: Middlewares are executed in reverse order of addition
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(PayloadSizeLimitMiddleware, max_upload_size=5 * 1024 * 1024)
app.add_middleware(GlobalRateLimitMiddleware, max_requests=600, window_seconds=60)

app.include_router(bypass_router)

# Register drop-in OpenAI-compatible router and Prometheus telemetry instrumentation
app.include_router(openai_router)
app.include_router(memory_router)
TelemetryInstrumentor.instrument_app(app)

from backend.core.health import router as health_router
app.include_router(health_router)

from backend.routers.auth import router as auth_router
app.include_router(auth_router)

# Include Routers
from backend.routers.benchmark import router as benchmark_router
app.include_router(benchmark_router)

from backend.routers.systems import router as systems_router
app.include_router(systems_router)

# Compatibility router for TestMemoryAPI endpoints in tests
from fastapi import APIRouter
compat_router = APIRouter(prefix="/api/v1/systems", tags=["Systems Compat"])

@compat_router.post("/memory/store")
async def compat_memory_store(req: dict):
    from backend.core.memory_system import global_memory_system
    content = f"{req.get('key')}: {req.get('value')}"
    memory_id, was_new = global_memory_system.store(
        content=content,
        memory_type="semantic",
        confidence=0.9
    )
    return {"memory_id": memory_id, "was_new": was_new}

@compat_router.get("/memory/summary")
async def compat_memory_summary():
    from backend.core.memory_system import global_memory_system
    return global_memory_system.get_summary()

app.include_router(compat_router)

from backend.routers.orchestrate import router as orchestrate_router
app.include_router(orchestrate_router)

from backend.routers.policy import router as policy_router
app.include_router(policy_router)

from backend.routers.devops import router as devops_router
app.include_router(devops_router)

from backend.routers.system import router as system_router
app.include_router(system_router)

from backend.routers.v40_engines import router as v40_engines_router
app.include_router(v40_engines_router, prefix="/api/v1/v40/engines", tags=["V40 Engines"])

from backend.routers.prefetch import router as prefetch_router
app.include_router(prefetch_router)

from backend.routers.scoreboard import router as scoreboard_router
app.include_router(scoreboard_router)

from backend.ira_router import router as ira_router
app.include_router(ira_router)

from backend.routers.ollama_chat import router as ollama_router
app.include_router(ollama_router)

from backend.routers.dream import router as dream_router
app.include_router(dream_router)
