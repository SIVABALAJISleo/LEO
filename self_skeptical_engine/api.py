import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Self-Skeptical Components
from self_skeptical_engine.kernel import SelfSkepticalKernel
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Self-Skeptical AI Engine")

# Init Kernel
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
kernel = SelfSkepticalKernel(inference)

@app.post("/skeptical_query")
async def handle_skeptical_query(raw_input: Dict[str, Any]):
    """
    STRICT 16-STEP SELF-SKEPTICAL PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_skeptical_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Booting Self-Skeptical Pipeline...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        res = await kernel.execute_pipeline(query)
        
        # 3. Formatted Output (STRICT STRUCTURE)
        output = (
            f"[Domain]: {res['domain']}\n"
            f"[Intent]: {res['intent']}\n"
            f"[Assumptions]: {', '.join(res['assumptions'])}\n"
            f"[Answer / Options]:\n{res['answer']}\n\n"
            f"[Evidence / Reasoning]: {res['reasoning']}\n"
            f"[Adversarial Risk]: {res['adversarial_risk']}\n"
            f"[Success Test]: Valid if result matches {res['domain'].lower()} verification.\n"
            f"[Failure Case + Fix]: If assumption set {res['assumptions']} is invalid, answer fails. Fix: Update context.\n"
            f"[Confidence % + Why]: {res['confidence'] * 100:.0f}% (Calculated via cross-domain path agreement)\n"
            f"[Epistemic Label]: [{res['epistemic_label']}]\n"
            f"[Residual Uncertainty]: {res['uncertainty']}\n\n"
            f"[User Confirmation]: Does this match your real situation? (Yes / No / Adjust)"
        )
        
        yield json.dumps({"token": output})
        
        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_skeptical_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8019)
