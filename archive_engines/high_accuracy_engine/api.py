import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# High-Accuracy Components
from archive_engines.high_accuracy_engine.kernel import HighAccuracyKernel
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="High-Accuracy AI Engine")

# Init Kernel
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
kernel = HighAccuracyKernel(inference)

@app.post("/accuracy_query")
async def handle_accuracy_query(raw_input: Dict[str, Any]):
    """
    STRICT 11-STEP ACCURACY PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_accuracy_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Booting High-Accuracy Pipeline...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        res = await kernel.execute_pipeline(query)
        
        # 3. Formatted Output (STEP 8: STRICT)
        output = (
            f"[Domain]: {res['domain']}\n"
            f"[Intent]: {res['intent']}\n"
            f"[Assumptions]: {', '.join(res['assumptions'])}\n"
            f"[Answer / Options]:\n{res['answer']}\n\n"
            f"[Evidence or Reasoning]: {res['evidence']}\n"
            f"[Success Test: how user verifies result]: Check the result against {res['evidence'].lower()}.\n"
            f"[Failure Case + Fix]: If context is missing, the answer is invalid. Fix: Provide more specific parameters.\n"
            f"[Confidence % + why]: {res['confidence'] * 100:.0f}% (Calculated via {res['domain'].lower()} verification logic)\n"
            f"[Uncertainty: exact gap]: {res['uncertainty'] or 'None identified.'}\n\n"
            f"[User Loop]: Is this correct for your situation? (Yes / No / Adjust)"
        )
        
        yield json.dumps({"token": output})
        
        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_accuracy_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)
