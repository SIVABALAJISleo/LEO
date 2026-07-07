import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Verified Components
from archive_engines.verified_outcome_ai.kernel import VerifiedKernel
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Verified Outcome AI System")

# Init Engine
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
kernel = VerifiedKernel(inference)

@app.post("/verified_outcome_query")
async def handle_verified_query(raw_input: Dict[str, Any]):
    """
    6-STEP PIPELINE: CLASSIFY -> CONFIDENCE -> PROCESS -> CRITIQUE -> OUTPUT -> AWARENESS
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_verified_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Booting Verified Outcome Kernel...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        result = await kernel.execute_verified_loop(query)
        
        # 3. Formatted Output (STEP 4)
        output = (
            f"[DOMAIN]: {result['domain']}\n"
            f"[CONFIDENCE]: {result['confidence'] * 100:.0f}%\n"
            f"[ANSWER]:\n{result['answer']}\n\n"
            f"[UNCERTAINTY]:\n- {result['uncertainty']}\n"
        )
        
        if result['sources']:
            output += "\n[SOURCES]:\n"
            for src in result['sources']:
                output += f"- {src}\n"
                
        if result['alternatives']:
            output += "\n[ALTERNATIVES]:\n"
            for alt in result['alternatives']:
                output += f"- {alt}\n"
        
        yield json.dumps({"token": output})
        
        # 4. Outcome Awareness (STEP 5)
        # We infer if the task was completed based on confidence
        if result['confidence'] > 0.8:
            yield json.dumps({"status": "SUCCESS", "msg": "High-confidence outcome verified."})
        else:
            yield json.dumps({"status": "AWARENESS_SIGNAL", "msg": "Outcome verification marginal. Correction may be likely."})

        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_verified_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
