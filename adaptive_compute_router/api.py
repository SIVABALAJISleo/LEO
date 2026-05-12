import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Adaptive Components
from adaptive_compute_router.kernel import AdaptiveKernel
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Self-Optimizing Universal Compute Router")

# Init Kernel
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
kernel = AdaptiveKernel(inference)

@app.post("/adaptive_route_query")
async def handle_adaptive_query(raw_input: Dict[str, Any]):
    """
    16-STEP SELF-OPTIMIZING PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_adaptive_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Profiling compute and historical performance...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        res = await kernel.execute_task(query)
        
        # 3. Formatted Output (STRICT STRUCTURE)
        output = (
            f"[Task Type]: {res['task_type']}\n"
            f"[Selected Route + Reason]: {res['route']} (Optimized via 90/10 adaptive logic)\n"
            f"[Execution Summary]: Compute path selected based on {res['latency']} historical performance.\n"
            f"[Answer]:\n{res['answer']}\n\n"
            f"[Latency]: {res['latency']}\n"
            f"[Cost]: {res['cost']}\n"
            f"[Confidence]: {res['confidence'] * 100:.0f}%"
        )
        
        yield json.dumps({"token": output})
        
        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_adaptive_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)
