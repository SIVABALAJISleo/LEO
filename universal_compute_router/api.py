import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Router Components
from universal_compute_router.orchestrator import UniversalOrchestrator
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Universal Compute Router AI")

# Init Kernel
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
orchestrator = UniversalOrchestrator(inference)

@app.post("/route_query")
async def handle_route_query(raw_input: Dict[str, Any]):
    """
    DYNAMIC COMPUTE ROUTING PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_router_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Detecting hardware & routing...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        res = await orchestrator.execute_task(query)
        
        # 3. Formatted Output (STRICT STRUCTURE)
        output = (
            f"[Task Type]: {res['task_type']}\n"
            f"[Selected Route + Reason]: {res['route']} ({res['reason']})\n"
            f"[Execution Summary]: Local inference engine activated on {res['route'].lower()}.\n"
            f"[Answer]:\n{res['answer']}\n\n"
            f"[Latency]: {res['latency']}\n"
            f"[Cost Estimate]: {res['cost']}\n"
            f"[Confidence]: {res['confidence'] * 100:.0f}%"
        )
        
        yield json.dumps({"token": output})
        
        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_router_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)
