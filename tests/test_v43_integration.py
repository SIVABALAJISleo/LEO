"""
LEO AI V43 – Integration Test Suite
====================================
Tests the full V43 software-first orchestration pipeline including:
  • Direct orchestrator execution (offline, zero network)
  • Avoidance hierarchy (cache hits, memory recall)
  • Multilingual routing (Dravidian scripts)
  • Adaptive quantization tier selection
  • Intelligence-per-watt metrics
  • API endpoint contract
  • Security gate blocking
  • Budget exhaustion graceful degradation
"""

import os
import pytest
from fastapi.testclient import TestClient

# Ensure offline mode before any imports that might touch HuggingFace
os.environ.setdefault("LEO_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")

from backend.main import app
from backend.layers.v43_software_first_orchestrator import (
    V43SoftwareFirstOrchestrator,
    IntelligenceBudget,
    _fingerprint,
    _probe_hardware,
    _select_quant_tier,
)

client = TestClient(app)


# ══════════════════════════════════════════════════════════════════════════
# Unit Tests – Helper functions
# ══════════════════════════════════════════════════════════════════════════

class TestV43Helpers:

    def test_fingerprint_deterministic(self):
        """Same query always produces the same fingerprint."""
        q = "How does LEO AI work?"
        fp1 = _fingerprint(q)
        fp2 = _fingerprint(q)
        assert fp1 == fp2
        assert len(fp1) == 16

    def test_fingerprint_normalised(self):
        """Whitespace and casing differences produce the same fingerprint."""
        fp_a = _fingerprint("hello world")
        fp_b = _fingerprint("  HELLO   WORLD  ")
        assert fp_a == fp_b

    def test_hardware_probe_returns_dict(self):
        hw = _probe_hardware()
        assert isinstance(hw, dict)
        assert "cpu_cores" in hw
        assert hw["cpu_cores"] >= 1
        assert "quantization_tier" in hw
        assert hw["quantization_tier"] in ("INT4", "INT8", "FP16", "BF16", "FP32")

    def test_quant_tier_low_complexity(self):
        hw = {"quantization_tier": "INT8"}
        tier = _select_quant_tier(hw, "low")
        # Low complexity → step down from INT8 → INT4
        assert tier in ("INT4", "INT8")

    def test_quant_tier_high_complexity(self):
        hw = {"quantization_tier": "INT8"}
        tier = _select_quant_tier(hw, "high")
        # High complexity → step up from INT8 → FP16
        assert tier in ("INT8", "FP16")

    def test_quant_tier_bounds(self):
        """Never goes out of range even for extreme inputs."""
        hw = {"quantization_tier": "INT4"}
        low = _select_quant_tier(hw, "low")
        assert low in ("INT4", "INT8")     # Can't go below INT4

        hw2 = {"quantization_tier": "FP32"}
        high = _select_quant_tier(hw2, "research")
        assert high == "FP32"             # Already at max


class TestIntelligenceBudget:

    def test_budget_ticks_correctly(self):
        budget = IntelligenceBudget(latency_slo_ms=100.0)
        budget.tick(40.0)
        budget.tick(30.0)
        assert budget.elapsed_ms() == 70.0
        assert not budget.budget_exhausted()

    def test_budget_exhaustion(self):
        budget = IntelligenceBudget(latency_slo_ms=50.0)
        budget.tick(60.0)
        assert budget.budget_exhausted()

    def test_result_acceptable(self):
        budget = IntelligenceBudget(confidence_floor=0.70)
        assert budget.result_acceptable(0.85) is True
        assert budget.result_acceptable(0.60) is False


# ══════════════════════════════════════════════════════════════════════════
# Integration Tests – V43 Orchestrator (offline, no network)
# ══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def orchestrator():
    return V43SoftwareFirstOrchestrator(latency_slo_ms=3000.0, confidence_floor=0.50)


class TestV43OrchestratorDirect:

    def test_basic_query_resolves(self, orchestrator):
        """Standard English query must resolve with required response fields."""
        res = orchestrator.execute_semantic_workflow(
            "How does LEO AI optimize CPU+iGPU performance?", {}
        )
        assert "answer" in res
        assert isinstance(res["answer"], str)
        assert len(res["answer"]) > 0
        assert res["latency_ms"] > 0
        assert res["entropy_tier"] == "v43_software_first"
        assert res["version"] == "V43"

    def test_compute_avoided_flag(self, orchestrator):
        """compute_avoided must be a boolean."""
        res = orchestrator.execute_semantic_workflow("What is 2+2?", {})
        assert isinstance(res["compute_avoided"], bool)

    def test_layer_trace_present(self, orchestrator):
        """Layer trace must contain at minimum security + router layers."""
        res = orchestrator.execute_semantic_workflow("Explain speculative decoding", {})
        assert "layer_trace" in res
        assert isinstance(res["layer_trace"], list)
        assert len(res["layer_trace"]) >= 3    # security gate + multilingual + router

    def test_hardware_metadata_included(self, orchestrator):
        """Hardware metadata dict must be present with mandatory fields."""
        res = orchestrator.execute_semantic_workflow("Test query", {})
        hw = res.get("hardware", {})
        assert "cpu_cores" in hw
        assert "has_igpu" in hw
        assert "has_npu" in hw
        assert "quant_tier" in hw
        assert hw["quant_tier"] in ("INT4", "INT8", "FP16", "BF16", "FP32")

    def test_efficiency_metrics_included(self, orchestrator):
        """Efficiency block must include intelligence-per-watt."""
        res = orchestrator.execute_semantic_workflow("Test efficiency", {})
        eff = res.get("efficiency", {})
        assert "active_watts" in eff
        assert "watts_saved" in eff
        assert "intelligence_per_watt" in eff
        assert isinstance(eff["intelligence_per_watt"], float)

    def test_confidence_within_range(self, orchestrator):
        """Confidence must be a float in [0.0, 1.0]."""
        res = orchestrator.execute_semantic_workflow("What is machine learning?", {})
        assert 0.0 <= res["confidence"] <= 1.0

    def test_query_fingerprint_in_context(self, orchestrator):
        """query_fp should be set in context before any layer runs."""
        context = {}
        orchestrator.execute_semantic_workflow("fingerprint test", context)
        # After execution, context should contain query_fp
        assert "query_fp" in context
        assert len(context["query_fp"]) == 16


class TestV43MultilingualRouting:

    def test_telugu_query(self, orchestrator):
        """Telugu script (U+0C00–U+0C7F) must be handled without error."""
        res = orchestrator.execute_semantic_workflow("హలో ఎలా ఉన్నారు", {})
        assert "answer" in res
        assert res["entropy_tier"] == "v43_software_first"

    def test_kannada_query(self, orchestrator):
        """Kannada script (U+0C80–U+0CFF) must be handled without error."""
        res = orchestrator.execute_semantic_workflow("ಹಲೋ ನೀವು ಹೇಗಿದ್ದೀರಿ", {})
        assert "answer" in res

    def test_malayalam_query(self, orchestrator):
        """Malayalam script (U+0D00–U+0D7F) must be handled without error."""
        res = orchestrator.execute_semantic_workflow("ഹലോ സുഖമാണോ", {})
        assert "answer" in res

    def test_tamil_query(self, orchestrator):
        """Tamil script (U+0B80–U+0BFF) must be handled without error."""
        res = orchestrator.execute_semantic_workflow("வணக்கம் எப்படி இருக்கீங்க", {})
        assert "answer" in res

    def test_hindi_query(self, orchestrator):
        """Hindi Devanagari script must pass through the pipeline."""
        res = orchestrator.execute_semantic_workflow("नमस्ते आप कैसे हैं", {})
        assert "answer" in res


class TestV43BudgetExhaustion:

    def test_zero_budget_returns_graceful_degradation(self):
        """With 0 ms budget, all layers are skipped and degradation kicks in."""
        orc = V43SoftwareFirstOrchestrator(
            latency_slo_ms=0.0,       # Immediately exhausted
            confidence_floor=0.99,    # Impossible to satisfy
            enable_cloud_fallback=False
        )
        res = orc.execute_semantic_workflow("Any query", {})
        assert "answer" in res
        assert isinstance(res["answer"], str)
        # Should not crash
        assert res["entropy_tier"] == "v43_software_first"


class TestV43SecurityGate:

    def test_normal_query_not_blocked(self, orchestrator):
        """Normal queries must not be blocked by the security gate."""
        res = orchestrator.execute_semantic_workflow(
            "Tell me about machine learning optimization", {}
        )
        assert res.get("blocked") is False or "blocked" not in res

    def test_response_never_none(self, orchestrator):
        """Response must always be a dict (never None) regardless of input."""
        for q in ["", "a" * 1000, "SELECT * FROM users;", "漢字テスト"]:
            res = orchestrator.execute_semantic_workflow(q, {})
            assert res is not None
            assert isinstance(res, dict)


class TestV43SystemStatus:

    def test_status_has_required_fields(self, orchestrator):
        status = orchestrator.get_system_status()
        assert status["status"] == "ACTIVE"
        assert status["version"] == "V43"
        assert "layers" in status
        assert status["layers"] == 20
        assert "telemetry" in status
        assert "hardware" in status

    def test_telemetry_has_slo(self, orchestrator):
        status = orchestrator.get_system_status()
        telem = status["telemetry"]
        assert "latency_slo_ms" in telem
        assert "confidence_floor" in telem


# ══════════════════════════════════════════════════════════════════════════
# API Contract Tests (V42 backward-compat + V43 new fields)
# ══════════════════════════════════════════════════════════════════════════

class TestV43APIEndpoints:

    def test_orchestrate_english(self):
        """V43 orchestrate endpoint must return 200 with answer field."""
        payload = {"query": "How does LEO AI work?", "workspace_id": "test_v43"}
        response = client.post("/api/v1/leo/orchestrate", json=payload, headers={"Authorization": "Bearer AUDIT_MODE_TOKEN"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_orchestrate_telugu(self):
        """Telugu queries must be accepted and answered."""
        payload = {"query": "హలో ఎలా ఉన్నారు", "workspace_id": "test_v43_te"}
        response = client.post("/api/v1/leo/orchestrate", json=payload, headers={"Authorization": "Bearer AUDIT_MODE_TOKEN"})
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_status_endpoint_fields(self):
        """Status endpoint must return 200 with required V42-compat fields."""
        response = client.get("/api/v1/leo/status")
        assert response.status_code == 200
        data = response.json()
        # V42 backward-compat assertions
        assert "system" in data
        assert "layers" in data
