import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Boundary Components
from archive_engines.boundary_perfect_ai.kernel import BoundaryKernel
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Boundary-Perfect AI System")

# Init Kernel
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
kernel = BoundaryKernel(inference)

@app.post("/boundary_query")
async def handle_boundary_query(raw_input: Dict[str, Any]):
    """
    STRICT 10-STEP BOUNDARY PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_boundary_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Booting Boundary-Perfect Pipeline...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        res = await kernel.execute_pipeline(query)
        
        # 3. Formatted Output (STRICT STRUCTURE)
        output = (
            f"[Domain]: {res['domain']}\n"
            f"[Intent Restatement]: {res['intent']}\n"
            f"[Assumptions]: {', '.join(res['assumptions'])}\n"
            f"[Answer / Options]:\n{res['answer']}\n\n"
            f"[Verification / Evidence]: {res['verification']}\n"
            f"[Success Test]: {res['success_test']}\n"
            f"[Failure Case + Fix]: {res['failure_case']}\n"
            f"[Confidence % + Why]: {res['confidence']}% (Validated through {res['domain'].lower()} reasoning engine)\n"
            f"[Residual Uncertainty]: {res['residual_uncertainty']}\n\n"
            f"[User Confirmation Prompt]: Does this match your actual situation? (Yes / No / Adjust)"
        )
        
        yield json.dumps({"token": output})
        
        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_boundary_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8017)
