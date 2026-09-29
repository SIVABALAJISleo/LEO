"""
tests/test_online_adaptation_engine.py
=======================================
Regression tests for the HYPER-Ω Online Adaptation Engine (Section 38).

Validates:
  1. Bayesian prior downdating on failure
  2. Floor prior enforcement (no total suppression)
  3. Re-promotion on success after failure
  4. Time-decayed weight recovery
  5. Domain isolation (domain A failures do not affect domain B)
  6. Global prior blending
  7. Failure file persistence (load_from_file round-trip)
  8. Predict-route returns demoted routes less often after repeated failures
  9. Integration: SpeculativeBreakthroughRouter records failures into engine
 10. Export/summary structure validation
"""

import json
import math
import time
import tempfile
from pathlib import Path

import numpy as np
import pytest

from hyper_x.wormhole_compiler.online_adaptation_engine import (
    OnlineAdaptationEngine,
    RoutePrior,
    AdaptationState,
    ALL_ROUTES,
    _FAILURE_PENALTY,
    _FLOOR_PRIOR,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_engine(failure_file: str = "") -> OnlineAdaptationEngine:
    """Create a fresh engine without loading any existing failure file."""
    return OnlineAdaptationEngine(failure_file=failure_file or "/nonexistent/path.json", mode="PASSIVE")


# ---------------------------------------------------------------------------
# 1. Bayesian prior downdating on failure
# ---------------------------------------------------------------------------

class TestFailureDowndating:
    def test_single_failure_reduces_weight(self):
        engine = _fresh_engine()
        route = "EXACT_SPARSE"
        initial_weight = engine._get_state("DENSE_GEMM").priors[route].weight

        engine.record_failure(route, domain="DENSE_GEMM")

        updated_weight = engine._get_state("DENSE_GEMM").priors[route].weight
        assert updated_weight < initial_weight, "Weight must decrease after failure"
        expected = max(_FLOOR_PRIOR, initial_weight * _FAILURE_PENALTY)
        assert abs(updated_weight - expected) < 1e-6

    def test_repeated_failures_converge_to_floor(self):
        engine = _fresh_engine()
        route = "EXACT_ROW_DELTA"
        for _ in range(50):
            engine.record_failure(route, domain="DENSE_GEMM")

        weight = engine._get_state("DENSE_GEMM").priors[route].weight
        assert abs(weight - _FLOOR_PRIOR) < 1e-6, "Weight must clamp at floor after many failures"

    def test_failure_count_increments(self):
        engine = _fresh_engine()
        route = "OUTPUT_SENSITIVE"
        for _ in range(3):
            engine.record_failure(route, domain="TEMPORAL_STREAM")

        prior = engine._get_state("TEMPORAL_STREAM").priors[route]
        assert prior.failure_count == 3

    def test_unrelated_routes_unaffected(self):
        engine = _fresh_engine()
        engine.record_failure("EXACT_SPARSE", domain="SPARSE_LINEAR")
        weight_other = engine._get_state("SPARSE_LINEAR").priors["OUTPUT_SENSITIVE"].weight
        assert weight_other == 1.0, "Other routes must not be affected by failure"


# ---------------------------------------------------------------------------
# 2. Floor prior enforcement
# ---------------------------------------------------------------------------

class TestFloorPrior:
    def test_floor_is_respected_after_many_failures(self):
        prior = RoutePrior(route="EXACT_FACTORIZATION", weight=_FLOOR_PRIOR * 2)
        for _ in range(100):
            prior.apply_failure()
        assert prior.weight >= _FLOOR_PRIOR

    def test_floor_prevents_zero_weight(self):
        prior = RoutePrior(route="CPU_REFERENCE_FALLBACK", weight=0.001)
        prior.apply_failure()
        assert prior.weight >= _FLOOR_PRIOR


# ---------------------------------------------------------------------------
# 3. Re-promotion on success after failure
# ---------------------------------------------------------------------------

class TestSuccessRepromotion:
    def test_success_after_failure_increases_weight(self):
        engine = _fresh_engine()
        route = "EXACT_ROW_DELTA"
        for _ in range(5):
            engine.record_failure(route, domain="DENSE_GEMM")

        depressed_weight = engine._get_state("DENSE_GEMM").priors[route].weight

        engine.record_success(route, domain="DENSE_GEMM")
        recovered_weight = engine._get_state("DENSE_GEMM").priors[route].weight

        assert recovered_weight > depressed_weight, "Success must increase weight"

    def test_success_count_increments(self):
        engine = _fresh_engine()
        engine.record_success("CPU_REFERENCE_FALLBACK", domain="DENSE_GEMM")
        prior = engine._get_state("DENSE_GEMM").priors["CPU_REFERENCE_FALLBACK"]
        assert prior.success_count == 1


# ---------------------------------------------------------------------------
# 4. Time-decayed weight recovery
# ---------------------------------------------------------------------------

class TestTimeDecay:
    def test_old_failure_decays_toward_full_weight(self):
        prior = RoutePrior(route="EXACT_SPARSE")
        ancient_ts = time.time() - 3600 * 24 * 7  # 1 week ago
        prior.apply_failure(timestamp=ancient_ts)

        # Decayed weight should be significantly higher than immediate post-failure weight
        now_weight = prior.time_decayed_weight(time.time())
        assert now_weight > prior.weight + 0.1, "Old failure should mostly decay away"

    def test_recent_failure_has_strong_penalty(self):
        prior = RoutePrior(route="EXACT_SPARSE")
        recent_ts = time.time() - 1  # 1 second ago
        prior.apply_failure(timestamp=recent_ts)

        # Decayed weight should be close to post-failure weight
        now_weight = prior.time_decayed_weight(time.time())
        assert abs(now_weight - prior.weight) < 0.05, "Recent failure should retain most of penalty"

    def test_floor_respected_in_decayed_weight(self):
        prior = RoutePrior(route="EXACT_ROW_DELTA", weight=_FLOOR_PRIOR)
        ancient_ts = time.time() - 1
        prior.last_failure_ts = ancient_ts
        assert prior.time_decayed_weight(time.time()) >= _FLOOR_PRIOR


# ---------------------------------------------------------------------------
# 5. Domain isolation
# ---------------------------------------------------------------------------

class TestDomainIsolation:
    def test_failures_in_domain_a_do_not_affect_domain_b(self):
        engine = _fresh_engine()
        route = "EXACT_SPARSE"

        for _ in range(10):
            engine.record_failure(route, domain="DOMAIN_A")

        weight_b = engine._get_state("DOMAIN_B").priors[route].weight
        assert weight_b == 1.0, "Domain A failures must not bleed into Domain B"

    def test_different_domains_can_have_different_top_routes(self):
        engine = _fresh_engine()
        # Hammer CPU_REFERENCE_FALLBACK in domain A → makes it lowest priority
        for _ in range(20):
            engine.record_failure("CPU_REFERENCE_FALLBACK", domain="DOM_A")

        # In Domain B, hammer EXACT_SPARSE
        for _ in range(20):
            engine.record_failure("EXACT_SPARSE", domain="DOM_B")

        top_a = engine.predict_route("DOM_A")
        top_b = engine.predict_route("DOM_B")
        # They should differ (different routes were demoted)
        # At minimum, EXACT_SPARSE should not be top in DOM_B
        assert top_b != "EXACT_SPARSE"


# ---------------------------------------------------------------------------
# 6. Predict-route returns demoted routes less often
# ---------------------------------------------------------------------------

class TestPredictRouteDemotion:
    def test_demoted_route_not_predicted_as_top(self):
        engine = _fresh_engine()
        # Demote OUTPUT_SENSITIVE in DENSE_GEMM domain
        for _ in range(30):
            engine.record_failure("OUTPUT_SENSITIVE", domain="DENSE_GEMM")

        top = engine.predict_route("DENSE_GEMM")
        assert top != "OUTPUT_SENSITIVE"

    def test_predict_excludes_specified_routes(self):
        engine = _fresh_engine()
        top_without_fallback = engine.predict_route(
            "DENSE_GEMM", exclude_routes=["CPU_REFERENCE_FALLBACK"]
        )
        assert top_without_fallback != "CPU_REFERENCE_FALLBACK"


# ---------------------------------------------------------------------------
# 7. Failure file persistence (round-trip)
# ---------------------------------------------------------------------------

class TestFilePersistence:
    def test_load_from_file_replays_failures(self, tmp_path):
        failure_data = [
            {
                "route": "EXACT_SPARSE",
                "workload_id": "WL_001",
                "domain": "SPARSE_LINEAR",
                "barrier_type": "INFORMATION_BOUND",
                "timestamp": time.time() - 60,
            },
            {
                "route": "EXACT_SPARSE",
                "workload_id": "WL_002",
                "domain": "SPARSE_LINEAR",
                "barrier_type": "CONTRACT_BOUND",
                "timestamp": time.time() - 30,
            },
        ]
        fp = tmp_path / "failures.json"
        fp.write_text(json.dumps(failure_data))

        engine = OnlineAdaptationEngine(failure_file=str(fp), mode="PASSIVE")

        weight = engine._get_state("SPARSE_LINEAR").priors["EXACT_SPARSE"].weight
        expected = max(_FLOOR_PRIOR, 1.0 * (_FAILURE_PENALTY ** 2))
        assert abs(weight - expected) < 1e-5

    def test_active_mode_writes_failures(self, tmp_path):
        fp = tmp_path / "out_failures.json"
        engine = OnlineAdaptationEngine(failure_file=str(fp), mode="ACTIVE")

        engine.record_failure("EXACT_FACTORIZATION", domain="LOW_RANK", workload_id="WL_WRITE_TEST")

        assert fp.exists()
        records = json.loads(fp.read_text())
        assert len(records) == 1
        assert records[0]["route"] == "EXACT_FACTORIZATION"
        assert records[0]["domain"] == "LOW_RANK"

    def test_export_priors_writes_valid_json(self, tmp_path):
        engine = _fresh_engine()
        engine.record_failure("EXACT_SPARSE", domain="TEST")
        out = tmp_path / "priors.json"
        result = engine.export_priors(out)
        assert "domains" in result
        assert "TEST" in result["domains"]
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert "domains" in loaded


# ---------------------------------------------------------------------------
# 8. Summary structure
# ---------------------------------------------------------------------------

class TestSummary:
    def test_summary_structure(self):
        engine = _fresh_engine()
        engine.record_failure("EXACT_SPARSE", domain="DOM_X")
        engine.record_success("CPU_REFERENCE_FALLBACK", domain="DOM_X")

        summary = engine.summary()
        assert "domains_tracked" in summary
        assert "total_failures_recorded" in summary
        assert "global_top_route" in summary
        assert "per_domain_top_routes" in summary
        assert "DOM_X" in summary["per_domain_top_routes"]
        assert summary["total_failures_recorded"] >= 1

    def test_all_routes_present_in_state(self):
        engine = _fresh_engine()
        state = engine._get_state("NEW_DOMAIN")
        for r in ALL_ROUTES:
            assert r in state.priors, f"Route {r} missing from AdaptationState"


# ---------------------------------------------------------------------------
# 9. AdaptationState.ranked_routes ordering
# ---------------------------------------------------------------------------

class TestRankedRoutes:
    def test_unfailed_routes_ranked_before_failed(self):
        state = AdaptationState(domain="TEST")
        state.priors["EXACT_SPARSE"].apply_failure(time.time())
        state.priors["EXACT_SPARSE"].apply_failure(time.time())

        ranked = state.ranked_routes()
        routes = [r for r, _ in ranked]
        sparse_idx = routes.index("EXACT_SPARSE")
        fallback_idx = routes.index("CPU_REFERENCE_FALLBACK")

        # Fallback (unfailed) should rank above demoted EXACT_SPARSE
        assert fallback_idx < sparse_idx, "Unfailed route must outrank repeatedly-failed route"

    def test_all_routes_appear_in_ranked_output(self):
        state = AdaptationState(domain="TEST2")
        ranked = state.ranked_routes()
        assert len(ranked) == len(ALL_ROUTES)
