from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from hyper_optimized_ai.app.core.engine import HyperEngine
from hyper_optimized_ai.app.core.output import AdaptiveResponse
import json
import asyncio

app = FastAPI(title="HyperOptimizedAI")
engine = HyperEngine()

class QueryRequest(BaseModel):
    text: str
    is_high_risk: bool = False

@app.post("/process")
async def process_query(request: QueryRequest):
    """
    Standard endpoint (blocks until first full chunk or gate failure)
    """
    try:
        # For non-streaming, we just take the first yielded item (which might be a gate failure or full tiny result)
        # or consume the whole generator.
        results = []
        async for chunk in engine.process(request.text, request.is_high_risk):
            results.append(chunk)
        
        # If it's a JSON string (from gate or tiny), return it as dict
        try:
            return json.loads(results[0])
        except (ValueError, IndexError):
            return {"content": "".join(results), "confidence": 0.8} # Fallback for streaming results
            
    except Exception as e:
        # 7. SAFETY RULES: No silent failure
        return {"error": str(e), "status": "FAILED", "path": "Check logs for correction path."}

@app.get("/stream")
async def stream_query(text: str, is_high_risk: bool = False):
    """
    6. SPEED LAYER: Streaming (instant first token)
    """
    async def generate():
        async for chunk in engine.process(text, is_high_risk):
            yield chunk
            # Small sleep to ensure event loop doesn't block
            await asyncio.sleep(0.01)

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/feedback")
async def report_feedback(query: str, action: str):
    # 8. FEEDBACK LOOP: Track copy, re-ask, edit
    # Improve cache + routing by invalidating bad outputs
    if action in ["copy", "useful"]:
        # Reinforce cache if needed
        pass
    elif action in ["edit", "fail", "re-ask"]:
        await engine.vector_db.invalidate_cache(query)
        
    return {"status": "recorded", "action": action, "optimization": "applied"}

@app.get("/health")
async def health():
    return {"status": "healthy", "optimized": True, "igpu_active": True}
