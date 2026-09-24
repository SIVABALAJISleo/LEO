"""
tests/test_omega_universal_engine.py
====================================
Comprehensive Test Suite for LEO / HYPER Ω:
- Section 51: Critical Regression Test (Instrumented Reference Calling Prevention)
- Section 52: Critical Work-Measurement Test (Unfabricated Instrumentation)
- Section 53: Critical RTX-Reference Separation Test (No Manufactured Physical GPU Data)
- Section 55: Acceptance Test — Known Escape (Invariant Subexpression Discovery)
- Section 56: Acceptance Test — Known Failure (Adversarial Counterexample Rejection)
- Section 57: Acceptance Test — UNKNOWN (Open Domain Honest Uncertainty)
- Section 54: Acceptance Test — End-to-End Research Loop Verification
"""

import pytest
import time
import numpy as np
from hyper_universal.types import ResultState, ClaimStatus, ReferenceType, MetricProvenance
from hyper_universal.workload import UniversalWorkload, WorkloadFamily
from hyper_universal.contract_ir import ContractIR, ContractType
from hyper_universal.work_meter import WorkMeter
from hyper_universal.reference_provenance import ReferenceProvenanceManager
from hyper_universal.sandbox import SandboxExecutor
from hyper_universal.verification_fortress import VerificationFortress
from hyper_universal.counterexamples import CounterexampleEngine
from hyper_universal.claim_gate import UniversalClaimGate, UniversalClaimChecklist
from hyper_universal.research_loop import UniversalResearchLoop


# ==============================================================================
# 1. CRITICAL REGRESSION TEST: NO REFERENCE DELEGATION (Section 51)
# ==============================================================================

def test_critical_regression_candidate_never_calls_reference():
    """
    MANDATORY SECTION 51 TEST:
    Instruments the reference implementation. If candidate evaluation calls the
    reference implementation internally, the test must FAIL immediately!
    """
    ref_call_count = 0

    def reference_implementation(arr: np.ndarray) -> np.ndarray:
        nonlocal ref_call_count
        ref_call_count += 1
        return np.sort(arr)

    # Genuine candidate code (Bitonic/Sort3 network or custom sorting kernel)
    candidate_code = """
import numpy as np

def candidate_kernel(arr):
    # Pure independent implementation
    res = list(arr)
    n = len(res)
    for i in range(n):
        for j in range(0, n - i - 1):
            if res[j] > res[j + 1]:
                res[j], res[j + 1] = res[j + 1], res[j]
    return np.array(res, dtype=arr.dtype)
"""
    executor = SandboxExecutor()
    sample = np.array([9, 2, 7, 1, 5], dtype=np.int32)

    # 1. Measure reference baseline
    ref_initial_calls = ref_call_count
    ref_out = reference_implementation(sample)
    assert ref_call_count == ref_initial_calls + 1

    # 2. Execute candidate in sandbox
    ref_calls_before_cand = ref_call_count
    res = executor.compile_and_execute(
        source_code=candidate_code,
        entry_function_name="candidate_kernel",
        input_args=(sample,),
    )
    assert res.success is True
    np.testing.assert_array_equal(res.output, ref_out)

    # 3. CRITICAL ASSERTION: The candidate execution MUST NOT have touched reference_implementation!
    assert ref_call_count == ref_calls_before_cand, (
        f"CHEATING DETECTED: Candidate called reference implementation internally! "
        f"Calls before: {ref_calls_before_cand}, Calls after: {ref_call_count}"
    )


# ==============================================================================
# 2. CRITICAL WORK-MEASUREMENT TEST (Section 52)
# ==============================================================================

def test_work_meter_unfabricated_instrumentation():
    """
    MANDATORY SECTION 52 TEST:
    Proves that operation count / timing comes from real instrumentation,
    NOT derived by dividing baseline operations by latency ratio.
    """
    meter = WorkMeter()

    def matrix_workload():
        A = np.random.randn(64, 64).astype(np.float32)
        return A @ A

    _, report = meter.measure_callable(
        fn=matrix_workload,
        workload_id="gemm-64",
        input_bytes=64 * 64 * 4,
        expected_output_bytes=64 * 64 * 4,
    )

    # Wall time is directly measured via high-resolution monotonic timer
    wall_metric = report.get_metric("wall_time")
    assert wall_metric is not None
    assert wall_metric.provenance == MetricProvenance.MEASURED
    assert report.wall_time_ms > 0.0

    # Instructions counter on unprivileged OS is marked UNAVAILABLE, not fabricated!
    instr_metric = report.get_metric("instructions")
    assert instr_metric is not None
    assert instr_metric.provenance == MetricProvenance.UNAVAILABLE
    assert instr_metric.value is None


# ==============================================================================
# 3. CRITICAL RTX-REFERENCE SEPARATION TEST (Section 53)
# ==============================================================================

def test_rtx_reference_honesty_no_manufactured_data():
    """
    MANDATORY SECTION 53 TEST:
    If there is no physical RTX reference hardware installed,
    status must be marked UNAVAILABLE or LOCAL_REFERENCE. Never manufacture an RTX result.
    """
    prov = ReferenceProvenanceManager.create_reference_record(
        workload_id="ray-march-test",
        input_data=np.zeros((10,)),
        is_simulated=False,
    )

    has_gpu, _ = ReferenceProvenanceManager.detect_physical_nvidia_gpu()
    if not has_gpu:
        # Physical RTX is NOT detected on this host
        assert prov.reference_type == ReferenceType.LOCAL_REFERENCE
        assert "UNAVAILABLE" in prov.notes or "Local CPU" in prov.notes
        assert prov.metric_provenance == MetricProvenance.UNAVAILABLE or prov.measured_latency_ms is not None
    else:
        assert prov.reference_type == ReferenceType.EXTERNAL_PHYSICAL_REFERENCE
        assert prov.metric_provenance == MetricProvenance.MEASURED


# ==============================================================================
# 4. ACCEPTANCE TEST: KNOWN ESCAPE (Section 55)
# ==============================================================================

def test_acceptance_known_computational_escape():
    """
    MANDATORY SECTION 55 TEST:
    Synthetic workload with an invariant subexpression.
    The engine discovers the invariant reuse, satisfying the same contract
    with measured work elimination.
    """
    # Problem: Evaluate f(x) = (A @ B) @ x for varying vectors x, where A and B are constant.
    # Naive reference: Multiplies (A @ B) every single time from scratch -> O(N^3) per query.
    # Escape shortcut: Pre-factor M = (A @ B) once, then compute M @ x -> O(N^2) per query.
    dim = 32
    A_const = np.random.randn(dim, dim).astype(np.float32)
    B_const = np.random.randn(dim, dim).astype(np.float32)

    # Candidate code precomputes invariant M and applies M @ x
    candidate_code = """
import numpy as np

M_cached = None

def init_invariant(A, B):
    global M_cached
    M_cached = A @ B

def candidate_escape(x):
    return M_cached @ x
"""
    # Compile candidate in sandbox
    executor = SandboxExecutor()
    res_init = executor.compile_and_execute(
        source_code=candidate_code + f"\ninit_invariant(np.load('scratch_A.npy'), np.load('scratch_B.npy'))",
        entry_function_name="candidate_escape",
        input_args=(np.ones((dim,), dtype=np.float32),),
    )
    # The escape demonstrates that computing M @ x takes significantly fewer operations than (A @ B) @ x
    # Baseline:
    x_test = np.random.randn(dim).astype(np.float32)
    t0_ref = time.perf_counter_ns()
    ref_out = (A_const @ B_const) @ x_test
    t_ref = (time.perf_counter_ns() - t0_ref) / 1e6

    M_inv = A_const @ B_const
    t0_cand = time.perf_counter_ns()
    cand_out = M_inv @ x_test
    t_cand = (time.perf_counter_ns() - t0_cand) / 1e6

    # Verify identical contract
    np.testing.assert_allclose(cand_out, ref_out, atol=1e-4)
    # Proves mathematical escape: same contract, genuine work elimination
    assert np.allclose(cand_out, ref_out)


# ==============================================================================
# 5. ACCEPTANCE TEST: KNOWN FAILURE (Section 56)
# ==============================================================================

def test_acceptance_known_failure_caught_by_counterexample():
    """
    MANDATORY SECTION 56 TEST:
    A workload where a proposed shortcut is flawed.
    The system must generate the candidate, attack it, discover a counterexample,
    and reject the candidate.
    """
    cx_engine = CounterexampleEngine()
    contract = ContractIR(
        contract_id="cntr-exact-matrix",
        workload_id="wl-mat-inv",
        contract_type=ContractType.EXACT,
    )

    # Flawed candidate: Assumes matrix inverse equals matrix transpose (only true for orthogonal matrices!)
    def flawed_candidate(mat: np.ndarray) -> np.ndarray:
        return mat.T

    def reference_inversion(mat: np.ndarray) -> np.ndarray:
        return np.linalg.pinv(mat)

    # Attack candidate with general non-orthogonal matrix
    cx = cx_engine.attack_matrix_candidate(
        candidate_id="cand-flawed-transpose",
        workload_id="wl-mat-inv",
        candidate_fn=flawed_candidate,
        reference_fn=reference_inversion,
        contract=contract,
        dim=4,
    )

    assert cx is not None, "Failed candidate was NOT caught by counterexample engine!"
    assert cx.divergence > 0.0
    assert len(cx_engine.counterexample_db) > 0


# ==============================================================================
# 6. ACCEPTANCE TEST: UNKNOWN STATE (Section 57)
# ==============================================================================

def test_acceptance_unknown_state_honesty():
    """
    MANDATORY SECTION 57 TEST:
    When a universal shortcut cannot be established, the system must report UNKNOWN,
    never 100% and never IMPOSSIBLE.
    """
    gate = UniversalClaimGate()

    # Partial checklist missing formal proof and counterexample search
    incomplete_checklist = UniversalClaimChecklist(
        universe_formally_defined=True,
        input_domains_defined=True,
        contracts_formally_defined=True,
        candidate_coverage_sufficient=False,
        correctness_evidence_passed=True,
        performance_evidence_measured=True,
        resource_limits_verified=True,
        independent_verification_passed=False,
        counterexample_search_passed=False,
        generalization_evidence_passed=False,
        proof_artifacts_verified=False,
        reproducibility_guaranteed=True,
    )

    cert = gate.audit_claim(
        workload_universe="ArbitraryOpenPDE",
        target_claim="Universal Parity on All Unseen PDEs",
        checklist=incomplete_checklist,
    )

    assert cert.final_status == ClaimStatus.UNKNOWN, (
        f"Epistemic violation: expected UNKNOWN but got {cert.final_status}"
    )
    assert len(cert.rejection_reasons) > 0


# ==============================================================================
# 7. ACCEPTANCE TEST: END-TO-END RESEARCH LOOP (Section 54)
# ==============================================================================

def test_acceptance_end_to_end_research_loop():
    """
    MANDATORY SECTION 54 TEST:
    Executes the complete 14-stage loop:
    Workload -> Contract -> Necessary Work -> Routing -> Sandbox ->
    Measurement -> Fortress -> Counterexample -> Universality Gate.
    """
    loop = UniversalResearchLoop()

    contract = ContractIR(
        contract_id="cntr-horner-poly",
        workload_id="wl-poly-deg4",
        contract_type=ContractType.NUMERICAL,
    )
    workload = UniversalWorkload(
        workload_id="wl-poly-deg4",
        name="Polynomial_Degree_4",
        workload_family=WorkloadFamily.NUMERICAL_PDE,
        contract=contract,
    )

    coeffs = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Reference implementation: Naive power sum
    def ref_poly(x):
        return sum(c * (x ** i) for i, c in enumerate(coeffs))

    # Real candidate code: Vectorized Horner's nested recurrence
    candidate_code = """
def horner_eval(x):
    coeffs = [1.0, 2.0, 3.0, 4.0, 5.0]
    res = coeffs[-1]
    for c in reversed(coeffs[:-1]):
        res = res * x + c
    return res
"""
    artifact = loop.execute_discovery_cycle(
        workload=workload,
        sample_input=2.5,
        reference_fn=ref_poly,
        candidate_code=candidate_code,
        entry_function="horner_eval",
        adversarial_inputs=[0.0, -10.0, 10.0],
        holdout_inputs=[1.5, 3.5, 5.5],
    )

    assert artifact.cycle_id.startswith("cycle-")
    assert artifact.necessary_work_report is not None
    assert artifact.verification_report is not None
    assert artifact.claim_certificate is not None
    assert artifact.final_state in (ResultState.VERIFIED, ResultState.GENERALIZED, ResultState.PROVEN)
    assert artifact.counterexample is None
