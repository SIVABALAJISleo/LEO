import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Outcome Components
from outcome_driven_ai.kernel import OutcomeKernel
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Outcome-Driven AI System")

# Init Kernel
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
kernel = OutcomeKernel(inference)

@app.post("/outcome_query")
async def handle_outcome_query(raw_input: Dict[str, Any]):
    """
    STRICT PIPELINE: CLASSIFY -> PROCESS -> CRITIQUE -> FORMAT
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_outcome_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "msg": "Analyzing domain integrity...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Loop)
        result = await kernel.execute_outcome_loop(query)
        
        # 3. Formatted Output (STEP 4)
        output = (
            f"[DOMAIN]: {result['domain']}\n"
            f"[CONFIDENCE]: {result['confidence'] * 100:.0f}%\n"
            f"[ANSWER]:\n{result['answer']}\n\n"
            f"[UNCERTAINTY]:\n- {result['uncertainty']}\n"
        )
        
        if result['alternatives']:
            output += "\n[ALTERNATIVES]:\n"
            for alt in result['alternatives']:
                output += f"- {alt}\n"
        
        # Stream the full structured response
        yield json.dumps({"token": output})
        
        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_outcome_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)
