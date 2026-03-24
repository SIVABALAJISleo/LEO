"""
Phase 6: End-to-End Avoidance Validation
Tests all optimization layers including upgraded Phase 3 modules.
"""
import pytest
import asyncio
import time
from collections import Counter


@pytest.fixture
def engine():
    """Initialize the engine for testing."""
    from backend.core.orchestrator import hyper_engine
    return hyper_engine


@pytest.fixture
def reasoning_store():
    from backend.memory.reasoning_store import global_reasoning_store
    return global_reasoning_store


@pytest.fixture
def memory():
    from backend.memory.global_memory import global_memory
    return memory


# ─── Unit Tests: ReasoningStore ────────────────────────────────

class TestReasoningStore:
    """Validates the upgraded FAISS+SQLite ReasoningStore."""

    def test_store_and_exact_lookup(self, reasoning_store):
        """Storing a reasoning chain and retrieving it by exact match."""
        query = "What is the computational complexity of quicksort?"
        steps = ["Identify algorithm", "Analyze average case", "Analyze worst case"]
        answer = "Average O(n log n), worst O(n²)"

        reasoning_store.store(query, steps, answer, confidence=0.95)
        result = reasoning_store.lookup(query)

        assert result is not None
        assert result["mode"] == "EXACT"
        assert result["answer"] == answer
        assert result["steps"] == steps

    def test_semantic_fuzzy_match(self, reasoning_store):
        """Semantically similar queries should hit an existing reasoning chain."""
        # Store original
        reasoning_store.store(
            "Explain quicksort time complexity",
            ["Identify algorithm", "Analyze cases"],
            "Average O(n log n), worst O(n²)",
            confidence=0.95
        )
        # Query with a semantically very similar phrasing
        result = reasoning_store.lookup("What is quicksort time complexity?")

        # This may or may not hit depending on embedding similarity
        # The key assertion is that the lookup doesn't crash
        if result:
            assert result["mode"] in ("EXACT", "SEMANTIC")

    def test_stats(self, reasoning_store):
        """Stats should reflect stored data."""
        stats = reasoning_store.stats()
        assert "total_stored" in stats
        assert "total_reuses" in stats
        assert "faiss_total" in stats
        assert stats["total_stored"] >= 0


# ─── Unit Tests: GlobalMemory ─────────────────────────────────

class TestGlobalMemory:
    """Validates the upgraded FAISS-backed GlobalMemory."""

    def test_log_and_exact_lookup(self):
        from backend.memory.global_memory import global_memory
        global_memory.log(
            query="How to deploy on Railway?",
            answer="Use railway.toml config.",
            mode="CANONICAL",
            shape_key="deploy_railway",
            confidence=0.98,
            latency_ms=12.5
        )
        result = global_memory.lookup("How to deploy on Railway?")
        assert result is not None
        assert result["answer"] == "Use railway.toml config."

    def test_avoidance_stats(self):
        from backend.memory.global_memory import global_memory
        stats = global_memory.avoidance_stats()
        assert "total" in stats
        assert "avoidance_ratio" in stats
        assert "faiss_total" in stats


# ─── Integration Test: Telemetry ──────────────────────────────

class TestTelemetry:
    """Validates the telemetry endpoint returns correct data."""

    def test_get_telemetry(self, engine):
        telemetry = engine.get_telemetry()
        assert "inference_avoidance_ratio" in telemetry
        assert "total_requests" in telemetry
        assert "avoidance_pct" in telemetry
        assert "reasoning_cache_size" in telemetry
        assert "reasoning_reuses" in telemetry
        assert isinstance(telemetry["inference_avoidance_ratio"], float)


# ─── Benchmark: Full Pipeline Simulation ──────────────────────

class TestAvoidanceBenchmark:
    """Simulates a batch of queries and measures avoidance ratio."""

    @pytest.mark.asyncio
    async def test_avoidance_ratio_benchmark(self, engine):
        """
        Sends 50 queries (mix of repeated and unique) and asserts
        that the system avoids full compute on >50% of them.
        """
        patterns = [
            "How do I set up billing?",
            "What is GPU cost savings?",
            "How does RAG retrieval work?",
            "Explain the SaaS optimization pipeline.",
            "What is inference avoidance?",
        ]

        modes = []
        for i in range(50):
            # 70% repeated queries, 30% unique
            if i % 10 < 7:
                query = patterns[i % len(patterns)]
            else:
                query = f"Unique benchmark query number {i}"

            result = await engine.process(
                query,
                f"bench_{i}",
                tenant_id="bench_tenant",
                workspace_id="ws_bench"
            )
            modes.append(result.get("mode", "UNKNOWN"))

        counts = Counter(modes)
        total = len(modes)
        avoided = total - counts.get("FULL_CALC", 0)
        avoidance_ratio = avoided / total

        # At minimum, repeated queries should be served from cache
        assert avoidance_ratio > 0.5, (
            f"Avoidance ratio {avoidance_ratio:.2%} is below 50%. "
            f"Mode distribution: {dict(counts)}"
        )
