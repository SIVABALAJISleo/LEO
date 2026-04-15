"""
backend/intelligence/knowledge_field.py

Knowledge Field Coverage Engine (AIS++ Module 4 + 11)
=======================================================
Maps the full domain knowledge space as a 2D field:
  - Topics (top-level domains)
  - Subtopics (specific entities within each domain)

Continuously:
  1. Detects uncovered/missing areas (gaps)
  2. Auto-generates queries to fill gaps
  3. Enqueues gap-filling queries for background precompute
  4. Tracks coverage percentage per domain

Rules:
  - System starts with seeded domain map
  - Every new answer extends the coverage map
  - Gaps are filled proactively (before users ask)
  - Coverage report available via metrics endpoint
"""
import logging
import asyncio
import time
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

# ── Domain Knowledge Map ────────────────────────────────────────────────────
# topic → list of subtopics/entities
DOMAIN_MAP: Dict[str, List[str]] = {
    "AI_FUNDAMENTALS": [
        "machine_learning", "deep_learning", "neural_network", "supervised_learning",
        "unsupervised_learning", "reinforcement_learning", "transfer_learning",
        "few_shot_learning", "zero_shot_learning", "attention_mechanism",
    ],
    "LLM_SYSTEMS": [
        "llm", "gpt", "bert", "transformer", "tokenization", "fine_tuning",
        "quantization", "rlhf", "instruction_tuning", "prompt_engineering",
        "context_window", "temperature", "top_p_sampling",
    ],
    "RAG_ARCHITECTURE": [
        "rag", "retrieval_augmented_generation", "vector_database", "faiss",
        "embedding", "chunking", "reranking", "hybrid_search", "semantic_search",
        "bm25", "document_indexing", "context_compression",
    ],
    "INFERENCE_OPTIMIZATION": [
        "quantization", "pruning", "distillation", "onnx", "openvino",
        "triton_inference", "batching", "speculative_decoding", "kv_cache",
        "early_exit", "model_sharding", "tensor_parallelism",
    ],
    "COMPUTE_AVOIDANCE": [
        "caching", "semantic_cache", "prompt_cache", "compute_reuse",
        "approximate_computation", "delta_compute", "precompute",
        "zero_repeat", "prediction_engine", "triattention",
    ],
    "INFRASTRUCTURE": [
        "fastapi", "celery", "redis", "postgresql", "docker", "kubernetes",
        "prometheus", "grafana", "nginx", "asyncio", "uvicorn", "gunicorn",
    ],
    "SAAS_ARCHITECTURE": [
        "multi_tenancy", "rate_limiting", "api_gateway", "webhook", "billing",
        "usage_metering", "circuit_breaker", "bulkhead", "sla", "slo",
    ],
    "SECURITY": [
        "authentication", "authorization", "jwt", "oauth2", "zero_trust",
        "input_validation", "injection_prevention", "tls", "secret_management",
    ],
    "PERFORMANCE": [
        "latency", "throughput", "p95_latency", "load_testing", "profiling",
        "bottleneck_analysis", "horizontal_scaling", "vertical_scaling", "cdn",
    ],
}

# Intent types to generate per entity
COVERAGE_INTENTS = ["definition", "how_to", "benefit", "comparison"]

# Coverage thresholds
FULL_COVERAGE_PCT = 0.80   # 80% coverage of an intent per entity = "well covered"


class KnowledgeFieldEngine:
    """
    Domain knowledge coverage tracker and gap-filler.
    Ensures the system proactively covers all knowledge before users ask.
    """

    def __init__(self):
        # covered_fields: topic → entity → set of covered intents
        self._covered: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        self._gap_fill_count: int = 0
        self._last_scan: float = 0.0
        self._total_fields: int = sum(len(v) for v in DOMAIN_MAP.values()) * len(COVERAGE_INTENTS)

    # ── Coverage Reporting ─────────────────────────────────────────────────── #

    def mark_covered(self, entity: str, intent: str) -> None:
        """Records that an entity+intent pair is now covered."""
        for topic, entities in DOMAIN_MAP.items():
            normalized_entities = [e.replace("_", " ") for e in entities]
            entity_clean = entity.lower().replace("_", " ")
            if entity_clean in normalized_entities:
                self._covered[topic][entity_clean].add(intent)
                break

    def coverage_report(self) -> Dict[str, Any]:
        """Returns per-domain coverage percentages."""
        report = {}
        total_covered = 0
        total_possible = 0

        for topic, entities in DOMAIN_MAP.items():
            topic_covered = 0
            topic_possible = len(entities) * len(COVERAGE_INTENTS)

            for entity in entities:
                entity_clean = entity.replace("_", " ")
                covered_intents = self._covered.get(topic, {}).get(entity_clean, set())
                topic_covered += len(covered_intents)

            topic_pct = (topic_covered / topic_possible * 100) if topic_possible > 0 else 0
            report[topic] = {
                "covered": topic_covered,
                "possible": topic_possible,
                "coverage_pct": f"{topic_pct:.1f}%",
            }
            total_covered += topic_covered
            total_possible += topic_possible

        overall_pct = (total_covered / total_possible * 100) if total_possible > 0 else 0
        return {
            "overall_coverage": f"{overall_pct:.1f}%",
            "covered_count": total_covered,
            "total_possible": total_possible,
            "by_domain": report,
        }

    # ── Gap Detection ─────────────────────────────────────────────────────── #

    def detect_gaps(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Finds the highest-value uncovered entity+intent combinations.
        Returns list of {entity, intent, query, topic} dicts.
        """
        gaps: List[Dict[str, Any]] = []

        for topic, entities in DOMAIN_MAP.items():
            for entity in entities:
                entity_clean = entity.replace("_", " ")
                covered_intents = self._covered.get(topic, {}).get(entity_clean, set())
                missing_intents = [i for i in COVERAGE_INTENTS if i not in covered_intents]

                for intent in missing_intents:
                    query = self._make_gap_query(entity_clean, intent)
                    gaps.append({
                        "topic":  topic,
                        "entity": entity_clean,
                        "intent": intent,
                        "query":  query,
                    })
                    if len(gaps) >= limit:
                        return gaps

        return gaps

    # ── Auto-Expand ───────────────────────────────────────────────────────── #

    async def fill_gaps(
        self,
        bg_compute,
        tenant_id: str,
        session_id: str = "KNOWLEDGE_FIELD",
        batch_size: int = 20,
    ) -> int:
        """
        Detects gaps and enqueues gap-filling queries.
        Returns number of queries enqueued.
        """
        gaps = self.detect_gaps(limit=batch_size)
        enqueued = 0

        for gap in gaps:
            try:
                asyncio.create_task(
                    bg_compute.enqueue(
                        gap["query"],
                        tenant_id,
                        "KNOWLEDGE_FIELD",
                        session_id,
                        priority="gap_fill",
                    )
                )
                self._gap_fill_count += 1
                enqueued += 1
            except Exception as exc:
                logger.warning(f"knowledge_field.enqueue_error: {exc}")

        if enqueued:
            logger.info(
                f"knowledge_field.gaps_filled: {enqueued} queries enqueued "
                f"total_fills={self._gap_fill_count}"
            )
        return enqueued

    async def run_continuous(
        self,
        bg_compute,
        tenant_id: str = "default",
        interval_sec: float = 60.0,
        batch_size: int = 10,
    ) -> None:
        """Background coroutine: periodically scans for and fills gaps."""
        logger.info("knowledge_field.continuous_worker: started")
        while True:
            try:
                await self.fill_gaps(bg_compute, tenant_id, batch_size=batch_size)
                self._last_scan = time.time()
            except Exception as exc:
                logger.error(f"knowledge_field.run_error: {exc}")
            await asyncio.sleep(interval_sec)

    # ── Internal helpers ──────────────────────────────────────────────────── #

    def _make_gap_query(self, entity: str, intent: str) -> str:
        templates = {
            "definition":  f"What is {entity}?",
            "how_to":      f"How to use {entity}?",
            "benefit":     f"What are the benefits of {entity}?",
            "comparison":  f"When should I use {entity} vs alternatives?",
        }
        return templates.get(intent, f"Tell me about {entity}")

    def stats(self) -> Dict[str, Any]:
        return {
            "total_possible_fields": self._total_fields,
            "gap_fills_launched": self._gap_fill_count,
            "last_scan_ago_secs": round(time.time() - self._last_scan, 1) if self._last_scan else None,
            "coverage_summary": self.coverage_report()["overall_coverage"],
        }


global_knowledge_field = KnowledgeFieldEngine()
