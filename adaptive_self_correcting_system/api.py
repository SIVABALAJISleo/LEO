from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .core.orchestrator import CascadeOrchestrator
from .models.schemas import CascadeResponse

app = FastAPI(title="LEO CASCADE AI SYSTEM (CPU-FIRST)")
orchestrator = CascadeOrchestrator()

class Request(BaseModel):
    prompt: str

@app.post("/v1/generate", response_model=CascadeResponse)
async def generate(request: Request):
    try:
        # Pipeline handles all cascade layers (Cache -> RAG -> Tiny -> Med -> Heavy)
        result = await orchestrator.run(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
吐
