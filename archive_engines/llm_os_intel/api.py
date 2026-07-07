import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# LLM OS Components
from archive_engines.llm_os_intel.memory import LLMOSMemory
from archive_engines.llm_os_intel.reasoning_loop import IterativeReasoningEngine
from archive_engines.hybrid_intel_ai.knowledge import VerifiedKnowledgeLayer
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Operating System (Intel Optimized)")

# Init Engines
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
knowledge = VerifiedKnowledgeLayer()
memory = LLMOSMemory(knowledge)
reasoning_engine = IterativeReasoningEngine(inference, memory)

@app.post("/os_query")
async def handle_os_query(raw_input: Dict[str, Any]):
    """
    LLM OS ITERATIVE PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    memory.reset_scratchpad()
    
    async def generate_os_stream():
        # 1. Perception (Layer 10): Instant ACK
        yield json.dumps({"status": "ACK", "msg": "Initializing OS Kernel...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Retrieval (Layer 3)
        facts = memory.retrieve_facts(query)
        if facts:
            yield json.dumps({"step": "RETRIEVAL", "msg": "Context Loaded into RAM", "preview": facts[:100] + "..."})
            memory.scratchpad["concepts"] = f"Initial Context: {facts}"

        # 3. Iterative Reasoning (Layer 4)
        # We stream the progress of each pass
        for pass_key, instruction in reasoning_engine.passes:
            yield json.dumps({"step": "REASONING", "pass": pass_key.upper(), "msg": instruction})
            # Run pass (internal call to LLM)
            result = await reasoning_engine.run_pass(pass_key, instruction, query)
            
            # Perception: Show a snippet of progress
            yield json.dumps({"step": "SCRATCHPAD_UPDATE", "key": pass_key, "summary": result[:150] + "..."})
            
            # Optional: yield partial tokens if it's the final pass
            if pass_key == "refinement":
                yield json.dumps({"step": "FINAL_OUTPUT", "msg": "Streaming refined response..."})
                # Re-run final pass as stream for perception
                for token in inference.generate_stream(query, f"Final Refinement based on memory: {memory.get_full_context()}"):
                    yield json.dumps({"token": token})

        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(generate_os_stream(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
