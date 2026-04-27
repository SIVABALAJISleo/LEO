import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Safe Components
from safe_outcome_ai.kernel import SafeOutcomeKernel
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Safe Outcome AI System")

# Init Engine
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
kernel = SafeOutcomeKernel(inference)

@app.post("/safe_outcome_query")
async def handle_safe_query(raw_input: Dict[str, Any]):
    """
    6-STEP PIPELINE: CLASSIFY -> GATE -> PROCESS -> CRITIQUE -> OUTPUT -> AWARENESS
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_safe_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Booting Safe Outcome Kernel...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        result = await kernel.execute_safe_loop(query)
        
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
        # Infer correction likely if confidence is marginal
        if result['confidence'] < 0.75:
            yield json.dumps({"status": "AWARENESS_SIGNAL", "msg": "Marginal confidence detected. Adjusted strategy to Safe/Honest output."})

        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_safe_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016)
