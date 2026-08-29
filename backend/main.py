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


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from backend.security.middlewares import SecurityHeadersMiddleware, PayloadSizeLimitMiddleware, GlobalRateLimitMiddleware
# Middlewares execute in reverse order of addition; CORSMiddleware must be added LAST to be outermost
app.add_middleware(PayloadSizeLimitMiddleware, max_upload_size=5 * 1024 * 1024)
app.add_middleware(GlobalRateLimitMiddleware, max_requests=600, window_seconds=60)
app.add_middleware(SecurityHeadersMiddleware)

# Outermost CORS layer allows all localhost and tunnel origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:8080", "http://localhost:8000"],
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


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

from backend.routers.hardware_boost import router as hardware_boost_router
app.include_router(hardware_boost_router)

from backend.routers.governor import router as governor_router
app.include_router(governor_router)

from backend.routers.contract_subsumption import router as contract_subsumption_router
app.include_router(contract_subsumption_router)

from backend.routers.caao import router as caao_router
app.include_router(caao_router)

from backend.routers.contract_engine_v1 import router as contract_v1_router
app.include_router(contract_v1_router)





