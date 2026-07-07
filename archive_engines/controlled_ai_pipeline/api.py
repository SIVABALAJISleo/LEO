import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Controlled Pipeline Components
from archive_engines.controlled_ai_pipeline.kernel import ControlledKernel
from archive_engines.high_perf_intel_ai.inference import HighPerfEngine
from archive_engines.llm_os_core.memory_knowledge import OSKnowledge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Controlled Measurable AI Pipeline")

# Init Engines
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
engine = HighPerfEngine(model_path)
knowledge = OSKnowledge()
kernel = ControlledKernel(engine, knowledge)

@app.post("/controlled_query")
async def handle_controlled_query(raw_input: Dict[str, Any]):
    """
    12-STEP MEASURABLE CONTROL LOOP
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def run_controlled_pipeline():
        # 1. Perception
        yield json.dumps({"status": "ACK", "kernel": "Booting Controlled Pipeline...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Execution (The Pipeline)
        # For demo purposes, we run the full kernel logic
        result = await kernel.run_pipeline(query)
        
        yield json.dumps({"step": "PROCESS_COMPLETE", "result_type": result['status']})

        # 3. Final Output (LAYER 12 Success Condition)
        if result['status'] == "UNCERTAINTY":
            yield json.dumps({
                "mode": "MULTIPLE_PERSPECTIVES",
                "content": result['options'],
                "message": result['message']
            })
        else:
            yield json.dumps({
                "mode": "SINGLE_VERIFIED",
                "content": result['result'],
                "confidence": result.get('confidence', 0.0)
            })

        yield json.dumps({"step": "HALT", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(run_controlled_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)
