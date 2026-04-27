import time
import json
import logging
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

# Intel Optimized Components
from intel_core_ai.input_logic import IntelLogicEngine
from intel_core_ai.inference import IntelInferenceEngine
from intel_core_ai.knowledge import IntelKnowledgeSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Intel-Optimized AI Control")

# Initialize System Components
logic = IntelLogicEngine()
# Note: Model path should point to a valid Phi-3 GGUF file
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
knowledge = IntelKnowledgeSystem()

# Seed initial knowledge
knowledge.seed_knowledge([
    "Intel Iris Xe Graphics (iGPU) can accelerate AI workloads using Vulkan or SYCL.",
    "The Phi-3-mini model is highly efficient for CPU-only inference.",
    "Aggressive INT4 quantization reduces memory bandwidth bottlenecks on Intel CPUs."
])

@app.post("/intel_query")
async def handle_intel_query(raw_input: Dict[str, Any]):
    """
    STRICT 8-LAYER EXECUTION PIPELINE
    """
    start_time = time.time()
    
    # 1. Input Control (Layer 1)
    is_valid, validated = logic.validate(raw_input)
    if not is_valid:
        return validated
    
    query = validated.query
    
    async def generate_response():
        # 2. Logic Offloading (Layer 6)
        rule_hit = logic.check_rules(query)
        if rule_hit:
            yield json.dumps({"step": "LOGIC", "content": rule_hit, "latency": f"{(time.time()-start_time)*1000:.2f}ms"})
            return

        # 3. Knowledge Retrieval (Layer 5 & 7)
        context = knowledge.retrieve(query)
        yield json.dumps({"step": "KNOWLEDGE", "context_found": context is not None})
        
        # 4. LLM Execution (Layer 1, 2, 3)
        # Note: Layer 3 (Speed) is handled by streaming
        system_prompt = "You are a local AI optimized for Intel hardware. Be concise. "
        if context:
            system_prompt += f"Use this context: {context}"
            
        yield json.dumps({"step": "INFERENCE_START"})
        
        full_response = ""
        for token in inference.generate_stream(query, system_prompt):
            full_response += token
            yield json.dumps({"token": token})
            
        # 5. Error Control (Layer 8)
        # Simple confidence check: if response is empty or too short, warn user
        if len(full_response) < 10:
             yield json.dumps({"step": "ERROR_CONTROL", "warning": "Response may be low quality due to low signal."})
             
        total_lat = (time.time() - start_time) * 1000
        yield json.dumps({"step": "COMPLETE", "total_latency": f"{total_lat:.2f}ms"})

    return StreamingResponse(generate_response(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
