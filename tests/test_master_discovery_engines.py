"""
tests/test_master_discovery_engines.py
======================================
Comprehensive verification test suite for the Master Discovery Engines:
- Phase 2: Canonical Workload Model & Contract Extractor (Sections 5 & 6)
- Phase 3: Necessary-Work Information-Theoretic Analyzer (Section 7)
- Phase 15/16: Theorem Discovery & Performance Proof Engine (Sections 24 & 25)
- Phase 17: Complexity Lower-Bound & Computational Barrier Engine (Section 26)
- Sections 31 & 34: Universality Gate & 16-State Result Machine
"""

import pytest
import numpy as np
from hyper.discovery.workload_model import (
    CanonicalWorkload,
    ExtractedContract,
    ContractExactnessType,
    WorkloadPrecision,
    ContractExtractor,
)
from hyper.discovery.necessary_work_analyzer import (
    NecessaryWorkAnalyzer,
    OperationNecessity,
)
from hyper.discovery.theorem_engine import (
    TheoremDiscoveryEngine,
    TheoremType,
    TheoremStatus,
)
from hyper.discovery.barrier_engine import (
    BarrierEngine,
    BarrierClassification,
    BarrierType,
    HostHardwareModel,
)
from hyper.discovery.universality_gate import (
    UniversalityGate,
    UniversalityGateChecklist,
    DiscoveryResultState,
)


# ==============================================================================
# 1. CANONICAL WORKLOAD & CONTRACT EXTRACTOR TESTS (Sections 5 & 6)
# ==============================================================================

def test_canonical_workload_contract_extraction():
    """Verify automatic contract extraction and categorization."""
    # Test an exact workload (sorting)
    sample_arr = np.array([5, 2, 8, 1, 9], dtype=np.int32)
    workload_sort = ContractExtractor.extract_from_callable(
        fn=np.sort,
        sample_input=sample_arr,
        name="Sort_Int32",
        domain="SORTING",
    )
    assert workload_sort.contract.exactness_type == ContractExactnessType.EXACT
    assert workload_sort.contract.absolute_tolerance == 0.0
    assert not workload_sort.contract.allows_approximation
    assert len(workload_sort.compute_workload_hash()) == 16


def test_contract_non_silent_relaxation_guard():
    """Verify that EXACT contracts strictly forbid silent relaxation."""
    sample_arr = np.array([1, 2, 3], dtype=np.int32)
    workload = ContractExtractor.extract_from_callable(
        fn=lambda x: x,
        sample_input=sample_arr,
        name="ExactIdentity",
        force_exact=True,
    )
    with pytest.raises(ValueError, match="Forbidden"):
        workload.contract.relax_to_tolerance(1e-3, 1e-3, "Attempted silent relaxation")


def test_tolerant_contract_relaxation_tracking():
    """Verify that tolerant contracts can relax, but append audit history."""
    sample_mat = np.random.randn(16, 16).astype(np.float32)
    workload = ContractExtractor.extract_from_callable(
        fn=lambda x: x @ x,
        sample_input=sample_mat,
        name="MatrixMultiplication",
        domain="LINEAR_ALGEBRA",
    )
    assert workload.contract.exactness_type == ContractExactnessType.NUMERICALLY_TOLERANT
    workload.contract.relax_to_tolerance(1e-2, 1e-2, "Relaxed for int8 quantization test")
    assert workload.contract.absolute_tolerance == 1e-2
    assert len(workload.contract.relaxation_history) == 1
    assert "int8 quantization" in workload.contract.relaxation_history[0]


# ==============================================================================
# 2. NECESSARY-WORK INFORMATION-THEORETIC ENGINE TESTS (Section 7)
# ==============================================================================

def test_necessary_work_analysis_classification():
    """Verify classification of operations into Necessary, Redundant, Fusible, Reusable."""
    analyzer = NecessaryWorkAnalyzer()
    operations = [
        {"op_id": "op_0", "name": "copy_tensor", "op_type": "CAST", "flops": 10.0},
        {"op_id": "op_1", "name": "matmul_core", "op_type": "GEMM", "flops": 1000.0},
        {"op_id": "op_2", "name": "bias_add", "op_type": "FUSED_ADD", "flops": 50.0},
        {"op_id": "op_3", "name": "static_ambient_light", "op_type": "CONSTANT", "flops": 100.0},
        {"op_id": "op_4", "name": "unreferenced_debug", "op_type": "DEBUG", "flops": 40.0, "outputs": ["_unused_dbg"]},
    ]

    graph = analyzer.analyze_graph(workload_id="wl-test", operations=operations, contract_exactness="NUMERICALLY_TOLERANT")
    assert graph.nodes["op_0"].necessity == OperationNecessity.REDUNDANT
    assert graph.nodes["op_1"].necessity == OperationNecessity.NECESSARY
    assert graph.nodes["op_2"].necessity == OperationNecessity.FUSIBLE
    assert graph.nodes["op_3"].necessity == OperationNecessity.REUSABLE
    assert graph.nodes["op_4"].necessity == OperationNecessity.ELIMINABLE

    # Check work reduction metrics
    assert graph.potential_work_reduction_pct > 0.0
    assert graph.necessary_flops == 1000.0


# ==============================================================================
# 3. THEOREM DISCOVERY & PERFORMANCE PROOF TESTS (Sections 24 & 25)
# ==============================================================================

def test_zero_one_sorting_lemma_formal_proof():
    """Verify formal proof of 0-1 sorting lemma on known sorting networks."""
    engine = TheoremDiscoveryEngine()

    # Optimal 3-element sorting network (3 comparators: (0,1), (0,2), (1,2))
    # Correct 3-sorter:
    net_sort3 = [(0, 1), (0, 2), (1, 2)]
    cert_3 = engine.prove_zero_one_sorting_lemma(n=3, comparator_network=net_sort3)
    assert cert_3.status == TheoremStatus.PROVEN
    assert cert_3.verified_by_formal_checker is True
    assert len(cert_3.counterexamples) == 0

    # Defective 3-element network (missing (1,2)):
    defective_net = [(0, 1)]
    cert_defective = engine.prove_zero_one_sorting_lemma(n=3, comparator_network=defective_net)
    assert cert_defective.status == TheoremStatus.COUNTEREXAMPLE_FOUND
    assert cert_defective.verified_by_formal_checker is False
    assert len(cert_defective.counterexamples) > 0


def test_symbolic_polynomial_horner_theorem_proof():
    """Verify formal symbolic equivalence proof between polynomial and Horner recurrence."""
    engine = TheoremDiscoveryEngine()
    cert = engine.prove_symbolic_polynomial_identity(degree=4)
    # SymPy is available, should prove exactly
    assert cert.status == TheoremStatus.PROVEN
    assert cert.verified_by_formal_checker is True


def test_performance_upper_bound_theorem():
    """Verify empirical-statistical performance theorem bounding."""
    engine = TheoremDiscoveryEngine()
    thm = engine.form_performance_bound_conjecture(
        workload_name="Softmax_FP32",
        domain="DEEP_LEARNING",
        metric="latency_ms",
        target_bound=5.0,
        achieved_bound=2.4,
    )

    # All latencies below target (mean ~2.3 ms, max 3.1 ms < 5.0 ms)
    samples_pass = [2.1, 2.3, 2.2, 2.5, 3.1, 2.0, 2.2, 2.4]
    cert_pass = engine.prove_performance_upper_bound(thm, samples_pass)
    assert cert_pass.status == TheoremStatus.PROVEN
    assert cert_pass.verified_by_formal_checker is True

    # Violating samples (contains 8.5 ms > 5.0 ms)
    samples_fail = [2.1, 2.3, 8.5, 2.4]
    cert_fail = engine.prove_performance_upper_bound(thm, samples_fail)
    assert cert_fail.status == TheoremStatus.COUNTEREXAMPLE_FOUND
    assert cert_fail.verified_by_formal_checker is False


# ==============================================================================
# 4. COMPLEXITY LOWER-BOUND & BARRIER ENGINE TESTS (Section 26)
# ==============================================================================

def test_memory_bandwidth_barrier_analysis():
    """Verify theoretical floor calculation and separation of impossible vs bypassable."""
    engine = BarrierEngine()

    # 100 MB data movement with a target of 0.1 ms over 18.57 GB/s:
    # 100 MB at 18.57 GB/s takes ~5.38 ms. Target is 0.1 ms (53.8x faster than physics).
    bytes_100mb = 100 * 1024 * 1024

    # Case A: Contract allows bypass transformations (Zero-Copy, Sparsity, Quantization)
    rep_bypassable = engine.analyze_memory_bandwidth_barrier(
        workload_name="LargeAttentionCache",
        data_movement_bytes=bytes_100mb,
        target_latency_ms=0.1,
        allows_compression_or_sparsity=True,
    )
    assert rep_bypassable.classification == BarrierClassification.BARRIER_BYPASSABLE_VIA_TRANSFORMATION
    assert rep_bypassable.theoretical_floor_ms > 5.0
    assert not rep_bypassable.is_provably_impossible
    assert len(rep_bypassable.bypass_opportunities) > 0

    # Case B: Contract strictly forbids compression or modification (exact memory copying)
    rep_impossible = engine.analyze_memory_bandwidth_barrier(
        workload_name="RawMemoryDump",
        data_movement_bytes=bytes_100mb,
        target_latency_ms=0.1,
        allows_compression_or_sparsity=False,
    )
    assert rep_impossible.classification == BarrierClassification.PROVABLY_IMPOSSIBLE_UNDER_MODEL
    assert rep_impossible.is_provably_impossible is True


def test_sorting_complexity_shannon_barrier():
    """Verify information-theoretic comparison sort lower bound ceil(log2(N!))."""
    engine = BarrierEngine()
    # For N=5: 5! = 120, ceil(log2(120)) = 7 comparisons.
    # Attempting to sort N=5 with only 4 comparisons is mathematically impossible.
    rep_fail = engine.analyze_sorting_complexity_barrier(n=5, target_comparisons=4)
    assert rep_fail.classification == BarrierClassification.PROVABLY_IMPOSSIBLE_UNDER_MODEL
    assert rep_fail.is_provably_impossible is True
    assert rep_fail.theoretical_floor_ms == 7.0

    # Target of 7 comparisons is feasible
    rep_pass = engine.analyze_sorting_complexity_barrier(n=5, target_comparisons=7)
    assert rep_pass.classification == BarrierClassification.FEASIBLE_UNDER_CONSTRAINTS
    assert not rep_pass.is_provably_impossible


# ==============================================================================
# 5. UNIVERSALITY GATE & 16-STATE RESULT MACHINE TESTS (Sections 31 & 34)
# ==============================================================================

def test_universality_gate_transition_rules():
    """Verify structural validity of the 16-state DAG transitions."""
    gate = UniversalityGate()
    assert gate.can_transition(DiscoveryResultState.UNKNOWN, DiscoveryResultState.DISCOVERED)
    assert gate.can_transition(DiscoveryResultState.DISCOVERED, DiscoveryResultState.VERIFIED)
    assert gate.can_transition(DiscoveryResultState.PROVEN, DiscoveryResultState.GUARANTEED)
    # Direct jump from UNKNOWN to GUARANTEED is forbidden!
    assert not gate.can_transition(DiscoveryResultState.UNKNOWN, DiscoveryResultState.GUARANTEED)


def test_universality_gate_12_checkpoint_audit():
    """Verify that GUARANTEED is issued only when all 12 checkpoints pass."""
    gate = UniversalityGate()

    # Checklist missing reproducibility and formal proof
    incomplete_checklist = UniversalityGateChecklist(
        domain_formally_defined=True,
        contract_formally_defined=True,
        correctness_established=True,
        independent_verification_passed=True,
        counterexample_search_conducted=True,
        generalization_demonstrated=True,
        reproducibility_guaranteed=False,  # MISSING
        performance_evidence_measured=True,
        resource_evidence_verified=True,
        no_hidden_computation_verified=True,
        no_unfair_caching_verified=True,
        proof_or_formal_evidence_passed=False,  # MISSING
    )

    report_reject = gate.audit_for_guarantee(
        workload_id="wl-gemm-ternary",
        pathway_name="BitNetTernaryAdditiveBypass",
        current_state=DiscoveryResultState.PROVEN,
        checklist=incomplete_checklist,
    )
    assert report_reject.verdict == "NOT_PROVEN"
    assert report_reject.final_state == DiscoveryResultState.PROVEN  # Kept at PROVEN, not elevated
    assert len(report_reject.rejection_reasons) == 2

    # Checklist with 100% (12/12) passed checkpoints
    complete_checklist = UniversalityGateChecklist(
        domain_formally_defined=True,
        contract_formally_defined=True,
        correctness_established=True,
        independent_verification_passed=True,
        counterexample_search_conducted=True,
        generalization_demonstrated=True,
        reproducibility_guaranteed=True,
        performance_evidence_measured=True,
        resource_evidence_verified=True,
        no_hidden_computation_verified=True,
        no_unfair_caching_verified=True,
        proof_or_formal_evidence_passed=True,
    )

    report_guaranteed = gate.audit_for_guarantee(
        workload_id="wl-gemm-ternary",
        pathway_name="BitNetTernaryAdditiveBypass",
        current_state=DiscoveryResultState.PROVEN,
        checklist=complete_checklist,
    )
    assert report_guaranteed.verdict == "GUARANTEED"
    assert report_guaranteed.final_state == DiscoveryResultState.GUARANTEED
    assert report_guaranteed.passed_percentage == 100.0
    assert len(report_guaranteed.rejection_reasons) == 0
