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

try:
    from hyper.parity_engine.dashboard import router as parity_dashboard_router
    app.include_router(parity_dashboard_router)
except Exception as e:
    logger.warning(f"Failed to load parity dashboard router: {e}")

try:
    from hyper.godmode.dashboard import router as godmode_dashboard_router
    app.include_router(godmode_dashboard_router)
except Exception as e:
    logger.warning(f"Failed to load godmode dashboard router: {e}")

try:
    from hyper.hyper100_parity.dashboard import router as hyper100_dashboard_router
    app.include_router(hyper100_dashboard_router)
except Exception as e:
    logger.warning(f"Failed to load hyper100 dashboard router: {e}")

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

router_specs = [
    ("backend.routers.orchestrate", "router", {}),
    ("backend.routers.policy", "router", {}),
    ("backend.routers.devops", "router", {}),
    ("backend.routers.system", "router", {}),
    ("backend.routers.v40_engines", "router", {"prefix": "/api/v1/v40/engines", "tags": ["V40 Engines"]}),
    ("backend.routers.prefetch", "router", {}),
    ("backend.routers.scoreboard", "router", {}),
    ("backend.routers.escape_engine_router", "router", {}),
    ("backend.routers.universal_router", "router", {}),
    ("backend.routers.discovery_router", "router", {}),
    ("backend.ira_router", "router", {}),
    ("backend.routers.ollama_chat", "router", {}),
    ("backend.routers.dream", "router", {}),
    ("backend.routers.hardware_boost", "router", {}),
    ("backend.routers.governor", "router", {}),
    ("backend.routers.contract_subsumption", "router", {}),
    ("backend.routers.caao", "router", {}),
    ("backend.routers.contract_engine_v1", "router", {}),
    ("backend.routers.cgfp", "router", {}),
    ("backend.routers.breakthrough_dashboard", "router", {}),
    ("backend.routers.cgace", "router", {}),
    ("backend.routers.hyper_v2_api", "router", {}),
    ("backend.routers.hyper_v3_api", "router", {}),
    ("backend.routers.hyper_mvc_dar_router", "router", {}),
    ("backend.routers.omega_router", "router", {}),
]

for mod_name, attr_name, kwargs in router_specs:
    try:
        import importlib
        mod = importlib.import_module(mod_name)
        r = getattr(mod, attr_name)
        app.include_router(r, **kwargs)
    except Exception as e:
        logger.warning(f"Optional router {mod_name} not loaded: {e}")

try:
    from backend.routers.pathway_router import router as pathway_router, parity_router
    app.include_router(pathway_router)
    app.include_router(parity_router)
except Exception as e:
    logger.warning(f"Optional pathway_router not loaded: {e}")

try:
    from hyper.hyper100_parity.dashboard import router as hyper100_router
    app.include_router(hyper100_router)
except Exception as e:
    logger.warning(f"Failed to load hyper100 parity dashboard router: {e}")

try:
    from backend.routers.hyper_escape_router import router as hyper_escape_router
    app.include_router(hyper_escape_router)
except Exception as e:
    logger.warning(f"Failed to load hyper_escape_router: {e}")

try:
    from hyper.parity_engine.dashboard import router as parity_engine_router
    app.include_router(parity_engine_router)
except Exception as e:
    logger.warning(f"Failed to load parity_engine_router: {e}")

try:
    from backend.routers.upe_router import router as upe_router
    app.include_router(upe_router)
except Exception as e:
    logger.warning(f"Failed to load upe_router: {e}")

try:
    from backend.routers.inference_router import router as inference_router
    app.include_router(inference_router)
except Exception as e:
    logger.warning(f"Failed to load inference_router: {e}")

try:
    from backend.routers.cpce_router import router as cpce_router
    app.include_router(cpce_router)
except Exception as e:
    logger.warning(f"Failed to load cpce_router: {e}")

try:
    from backend.routers.canonical_workload_router import router as canonical_workload_router
    app.include_router(canonical_workload_router)
except Exception as e:
    logger.warning(f"Failed to load canonical_workload_router: {e}")

try:
    from backend.routers.universal_fabric_router import router as universal_fabric_router
    app.include_router(universal_fabric_router)
    logger.info("Universal Replacement Fabric REST API mounted successfully at /api/hyper/*")
except Exception as e:
    logger.warning(f"Failed to load universal_fabric_router: {e}")




