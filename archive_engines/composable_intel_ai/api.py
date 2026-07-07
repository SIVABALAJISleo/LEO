import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Composable Components
from archive_engines.composable_intel_ai.soft_router import SoftRouter
from archive_engines.composable_intel_ai.adapter_manager import AdapterManager
from archive_engines.hybrid_intel_ai.symbolic import SymbolicEngine
from archive_engines.hybrid_intel_ai.knowledge import VerifiedKnowledgeLayer
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Composable Intel-Optimized AI")

# Init Engines
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
soft_router = SoftRouter(inference)
adapter_manager = AdapterManager()
symbolic = SymbolicEngine()
knowledge = VerifiedKnowledgeLayer()

@app.post("/composable_query")
async def handle_composable_query(raw_input: Dict[str, Any]):
    """
    COMPOSABLE EXECUTION PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def generate_composable():
        # 1. Perception Layer (Layer 10): Instant ACK
        yield json.dumps({"status": "ACK", "msg": "Mapping latent domains...", "t": f"{(time.time()-start_time)*1000:.1f}ms"})

        # 2. Soft Routing (Layer 3)
        # Identify weights for LoRA Swarm
        weights = soft_router.extract_weights(query)
        yield json.dumps({"step": "ROUTING", "weights": weights})

        # 3. Dynamic Specialization (Layer 2)
        # Apply LoRAs to base model (Soft Activation)
        adapter_manager.apply_to_model(inference.llm, weights)
        system_prompt = adapter_manager.get_prompt_template(weights)
        
        # 4. Deterministic Check (Layer 5)
        # Check if query is purely math/logic (Symbolic Engine)
        # Note: We rely on the weights here; if logic is 100%, we might bypass LLM
        if weights.get("logic", 0) > 0.8 or weights.get("math", 0) > 0.8:
             yield json.dumps({"step": "SYMBOLIC", "msg": "Redirecting to deterministic core."})
             # Mock symbolic execution for demonstration
             # Real implementation would parse 'entities' from query
             
        # 5. Knowledge Retrieval (Layer 4)
        doc, source = knowledge.retrieve_with_source(query)
        if doc:
            yield json.dumps({"step": "KNOWLEDGE", "content": doc, "source": source})
            system_prompt += f"\nRelevant Context: {doc}"

        # 6. Generation Pipeline (Layer 6)
        yield json.dumps({"step": "SYNTHESIS", "msg": "Generating cross-domain response..."})
        for token in inference.generate_stream(query, system_prompt):
            yield json.dumps({"token": token})

        yield json.dumps({"step": "COMPLETE", "latency": f"{(time.time()-start_time)*1000:.1f}ms"})

    return StreamingResponse(generate_composable(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
