import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Steered Components
from steered_intel_ai.steering_engine import SteeringEngine
from steered_intel_ai.router import SteeredRouter
from steered_intel_ai.tools import ToolLayer
from hybrid_intel_ai.knowledge import VerifiedKnowledgeLayer
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Steered Intel-Optimized AI")

# Init Engines
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
steering_engine = SteeringEngine()
router = SteeredRouter(inference)
tools = ToolLayer()
knowledge = VerifiedKnowledgeLayer()

@app.post("/steered_query")
async def handle_steered_query(raw_input: Dict[str, Any]):
    """
    STEERED EXECUTION PIPELINE (10 STEPS)
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def generate_steered():
        # 1. Perception (Layer 10): Instant ACK
        yield json.dumps({"status": "ACK", "msg": "Analyzing intent signals...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Intent Parsing & Soft Routing (Layer 3)
        intent = router.parse(query)
        weights = intent.get("weights", {})
        yield json.dumps({"step": "ROUTING", "intent_profile": intent})

        # 3. Control Vector Build (Layer 2)
        # Combine vectors: V = Σ (weight_i * vector_i)
        active_vectors = steering_engine.blend_vectors(weights)
        if active_vectors:
             yield json.dumps({"step": "STEERING", "msg": f"Blending {len(active_vectors)} activation vectors..."})
             # Layer 6 Injection occurs here in the hidden layers
             steering_engine.apply_steering(inference.llm, active_vectors)

        # 4. Retrieval (Layer 4)
        context = ""
        if intent.get("need_retrieval", True):
             doc, source = knowledge.retrieve_with_source(query)
             if doc:
                 yield json.dumps({"step": "GROUNDING", "source": source})
                 context = doc
             else:
                 yield json.dumps({"step": "GROUNDING", "msg": "No local facts found."})

        # 5. Symbolic Tools (Layer 5)
        if intent.get("need_tools", False):
             yield json.dumps({"step": "SYMBOLIC", "msg": "Running deterministic tools..."})
             # Logic for tool selection would go here
        
        # 6. Generation Pipeline (Layer 6)
        system_prompt = "You are a steered local AI. "
        if context:
            system_prompt += f"Use context: {context}. Mandatory: cite source if provided."
            
        yield json.dumps({"step": "GENERATION", "msg": "Streaming steered response..."})
        for token in inference.generate_stream(query, system_prompt):
            yield json.dumps({"token": token})

        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(generate_steered(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
