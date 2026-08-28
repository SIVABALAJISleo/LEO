from fastapi import FastAPI
from .core.router import leo_orchestrator
from .schemas.contracts import QueryRequest, LeoPerceivedResponse

app = FastAPI(title="PROJECT HYPER — PERCEIVED 100% ENGINE")

@app.post("/v1/resolve", response_model=LeoPerceivedResponse)
async def resolve(request: QueryRequest):
    # Guaranteed to return useful output, never failure
    return leo_orchestrator.execute(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

