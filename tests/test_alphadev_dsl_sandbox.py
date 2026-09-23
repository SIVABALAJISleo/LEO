"""
tests/test_alphadev_dsl_sandbox.py
==================================
Unit and Integration Test Suite for:
1. AlphaDev Low-Level Algorithm Discovery (Sorting networks Sort3, Sort4, Sort5, Hashing)
2. Transformation DSL Engine (Rules, Preconditions, Postconditions, Cost Models)
3. AST Security Inspector & Secure Pathway Sandbox
4. Formal 8-Level Verification Stack (Levels 1-8)
5. Research Question Tracker (H001 - H008 Epistemic Lifecycle)
6. FastAPI Endpoints for AlphaDev, DSL, and Research Tracker
"""

import pytest
from fastapi.testclient import TestClient

from hyper.discovery.alphadev_engine import AlphaDevEngine, KernelType, DiscoveredKernel
from hyper.discovery.transformation_dsl import (
    TransformationDSLEngine,
    DSLTransformationRule,
    TransformationFamilyType,
    FailureMode,
)
from hyper.discovery.sandbox import (
    SecurePathwaySandbox,
    ASTSecurityInspector,
    SecurityViolationType,
)
from hyper.discovery.verification_stack import (
    FormalVerificationStack,
    VerificationLevel,
)
from hyper.discovery.research_tracker import (
    ResearchQuestionTracker,
    HypothesisStatus,
)
from backend.main import app


# ---------------------------------------------------------------------------
# 1. AlphaDev Low-Level Discovery Tests
# ---------------------------------------------------------------------------
def test_alphadev_sorting_networks_01_lemma():
    engine = AlphaDevEngine()

    # Sort3: 3 compare-swaps
    sort3 = engine.catalog.get("sort3")
    assert sort3 is not None
    assert sort3.instruction_count == 3
    assert engine.verify_sorting_network(sort3) is True

    # Sort4: 5 compare-swaps
    sort4 = engine.catalog.get("sort4")
    assert sort4 is not None
    assert sort4.instruction_count == 5
    assert engine.verify_sorting_network(sort4) is True

    # Sort5: 9 compare-swaps (AlphaDev / Green's network)
    sort5 = engine.catalog.get("sort5")
    assert sort5 is not None
    assert sort5.instruction_count == 9
    assert engine.verify_sorting_network(sort5) is True


def test_alphadev_execution_and_benchmark():
    engine = AlphaDevEngine()
    sort4 = engine.catalog["sort4"]

    # Test sorting arbitrary unordered lists
    assert sort4.execute([4, 2, 1, 3]) == [1, 2, 3, 4]
    assert sort4.execute([99, -5, 0, 12]) == [-5, 0, 12, 99]

    # Benchmark sorting kernel
    benchmarked = engine.benchmark_sorting_kernel(sort4, trials=500)
    assert benchmarked.measured_latency_ns > 0
    assert benchmarked.baseline_latency_ns > 0
    assert benchmarked.measured_speedup > 0


def test_alphadev_branch_free_hashing():
    engine = AlphaDevEngine()
    hash_k = engine.discover_branch_free_hash("murmur_style_32")
    assert hash_k.kernel_type == KernelType.HASH_FUNCTION
    assert hash_k.is_branch_free is True
    assert hash_k.is_verified is True


# ---------------------------------------------------------------------------
# 2. Transformation DSL Tests
# ---------------------------------------------------------------------------
def test_transformation_dsl_horner_rule():
    dsl = TransformationDSLEngine()
    rule = dsl.get_rule("dsl-math-horner")
    assert rule is not None
    assert rule.family == TransformationFamilyType.MATHEMATICAL

    # Precondition pass
    coeffs = [0.1, 0.2, 0.3, 0.4]
    ok, _ = rule.check_precondition(state=1.005, meta={"coeffs": coeffs})
    assert ok is True

    # Precondition fail (missing coeffs)
    fail_ok, reason = rule.check_precondition(state=1.005, meta={})
    assert fail_ok is False

    # Apply transformation
    success, result, failure_mode, msg = rule.apply(state=2.0, meta={"coeffs": [1.0, 2.0, 3.0]})
    assert success is True
    # 1 + 2*2 + 3*(2^2) = 1 + 4 + 12 = 17.0
    assert result == 17.0
    assert failure_mode is None


def test_transformation_dsl_sort3_rule():
    dsl = TransformationDSLEngine()
    rule = dsl.get_rule("dsl-algo-sort3")
    assert rule is not None

    # Apply Sort3
    success, result, failure_mode, msg = rule.apply(state=[9, 1, 5], meta={})
    assert success is True
    assert result == [1, 5, 9]

    # Precondition failure on invalid size
    fail_suc, _, fail_mode, _ = rule.apply(state=[1, 2], meta={})
    assert fail_suc is False
    assert fail_mode == FailureMode.PRECONDITION_VIOLATED


def test_transformation_dsl_residual_delta():
    dsl = TransformationDSLEngine()
    rule = dsl.get_rule("dsl-escape-delta")
    assert rule is not None

    success, res, _, _ = rule.apply(
        state=105.0,
        meta={"prev_input": 100.0, "prev_output": 500.0},
    )
    assert success is True
    assert res == 505.0  # 500 + (105 - 100)


# ---------------------------------------------------------------------------
# 3. AST Security Inspector & Sandbox Tests
# ---------------------------------------------------------------------------
def test_ast_security_blocks_malicious_code():
    malicious_code_1 = "import os; os.system('echo hacked')"
    audit_1 = ASTSecurityInspector.audit_source_code(malicious_code_1)
    assert audit_1.is_safe is False
    assert audit_1.violation_type == SecurityViolationType.FORBIDDEN_IMPORT

    malicious_code_2 = "import subprocess; subprocess.Popen(['calc'])"
    audit_2 = ASTSecurityInspector.audit_source_code(malicious_code_2)
    assert audit_2.is_safe is False

    malicious_code_3 = "eval('__import__(\"os\").remove(\"foo\")')"
    audit_3 = ASTSecurityInspector.audit_source_code(malicious_code_3)
    assert audit_3.is_safe is False

    clean_code = "def add(x, y):\n    return x + y\n"
    audit_clean = ASTSecurityInspector.audit_source_code(clean_code)
    assert audit_clean.is_safe is True
    assert len(audit_clean.violations) == 0


def test_secure_sandbox_execution():
    sandbox = SecurePathwaySandbox(default_timeout_s=1.0)

    # Clean function execution
    def fast_fn(x):
        return x * 2

    res = sandbox.run_callable(fast_fn, 21)
    assert res.success is True
    assert res.output == 42
    assert res.elapsed_ms > 0

    # Infinite loop / Timeout execution
    def infinite_fn(x):
        import time
        time.sleep(2.0)
        return x

    res_timeout = sandbox.run_callable(infinite_fn, 10, timeout_s=0.2)
    assert res_timeout.success is False
    assert "timeout" in res_timeout.error_message.lower()


# ---------------------------------------------------------------------------
# 4. Formal 8-Level Verification Stack Tests
# ---------------------------------------------------------------------------
def test_verification_stack_exact_match():
    stack = FormalVerificationStack()

    def cand_fn(arr):
        return sorted(arr)

    def ref_fn(arr):
        return list(sorted(arr))

    report = stack.evaluate_candidate(
        candidate_fn=cand_fn,
        reference_fn=ref_fn,
        sample_input=[3, 1, 2],
        is_exact=True,
    )
    assert report.all_levels_passed is False  # Level 8 formal proof was not attached
    assert report.highest_passed_level == 7   # Passed Levels 1 through 7
    assert report.epistemic_state == "EMPIRICALLY_VERIFIED"


def test_verification_stack_numerical_with_proof():
    stack = FormalVerificationStack()

    coeffs = [1.0, 2.0, 3.0]
    def cand_horner(x):
        return coeffs[0] + x * (coeffs[1] + x * coeffs[2])

    def ref_naive(x):
        return coeffs[0] + coeffs[1] * x + coeffs[2] * (x ** 2)

    def formal_proof():
        # Symbolic deduction: c0 + c1*x + c2*x^2 == c0 + x*(c1 + x*c2)
        return True

    report = stack.evaluate_candidate(
        candidate_fn=cand_horner,
        reference_fn=ref_naive,
        sample_input=1.5,
        is_exact=False,
        atol=1e-8,
        rtol=1e-8,
        formal_proof_fn=formal_proof,
    )
    assert report.highest_passed_level == 8
    assert report.all_levels_passed is True
    assert report.epistemic_state == "FORMALLY_PROVED"


# ---------------------------------------------------------------------------
# 5. Research Question Tracker Tests (H001 - H008)
# ---------------------------------------------------------------------------
def test_research_question_tracker():
    tracker = ResearchQuestionTracker()
    summary = tracker.get_summary()
    assert summary["total_hypotheses"] == 8

    # Check H001 (supported by Horner & Tensor contractions)
    h001 = tracker.get_hypothesis("H001")
    assert h001 is not None
    assert h001.hypothesis_id == "H001"

    # Add 3rd evidence to trigger SUPPORTED
    h001.record_evidence(
        workload_name="FFT_Convolution",
        speedup=12.4,
        description="O(N log N) frequency domain convolution verified.",
        is_verified=True,
    )
    assert h001.status == HypothesisStatus.SUPPORTED


# ---------------------------------------------------------------------------
# 6. FastAPI Router Endpoints for AlphaDev, DSL, and Research Tracker
# ---------------------------------------------------------------------------
def test_router_new_discovery_endpoints():
    client = TestClient(app)

    # AlphaDev catalog
    resp = client.get("/api/v1/discovery/alphadev/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_kernels"] >= 3

    # AlphaDev benchmark
    resp_bench = client.post("/api/v1/discovery/alphadev/benchmark", json={"kernel_key": "sort4", "trials": 100})
    assert resp_bench.status_code == 200
    bench_data = resp_bench.json()
    assert "measured_speedup" in bench_data

    # DSL rules
    resp_dsl = client.get("/api/v1/discovery/dsl/rules")
    assert resp_dsl.status_code == 200
    dsl_data = resp_dsl.json()
    assert dsl_data["total_rules"] >= 3

    # Research Tracker
    resp_res = client.get("/api/v1/discovery/research-tracker")
    assert resp_res.status_code == 200
    res_data = resp_res.json()
    assert res_data["total_hypotheses"] == 8
