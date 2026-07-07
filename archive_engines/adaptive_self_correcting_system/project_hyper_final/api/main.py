from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from .schemas.contracts import QueryRequest
from .backend.orchestrator import orchestrator
from .metrics.telemetry import telemetry

app = FastAPI(title="PROJECT HYPER vFinal: Elite CPU-First Intelligence")

@app.get("/health")
async def health():
    return {"status": "operational", "version": "HYPER-vFinal"}

@app.post("/query")
async def query(request: QueryRequest):
    async def stream():
        async for token in orchestrator.process(request):
            yield token
    
    return StreamingResponse(stream(), media_type="text/plain")

@app.get("/metrics")
async def metrics():
    return telemetry.get_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

