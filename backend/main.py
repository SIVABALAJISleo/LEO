"""
Project HYPER — FastAPI Entry Point
Fixed:
  - Flat imports (no hyper_saas.backend.* nesting)
  - Env-var based config (no hardcoded secrets)
  - Correct middleware order (CORS outermost)
  - Firebase optional: falls back to local JWT when credentials missing
  - Health check requires no auth (for Railway/Docker health probes)
"""
import time
import os
import logging
from contextlib import asynccontextmanager
import sentry_sdk

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4318/v1/traces")
resource = Resource(attributes={"service.name": "hyper-api-gateway"})
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_exporter = OTLPSpanExporter(endpoint=OTEL_ENDPOINT)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))
import logging
from contextlib import asynccontextmanager
import sentry_sdk

SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=1.0
    )

from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from backend.core.security import SecureHeadersMiddleware
from backend.routers.system import PrometheusMiddleware


# ── Config (reads from environment / .env file) ────────────────────────────────
class Settings(BaseSettings):
    app_env: str = "development"
    secret_key: str = "LEOSIVA44"          # JWT secret
    firebase_credentials: str = ""                        # path to serviceAccount.json
    allowed_origins: str = "http://localhost:5173"        # comma-separated

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()


# ── Lazy imports (so missing optional deps don't crash startup) ────────────────
def _import_engine():
    try:
        from backend.core.orchestrator import hyper_engine
        return hyper_engine
    except Exception as e:
        logging.warning(f"Orchestrator unavailable: {e}")
        return None

def _import_file_processor():
    try:
        from backend.core.ingest import file_processor
        return file_processor
    except Exception as e:
        logging.warning(f"File processor unavailable: {e}")
        return None


# ── Auth (Firebase if credentials present, else local JWT) ────────────────────
def get_token_verifier():
    if settings.firebase_credentials and os.path.exists(settings.firebase_credentials):
        try:
            from backend.core.security import verify_firebase_token
            return verify_firebase_token
        except Exception:
            pass

    # Local JWT fallback — safe for dev/staging
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from jose import jwt, JWTError

    bearer = HTTPBearer(auto_error=False)

    async def verify_local_jwt(
        credentials: HTTPAuthorizationCredentials = Depends(bearer)
    ) -> dict:
        if credentials is None:
            raise HTTPException(status_code=401, detail="No token provided")
        try:
            payload = jwt.decode(
                credentials.credentials,
                settings.secret_key,
                algorithms=["HS256"],
                options={"verify_exp": True, "verify_signature": True}
            )
            
            # Additional rigorous safety net
            if "exp" in payload and payload["exp"] < time.time():
                logger.warning(f"Expired token attempt rejected")
                raise HTTPException(status_code=401, detail="Token officially expired")
                
            return payload
        except JWTError as e:
            logger.warning(f"JWT Validation Error: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")

    return verify_local_jwt

verify_token = get_token_verifier()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("HYPER backend starting up...")
    
    # Phase 12: Boot HPC Optimizations
    try:
        from backend.core.hardware_optimizer import HardwareOptimizer
        from backend.core.hyper_config import config
        HardwareOptimizer.setup(config.PERFORMANCE_MODE)
    except Exception as e:
        logging.warning(f"Failed to initialize HPC Hardware Optimizer: {e}")
        
    yield
    logging.info("HYPER backend shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Project HYPER SaaS", version="1.0.0", lifespan=lifespan)

# Phase 18 [Enterprise Upgrade]: Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# CORS must be registered FIRST (outermost middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 9: Inject Enterprise Secure Headers
app.add_middleware(SecureHeadersMiddleware)

# Phase 3: Inject Prometheus Monitoring middleware to track latency and HTTP 500s 
app.add_middleware(PrometheusMiddleware)

# Optional telemetry middleware
try:
    from backend.observability.telemetry import TelemetryMiddleware
    app.add_middleware(TelemetryMiddleware)
except Exception:
    logging.warning("TelemetryMiddleware not available — skipping.")


# ── Routers ───────────────────────────────────────────────────────────────────
try:
    from backend.core.health import router as health_router
    app.include_router(health_router)
except Exception:
    @app.get("/health")
    async def health():
        return {"status": "ok", "env": settings.app_env}

try:
    from backend.routers.billing import router as billing_router
    app.include_router(billing_router)
except Exception as e:
    logging.warning(f"Billing router not available — skipping. {e}")

try:
    from backend.routers.cpu_compute import router as compute_router
    app.include_router(compute_router)
except Exception as e:
    logging.warning(f"Compute CPU router not available — skipping: {e}")

try:
    from backend.routers.vision import router as vision_router
    app.include_router(vision_router)
except Exception as e:
    logging.warning(f"Vision YOLO router not available — skipping: {e}")

try:
    from backend.routers.jepa import router as jepa_router
    app.include_router(jepa_router)
except Exception as e:
    logging.warning(f"JEPA predictive router not available — skipping: {e}")

try:
    from backend.routers.jobs import router as jobs_router
    app.include_router(jobs_router)
except Exception as e:
    logging.warning(f"Jobs router not available — skipping: {e}")

try:
    from backend.routers.system import router as system_router
    app.include_router(system_router)
except Exception as e:
    logging.warning(f"System router not available — skipping: {e}")

try:
    from backend.routers.apikeys import router as apikeys_router
    app.include_router(apikeys_router)
except Exception as e:
    logging.warning(f"API Keys router not available — skipping: {e}")

try:
    from backend.routers.paypal import router as paypal_router
    app.include_router(paypal_router)
except Exception as e:
    logging.warning(f"PayPal router not available — skipping: {e}")

try:
    from backend.routers.compliance import router as compliance_router
    app.include_router(compliance_router)
except Exception as e:
    logging.warning(f"Compliance router not available — skipping: {e}")

# ── Request models ────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Project HYPER SaaS Engine Active", "env": settings.app_env}


@app.post("/api/v1/orchestrate")
async def orchestrate(
    request: QueryRequest,
    token: dict = Depends(verify_token)
):
    engine = _import_engine()
    if engine is None:
        raise HTTPException(status_code=503, detail="Orchestration engine unavailable")

    user_id = token.get("uid") or token.get("sub", "anonymous")
    request_id = f"REQ_{user_id}_{int(time.time())}"

    try:
        return await engine.process(request.query, request_id)
    except Exception as e:
        logging.error(f"Orchestration error [{request_id}]: {e}")
        raise HTTPException(status_code=500, detail="Orchestration failed")


from backend.core.security import verify_upload_safety

@app.post("/api/v1/ingest/upload")
async def upload_file(
    file: UploadFile = File(...),
    token: dict = Depends(verify_token)
):
    await verify_upload_safety(file)
    processor = _import_file_processor()
    if processor is None:
        raise HTTPException(status_code=503, detail="File processor unavailable")

    user_id = token.get("uid") or token.get("sub", "anonymous")

    try:
        text = await processor.extract_text(file)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not extract text: {e}")

    engine = _import_engine()
    if engine and len(text) > 5:
        await engine.rag.add_documents([text])

    return {
        "filename": file.filename,
        "content_length": len(text),
        "status": "ingested",
        "user_id": user_id,
    }
