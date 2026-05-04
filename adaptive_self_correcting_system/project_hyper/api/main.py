from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import time
from .schemas.contracts import QueryRequest, QueryResponse
from .metrics.telemetry import track_latency, track_path
from .router.adaptive_router import adaptive_router
from .orchestrator import leo_orchestrator

app = FastAPI(title="PROJECT HYPER: CPU-First Intelligence Core")

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "HYPER-v56-CPU"}

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    start_time = time.time()
    
    # Adaptive Router decides the path
    # Orchestrator handles the execution
    async def response_stream():
        async for token in leo_orchestrator.stream_response(request):
            yield token

    latency = (time.time() - start_time) * 1000
    track_latency(latency)
    return StreamingResponse(response_stream(), media_type="text/event-stream")

@app.get("/metrics")
async def metrics():
    from .metrics.telemetry import get_metrics
    return get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

