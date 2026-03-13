from fastapi import FastAPI, Request
import time
from app.core.config import settings
from app.core.orchestrator import orchestrator

app = FastAPI(title=settings.PROJECT_NAME)

# Middleware to track computation stats and time
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root():
    return {"message": "Compute-Avoidance Intelligence System Active"}

@app.post("/api/v1/orchestrate")
async def orchestrate(payload: dict):
    """
    Main entry point for all intelligence requests.
    Routes to the appropriate module based on intent.
    """
    query = payload.get("query")
    if not query:
        return {"error": "Missing query"}
    
    result = await orchestrator.route(query)
    return result

@app.get("/api/v1/metrics")
async def get_metrics():
    """
    Returns system-wide compute-avoidance metrics.
    """
    return orchestrator.get_metrics()
