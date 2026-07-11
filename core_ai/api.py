import time
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import logging

from core_ai.input_control import InputController
from core_ai.intent_layer import IntentLayer
from core_ai.knowledge_layer import KnowledgeLayer
from core_ai.pipeline_components import ExecutionEngine, ErrorController, FeedbackLoop

# --- LEO Tesla Resonance Layers Import ---
from core_ai.resonance.semantic_cache import LEOSemanticCache
from core_ai.resonance.hetero_scheduler import HeteroFrequencyScheduler
from memory.resonance_graph import LEOKnowledgeGraph
from core_ai.resonance.speculative_decoder import TeslaSpeculativeDecoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Core AI Production System")

# Initialize Layers
input_ctrl = InputController()

intent_layer = IntentLayer()
intent_layer.register_intents({
    "status_check": "What is the system status?",
    "security_override": "Initiate security override protocol.",
    "general_query": "Search for information."
})

knowledge_layer = KnowledgeLayer()
exec_engine = ExecutionEngine()
error_ctrl = ErrorController()
feedback_loop = FeedbackLoop()

# Tesla Resonance Subsystems Singletons
tesla_cache = LEOSemanticCache()
tesla_scheduler = HeteroFrequencyScheduler()
tesla_graph = LEOKnowledgeGraph()
tesla_decoder = TeslaSpeculativeDecoder()

@app.get("/stream")
async def process_query_stream(query: str, session_id: str = "default"):
    """
    LAYER 6 & 8: PERFORMANCE SYSTEM & SYSTEM CONSTRAINTS
    - Stream responses (perceived speed > actual speed).
    - Max latency target: <1.5s
    """
    start_time = time.time()
    
    async def event_generator():
        # LAYER 1: Semantic Cache Pre-Intercept (Tesla Resonance Layer 1)
        cache_hit = tesla_cache.intercept_query(query)
        if cache_hit:
            yield f"data: {json.dumps({'step': 'TESLA_CACHE_HIT', 'result': cache_hit, 'total_latency_ms': round((time.time()-start_time)*1000)})}\n\n"
            return

        # LAYER 2: INPUT CONTROL
        is_valid, val_data = input_ctrl.validate({"query": query, "session_id": session_id})
        if not is_valid:
            yield f"data: {json.dumps({'status': 'error', 'payload': val_data})}\n\n"
            return
            
        yield f"data: {json.dumps({'step': 'ACK', 'latency_ms': round((time.time()-start_time)*1000)})}\n\n"
        
        # LAYER 3: Knowledge Graph Lookup (Tesla Resonance Layer 4)
        kg_context = tesla_graph.retrieve_context(query)
        if kg_context:
            yield f"data: {json.dumps({'step': 'TESLA_KG_CONTEXT_RESOLVED', 'context': kg_context})}\n\n"

        # Route dynamically via Heterogeneous Scheduler (Tesla Resonance Layer 2)
        routing_decision = tesla_scheduler.route_compute("inference", "models/leo-3b-1.58bit")
        yield f"data: {json.dumps({'step': 'TESLA_ROUTING_RESOLVED', 'route': routing_decision})}\n\n"

        # LAYER 4: INTENT + CONFIDENCE
        intent_res = intent_layer.determine_intent(val_data.query)
        yield f"data: {json.dumps({'step': 'INTENT_RESOLVED', 'intent': intent_res['intent']})}\n\n"
        
        if intent_res["status"] == "clarify":
            yield f"data: {json.dumps({'status': 'clarify', 'payload': intent_res['message']})}\n\n"
            feedback_loop.record_signal(intent_res["intent"], success=False)
            return

        # LAYER 5: KNOWLEDGE LAYER
        knowledge = await knowledge_layer.retrieve(intent_res["intent"])
        yield f"data: {json.dumps({'step': 'GROUNDING_COMPLETE', 'source': knowledge['source']})}\n\n"
        
        # Speculative Decoding execution (Tesla Resonance Layer 5)
        pipe, config = tesla_decoder.init_speculative_pipeline()
        spec_result = pipe.generate(query)

        # LAYER 6: EXECUTION ENGINE
        exec_res = exec_engine.execute(intent_res["intent"], knowledge)
        # Fuse speculative result into executor output
        exec_res["data"] = f"{spec_result} | {exec_res['data']}"

        # LAYER 7: ERROR CONTROL
        final_res = error_ctrl.validate_output(exec_res, intent_res["confidence"])
        
        # Update user model on success
        if final_res["status"] == "success":
            feedback_loop.record_signal(intent_res["intent"], success=True)
            # Store in semantic cache
            tesla_cache.store_query(query, final_res["result"])
            
        final_latency = round((time.time()-start_time)*1000)
        yield f"data: {json.dumps({'step': 'FINAL', 'result': final_res, 'total_latency_ms': final_latency})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
