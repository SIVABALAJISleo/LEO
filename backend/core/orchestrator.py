from typing import Optional, Dict, List, Any
from backend.intelligence.router import MoERouter, SemanticCache, HallucinationGuard, TraceEngine
from backend.intelligence.rag import RAGEngine
from backend.intelligence.reasoning import reasoning_expert
from backend.performance.caching import MultiLevelCache, PredictiveEngine
from backend.performance.memo import global_memo
from backend.performance.scheduler import scheduler
from backend.performance.embedding_cache import global_embedding_cache
from backend.core.reliability import CircuitBreaker, ReliabilityOrchestrator
from backend.data_efficiency.probabilistic import BloomFilter
import logging
import time
import asyncio
import psutil
import numpy as np
from backend.core.prompt_cache import check_cache, save_cache
from backend.predictive.answer_store import global_predictive_store
from backend.predictive.predictor import global_predictor
from backend.shadow.shadow_store import global_shadow_store
from backend.shadow.shadow_worker import global_shadow_worker
from backend.shadow.conversation_tracker import global_tracker
from backend.core.metrics import (
    PPE_HITS, SHADOW_HITS, MODEL_INVOCATIONS, RAG_HITS, MICRO_MODEL_HITS, CACHE_HITS,
    GRAPH_HITS, TEMPLATE_HITS, MODEL_CALLS_TOTAL,
    REASONING_REUSES, EARLY_EXIT_TOTAL, TOKEN_SAVINGS,
    CANONICAL_HITS, PRECOMPUTE_HITS, FAILURE_RATE, DOMAIN_REJECTIONS,
    COST_FORCED_SAVES, LATENCY_SKIPS, AVOIDANCE_RATIO,    MICRO_MODEL_HITS, CACHE_HITS, COST_SAVED_TOTAL, ENHANCEMENT_HITS,
    CPU_USAGE, EMBEDDING_CACHE_HITS, TINY_MODEL_SUCCESS, LAST_RESORT_MODEL_USAGE,
    MODEL_CALLS_TOTAL, MODEL_INVOCATIONS, FUSION_HITS, CONFIDENCE_BYPASS_RATE,
    AIC_ESCALATION_TOTAL, ENHANCEMENT_ATTEMPTS, ENHANCEMENT_SUCCESS, MODEL_BYPASS_VIA_ENHANCEMENT
)
from backend.analytics.query_logger import global_query_logger

from backend.inference.kv_cache import global_kv_cache
from backend.inference.speculative_decoder import global_speculative_decoder
from backend.rag.context_compression import global_compressor
from backend.reasoning.query_planner import global_query_planner
from backend.micro_models.router import global_micro_router
from backend.learning.answer_store import global_learning_engine
from backend.inference.distributed_router import global_inference_controller

# Next-Gen 10-Layer Pipeline Imports
from backend.normalization.normalizer import global_normalizer
from backend.graph.answer_graph_engine import global_age
from backend.templates.template_engine import global_template_engine
from backend.router.query_complexity import global_complexity_estimator
from backend.memory.reasoning_store import global_reasoning_store
from backend.optimization.token_optimizer import global_token_optimizer
from backend.inference.early_exit import global_early_exit
from backend.planner.execution_planner import global_execution_planner
from backend.enhancement.enhancer import global_enhancer

# Compute-Controlled System Imports (12-Module Architecture)
from backend.domain.domain_guard import global_domain_guard
from backend.normalization.query_shaper import global_query_shaper
from backend.answers.canonical_store import global_canonical_store
from backend.answers.diff_engine import global_diff_engine
from backend.memory.global_memory import global_memory
from backend.memory.failure_store import global_failure_store
from backend.core.confidence import global_confidence_gate
from backend.core.cost_controller import global_cost_controller
from backend.core.latency_controller import global_latency_controller
from backend.predictive.precompute_expander import global_precompute_expander
from backend.predictive.user_profiler import global_user_profiler
from backend.intelligence.reasoning_templates import global_templates

from backend.intelligence.tiny_model_guard import global_tiny_guard

# SaaS Optimization Engine Imports (Phase 8-10)
from backend.enhancement.answer_fusion import global_answer_fusion
from backend.enhancement.answer_enhancer import global_aee
from backend.enhancement.temporal_memory import global_temporal_memory
from backend.intelligence.confidence_engine import global_acce
from backend.intelligence.feedback_store import global_feedback_store
from backend.core.cost_tracker import global_cost_tracker
from backend.core.usage_metering import global_usage_meter

# Phase 3: High-Avoidance Core
try:
    from backend.answers.semantic_canonical import global_semantic_canonical
    from backend.answers.fragment_engine import global_fragment_composer

    from backend.core.composer import global_composer
    from backend.predictive.knowledge_expansion import global_knowledge_expander
    # Intelligence Compression Layer
    from backend.compression.knowledge_compressor import global_knowledge_compressor
    from backend.compression.reconstructor import global_reconstructor
    from backend.compression.fragments import global_fragment_compressor
    from backend.compression.embedding_optimizer import global_embedding_optimizer
    from backend.compression.compute_optimizer import global_compute_optimizer
    from backend.compression.storage_optimizer import global_storage_optimizer
except ImportError:
    # Handle if running from different root
    try:
        from answers.semantic_canonical import global_semantic_canonical
        from answers.fragment_engine import global_fragment_composer

        from core.composer import global_composer
        from predictive.knowledge_expansion import global_knowledge_expander
        
        # Intelligence Compression Layer
        from compression.knowledge_compressor import global_knowledge_compressor
        from compression.reconstructor import global_reconstructor
        from compression.fragments import global_fragment_compressor
        from compression.embedding_optimizer import global_embedding_optimizer
        from compression.compute_optimizer import global_compute_optimizer
        from compression.storage_optimizer import global_storage_optimizer
    except ImportError:
        logger.warning("some_composition_engines_missing")

# Phase 20: Unified Zero-Runtime Control Layer
from backend.core.zero_compute import global_zero_control
from backend.optimization.batcher import global_query_batcher

logger = logging.getLogger(__name__)

class UnifiedSaaSEngine:
    """
    Hyperscaler-Grade Processing Engine with Intelligence Compression.
    """
    def __init__(self):
        # 1. Intelligence & Verification
        self.router = MoERouter()
        self.semantic_cache = SemanticCache()
        self.rag = RAGEngine()
        self.guard = HallucinationGuard()
        self.trace_engine = TraceEngine()
        
        # 2. Performance & Compute Reduction
        self.cache = MultiLevelCache()
        self.predictor = PredictiveEngine(self.cache)
        self.scheduler = scheduler
        
        # 3. Reliability
        self.cb = CircuitBreaker()
        self.reliability = ReliabilityOrchestrator(self.cb)
        
        # 4. Data Efficiency
        self.bloom = BloomFilter()
        
        # 5. In-flight Request Deduplication
        self.processing: Dict[str, asyncio.Task] = {}

        # 6. BG Workers (Will be started via start())
        self.precompute_worker_started = False

    async def start(self):
        """Initializes background workers and queues."""
        if not self.precompute_worker_started:
            from backend.predictive.precompute_worker import global_precompute_worker
            from backend.background.compute_engine import global_bg_compute
            asyncio.create_task(global_precompute_worker.run())
            asyncio.create_task(global_bg_compute.run())
            self.precompute_worker_started = True
            logger.info("orchestrator_background_workers_started")
        
    async def _check_persistent_cluster(self, query: str, tenant_id: str, query_emb: Optional[np.ndarray] = None) -> Optional[Dict[str, Any]]:
        """Layer 2: Semantic Canonical Answer Reuse."""
        if query_emb is None:
            # Fallback to hash if no embedding (should be rare in new pipeline)
            return await self._check_legacy_hash_cluster(query, tenant_id)
            
        return global_semantic_canonical.lookup(query_emb)

    async def _check_legacy_hash_cluster(self, query: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Legacy hash-based lookup for backward compatibility."""
        from backend.core.database import SessionLocal, QueryCluster
        import hashlib
        db = SessionLocal()
        try:
            h = hashlib.sha256(query.lower().strip().encode()).hexdigest()
            cluster = db.query(QueryCluster).filter(QueryCluster.cluster_hash == h, QueryCluster.tenant_id == tenant_id).first()
            if cluster:
                cluster.use_count += 1
                db.commit()
                return {"answer": cluster.canonical_answer, "confidence": 0.98, "canonical": True}
        finally:
            db.close()
        return None

    def _save_canonical_cluster(self, query: str, answer: str, tenant_id: str, query_emb: Optional[np.ndarray] = None):
        """Saves a high-confidence result as a canonical cluster."""
        if query_emb is not None:
             global_semantic_canonical.register(query, answer, query_emb, tenant_id)
        else:
             # Legacy fallback
             from backend.core.database import SessionLocal, QueryCluster
             import hashlib
             db = SessionLocal()
             try:
                 h = hashlib.sha256(query.lower().strip().encode()).hexdigest()
                 exists = db.query(QueryCluster).filter(QueryCluster.cluster_hash == h).first()
                 if not exists:
                     new_c = QueryCluster(
                         cluster_hash=h,
                         canonical_query=query,
                         canonical_answer=answer,
                         tenant_id=tenant_id
                     )
                     db.add(new_c)
                     db.commit()
             finally:
                 db.close()
    async def process(self, query: str, request_id: str, tenant_id: str = "default", workspace_id: str = "default"):
        """Standard entry point with micro-batching and latency tracking."""
        from backend.optimization.batcher import global_query_batcher
        from backend.analytics.metrics import global_metrics
        
        async def run_internal(q):
            start_time = time.time()
            res = await self._process_core(q, request_id, tenant_id, workspace_id, start_time)
            latency_ms = (time.time() - start_time) * 1000
            global_metrics.track_latency(latency_ms)
            return res

        return await global_query_batcher.get_batched_result(query, run_internal)

    async def _process_core(self, query: str, request_id: str, tenant_id: str, workspace_id: str, start_time: float):
        """ Hardened Zero-Runtime Pipeline routing through Unified Control Layer. """
        from backend.analytics.metrics import global_metrics
        from backend.core.zero_compute import global_zero_control

        logger.info(f"zero_runtime_request: id={request_id} query={query}")
        
        # ALL RUNTIME LOGIC CONSOLIDATED IN CONTROL LAYER
        result = await global_zero_control.handle_request(query, request_id, tenant_id, workspace_id, start_time)
        
        # Double-check for wrap format compliance
        return self._wrap_response(result["result"], result["mode"], start_time, result["confidence"])

    async def _process_core_LEGACY_HAVE_BEEN_REPLACED(self):
        # This is a marker for the end of the replaced block
        pass

    async def process_stream(self, query: str, request_id: str, tenant_id: str = "default"):
        """Streaming version that follows the full optimization pipeline."""
        start_time = time.time()
        
        # 1. ATTEMPT FULL RESULT PRE-DETECTION (Bypass stream if possible)
        # This is the 'holy grail' of avoidance: stream an already fully computed result instantly.
        result = await self.process(query, request_id, tenant_id)
        if result.get("compute_cost_avoided"):
            logger.info("stream_fully_avoided")
            yield result["result"]
            return

        # 2. IF NOT AVOIDED, FALLBACK TO STREAMING REASONING
        user_id = request_id.split("_")[1] if "_" in request_id else "default"
        
        # 1. RETRIEVAL
        context_nodes = self.rag.retrieve(query, tenant_id=tenant_id)
        context_docs = [n["content"] for n in context_nodes]
        
        # 2. STREAMING REASONING
        from backend.intelligence.reasoning import reasoning_expert
        async for chunk in reasoning_expert.solve_stream(
            query, 
            context=context_docs, 
            session_id=user_id, 
            tenant_id=tenant_id
        ):
            yield chunk

        # 3. BG LOGGING & USAGE
        from backend.core.database import SessionLocal
        from backend.core.metering import record_usage
        db = SessionLocal()
        try:
            record_usage(db, tenant_id, user_id, "request_stream", 1)
        finally:
            db.close()

    def _wrap_response(self, result, mode, start_time, confidence=1.0):
        data = result.get("result") if isinstance(result, dict) and "result" in result else result
        answer = data.get("answer") if isinstance(data, dict) else str(data)
        expert = data.get("expert") if isinstance(data, dict) else "MoE_Default"
        trace = data.get("trace") if isinstance(data, dict) else []

        return {
            "status": "success",
            "mode": mode,
            "expert": str(expert),
            "result": str(answer),
            "confidence": float(confidence),
            "trace": trace,
            "compute_cost_avoided": mode != "FULL_CALC",
            "latency_ms": float(f"{(float(time.time()) - float(start_time)) * 1000.0:.2f}"),
            "timestamp": float(time.time())
        }

    def get_telemetry(self) -> dict:
        """
        PHASE 5: Returns real-time inference avoidance telemetry.
        Aggregates data from all optimization layers.
        """
        avoidance = global_memory.avoidance_stats()
        reasoning_stats = global_reasoning_store.stats()
        
        total = avoidance.get("total", 0)
        avoidance_ratio = avoidance.get("avoidance_ratio", 0.0)
        
        # Calculate real-time last-resort usage
        total_calls = MODEL_INVOCATIONS._value.get() if hasattr(MODEL_INVOCATIONS, '_value') else 1
        large_calls = MODEL_CALLS_TOTAL._value.get() if hasattr(MODEL_CALLS_TOTAL, '_value') else 0
        usage_pct = (large_calls / total_calls) * 100 if total_calls > 0 else 0
        LAST_RESORT_MODEL_USAGE.set(usage_pct)

        return {
            "inference_avoidance_ratio": avoidance_ratio,
            "total_requests": total,
            "avoidance_pct": float(f"{avoidance_ratio * 100.0:.1f}"),
            "last_resort_usage_pct": float(f"{usage_pct:.2f}"),
            "reasoning_cache_size": reasoning_stats.get("total_stored", 0),
            "reasoning_reuses": reasoning_stats.get("total_reuses", 0),
            "embedding_cache_hits": EMBEDDING_CACHE_HITS._value.get() if hasattr(EMBEDDING_CACHE_HITS, '_value') else 0,
            "tiny_model_success_rate": TINY_MODEL_SUCCESS._value.get() / total if total > 0 else 0,
        }


hyper_engine = UnifiedSaaSEngine()
