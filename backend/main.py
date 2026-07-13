"""
backend/main.py
LEO: Production-Grade Semantic Compute Orchestration API
"""
import logging
import os
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
from backend.observability.telemetry import TelemetryInstrumentor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LEO AI V43 – Software-First Intelligence Platform",
    description="Intelligence-per-Watt · Local-First · CPU+iGPU Optimised · 20-Layer Architecture",
    version="43.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
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

# Register drop-in OpenAI-compatible router and Prometheus telemetry instrumentation
app.include_router(openai_router)
TelemetryInstrumentor.instrument_app(app)

# Include Routers
from backend.routers.benchmark import router as benchmark_router
app.include_router(benchmark_router)

from backend.routers.systems import router as systems_router
app.include_router(systems_router)

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
