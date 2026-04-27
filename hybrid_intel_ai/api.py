import time
import json
import logging
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Hybrid Components
from hybrid_intel_ai.symbolic import SymbolicEngine
from hybrid_intel_ai.router import HybridRouter
from hybrid_intel_ai.knowledge import VerifiedKnowledgeLayer
from hybrid_intel_ai.evaluator import TestTimeEvaluator
from intel_core_ai.inference import IntelInferenceEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hybrid Intel-Optimized AI")

# Init Engines
model_path = "models/phi-3-mini-4k-instruct-q4_k_m.gguf"
inference = IntelInferenceEngine(model_path)
router = HybridRouter(inference)
symbolic = SymbolicEngine()
knowledge = VerifiedKnowledgeLayer()
evaluator = TestTimeEvaluator(inference)

# Seed Knowledge with Sources
knowledge.seed_with_sources([
    ("The hybrid system routes math to a symbolic engine and facts to RAG.", "System Architecture Doc"),
    ("Intel Iris Xe is an integrated GPU designed for mobile and desktop efficiency.", "Intel Product Sheet")
])

@app.post("/hybrid_query")
async def handle_hybrid_query(raw_input: Dict[str, Any]):
    """
    HYBRID EXECUTION PIPELINE
    """
    start_time = time.time()
    query = raw_input.get("query", "")
    
    async def generate_pipeline():
        # 1. Perception Layer (Layer 9): Instant ACK
        yield json.dumps({"status": "ACK", "message": "Analyzing query signals...", "latency": f"{(time.time()-start_time)*1000:.2f}ms"})
        
        # 2. Intent Parsing & Routing (Layer 1 & 2)
        intent = router.parse_intent(query)
        task = intent.get("task", "language")
        yield json.dumps({"step": "ROUTING", "target": task})

        # 3. Dynamic Execution
        if task == "math":
            # Layer 6: Symbolic Engine
            result = symbolic.execute(intent.get("sub_task"), intent.get("entities"))
            yield json.dumps({"step": "SYMBOLIC", "result": result, "source": "Deterministic Logic"})
            
        elif task == "knowledge":
            # Layer 3: Verified RAG
            doc, source = knowledge.retrieve_with_source(query)
            if doc:
                yield json.dumps({"step": "KNOWLEDGE", "content": doc, "source": source})
            else:
                # Fallback to language if not found in RAG
                yield json.dumps({"step": "KNOWLEDGE", "content": "No local grounding found. Escalating to LLM."})
                for token in inference.generate_stream(query):
                    yield json.dumps({"token": token})
                    
        elif task == "complex":
            # Layer 5: Test-Time Compute
            yield json.dumps({"step": "COMPUTATION", "status": "Executing test-time evaluation loop..."})
            result = evaluator.resolve_complex(query)
            yield json.dumps({"step": "FINAL", "content": result})
            
        else:
            # Layer 4: Generation Layer
            yield json.dumps({"step": "GENERATION", "mode": "Streaming"})
            for token in inference.generate_stream(query):
                yield json.dumps({"token": token})

        yield json.dumps({"step": "COMPLETE", "total_latency": f"{(time.time()-start_time)*1000:.2f}ms"})

    return StreamingResponse(generate_pipeline(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
