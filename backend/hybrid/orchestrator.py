import time
import logging
import uuid
from typing import Dict, Any, AsyncGenerator

from backend.hybrid.intent import global_intent_engine
from backend.hybrid.cache import global_hybrid_cache
from backend.hybrid.rag import global_rag_pipeline
from backend.hybrid.reasoning import global_reasoning_layer

logger = logging.getLogger(__name__)

class HybridSystem:
    """
    Project HYPER: Unified Hybrid Architecture
    Integrates all modules from Intent Engine to Learning Loop.
    """
    def __init__(self, confidence_threshold: float = 0.6):
        self.conf_threshold = confidence_threshold
        self.feedback_log = []

    async def process_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Full pipeline with fast-path and slow-path logic."""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # 1. INPUT -> INTENT ENGINE
        intent_info = global_intent_engine.detect_intent(query)
        confidence = intent_info["confidence"]
        
        # 6. CONFIDENCE CONTROL
        if confidence < self.conf_threshold:
            return {
                "request_id": request_id,
                "answer": "I'm not quite sure I understand. Could you please clarify your request?",
                "status": "CLARIFICATION_REQUIRED",
                "confidence": confidence,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        # 2. FAST PATH -> CACHE
        # We need embedding for cache L2
        embedding = global_intent_engine.model.encode([intent_info["normalized_query"]])[0]
        
        # Check L1 (exact) then L2 (semantic)
        cached_result = global_hybrid_cache.get_l1(query)
        if not cached_result:
            cached_result = global_hybrid_cache.get_l2(embedding)
            
        if cached_result:
            logger.info(f"Cache hit for query: {query}")
            return {
                **cached_result,
                "source": "CACHE",
                "confidence": confidence,
                "latency_ms": int((time.time() - start_time) * 1000)
            }

        # 3. SLOW PATH -> RAG PIPELINE
        context = await global_rag_pipeline.get_context(query)
        
        # 4 & 5. REASONING LAYER + ERROR REDUCTION
        answer = await global_reasoning_layer.get_reasoned_answer(
            intent_info["intent"], context, query
        )
        
        # 8. LEARNING LOOP (Cache update)
        final_response = {
            "request_id": request_id,
            "answer": answer,
            "source": "RAG_REASONING",
            "confidence": confidence
        }
        global_hybrid_cache.set(query, final_response, embedding)
        
        result = {
            **final_response,
            "latency_ms": int((time.time() - start_time) * 1000)
        }
        return result

    async def process_query_stream(self, query: str, session_id: str = "default") -> AsyncGenerator[Dict[str, Any], None]:
        """7. RESPONSE DELIVERY: Streaming output."""
        start_time = time.time()
        
        # Fast initial check
        intent_info = global_intent_engine.detect_intent(query)
        yield {"status": "analyzing", "intent": intent_info["intent"]}
        
        # Check cache immediately
        embedding = global_intent_engine.model.encode([intent_info["normalized_query"]])[0]
        cached = global_hybrid_cache.get_l1(query) or global_hybrid_cache.get_l2(embedding)
        
        if cached:
            yield {**cached, "source": "CACHE_STREAM", "latency_ms": int((time.time() - start_time) * 1000)}
            return

        # Start RAG
        yield {"status": "retrieving_knowledge"}
        context = await global_rag_pipeline.get_context(query)
        
        # Start Reasoning (yield partials if possible, here mocked as steps)
        yield {"status": "reasoning", "mode": "ensemble_active"}
        answer = await global_reasoning_layer.get_reasoned_answer(
            intent_info["intent"], context, query
        )
        
        final_result = {
            "answer": answer,
            "source": "RAG_STREAM",
            "confidence": intent_info["confidence"],
            "latency_ms": int((time.time() - start_time) * 1000)
        }
        
        # Cache final
        global_hybrid_cache.set(query, final_result, embedding)
        yield final_result

    def record_feedback(self, request_id: str, feedback: int):
        """8. LEARNING LOOP: Store feedback."""
        self.feedback_log.append({"request_id": request_id, "score": feedback, "time": time.time()})
        logger.info(f"Feedback recorded for {request_id}: {feedback}")

global_hybrid_system = HybridSystem()
