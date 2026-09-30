import pytest
import numpy as np
from hyper_x.wormhole_compiler.optimization_applicability import OptimizationApplicabilityEngine

def test_low_rank_flat_spectrum_rejection():
    engine = OptimizationApplicabilityEngine()
    # Create a full rank matrix with a flat spectrum
    workload = np.eye(128)
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "LOW_RANK")
    assert not report.applicable
    assert report.classification == "FLAT_SPECTRUM"

def test_low_rank_decaying_spectrum_acceptance():
    engine = OptimizationApplicabilityEngine()
    # Create a matrix with strong spectral decay
    U = np.random.randn(128, 16)
    V = np.random.randn(16, 128)
    workload = U @ V
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "LOW_RANK")
    assert report.applicable
    assert report.classification == "STRONG_SPECTRAL_DECAY"

def test_sparse_threshold_overhead_rejection():
    engine = OptimizationApplicabilityEngine()
    # Matrix that is mostly dense
    workload = np.random.randn(128, 128)
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "THRESHOLD_SPARSITY")
    assert not report.applicable
    assert report.classification == "LOW_SPARSITY"

def test_sparse_real_sparsity_acceptance():
    engine = OptimizationApplicabilityEngine()
    # Matrix that is mostly sparse
    workload = np.zeros((128, 128))
    workload[0, 0] = 1.0
    workload[1, 1] = 1.0
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate(workload, "test_mat", DummyContract(), "THRESHOLD_SPARSITY")
    assert report.applicable
    assert report.classification == "HIGH_SPARSITY"

def test_exact_reuse_cold_cache_rejection():
    engine = OptimizationApplicabilityEngine()
    class DummyContract:
        cache_policy = "COLD"
        tolerance = 0.0
    report = engine.evaluate(np.zeros((10, 10)), "reuse_test", DummyContract(), "EXACT_REUSE")
    assert not report.applicable
    assert report.classification == "CONTRACT_FORBIDS_REUSE"

def test_exact_reuse_streaming_unique_rejection():
    engine = OptimizationApplicabilityEngine()
    # 20 distinct random arrays simulating high-entropy streaming
    workload = [np.random.randn(10, 10) for _ in range(20)]
    class DummyContract:
        cache_policy = "WARM"
        deterministic = True
    report = engine.evaluate(workload, "streaming_test", DummyContract(), "EXACT_REUSE")
    assert not report.applicable
    assert report.classification == "ZERO_HIT_RATE_STREAMING"

def test_exact_reuse_acceptance():
    engine = OptimizationApplicabilityEngine()
    workload = np.random.randn(10, 10)
    class DummyContract:
        cache_policy = "WARM"
        deterministic = True
    report = engine.evaluate(workload, "static_reuse_test", DummyContract(), "EXACT_REUSE")
    assert report.applicable
    assert report.classification == "HIGH_REPETITION_POTENTIAL"

def test_delta_computation_dense_entropy_rejection():
    engine = OptimizationApplicabilityEngine()
    # Two consecutive frames with dense differences (>70% changes)
    frame1 = np.zeros((32, 32))
    frame2 = np.ones((32, 32))
    class DummyContract:
        tolerance = 1e-4
    report = engine.evaluate([frame1, frame2], "delta_test", DummyContract(), "DELTA_COMPUTATION")
    assert not report.applicable
    assert report.classification == "INSUFFICIENT_TEMPORAL_COHERENCE"

def test_delta_computation_sparse_acceptance():
    engine = OptimizationApplicabilityEngine()
    # Two consecutive frames with very sparse changes (only 1 element changes out of 1024)
    frame1 = np.zeros((32, 32))
    frame2 = np.zeros((32, 32))
    frame2[0, 0] = 5.0
    class DummyContract:
        tolerance = 1e-3
    report = engine.evaluate([frame1, frame2], "delta_test", DummyContract(), "DELTA_COMPUTATION")
    assert report.applicable
    assert report.classification == "SPARSE_TEMPORAL_DELTA"

def test_precision_reduction_exact_contract_rejection():
    engine = OptimizationApplicabilityEngine()
    workload = np.random.randn(32, 32)
    class DummyContract:
        tolerance = 0.0
        correctness_mode = "EXACT"
    report = engine.evaluate(workload, "prec_test", DummyContract(), "PRECISION_REDUCTION")
    assert not report.applicable
    assert report.classification == "CONTRACT_DEMANDS_EXACT_PRECISION"

def test_precision_reduction_ill_conditioned_rejection():
    engine = OptimizationApplicabilityEngine()
    # Create ill-conditioned matrix: singular values 1.0 and 1e-6
    U = np.eye(32)
    S = np.ones(32)
    S[-1] = 1e-6
    workload = U * S
    class DummyContract:
        tolerance = 1e-2
        correctness_mode = "BOUNDED_APPROXIMATION"
    report = engine.evaluate(workload, "prec_test", DummyContract(), "PRECISION_REDUCTION")
    assert not report.applicable
    assert report.classification == "ILL_CONDITIONED_SPECTRUM"

def test_precision_reduction_well_conditioned_acceptance():
    engine = OptimizationApplicabilityEngine()
    # Well conditioned matrix
    workload = np.eye(32) + 0.1 * np.random.randn(32, 32)
    class DummyContract:
        tolerance = 1e-2
        correctness_mode = "BOUNDED_APPROXIMATION"
    report = engine.evaluate(workload, "prec_test", DummyContract(), "PRECISION_REDUCTION")
    assert report.applicable
    assert report.classification == "WELL_CONDITIONED_NUMERICAL_SLACK"

def test_output_sensitive_dense_requirement_rejection():
    engine = OptimizationApplicabilityEngine()
    workload = np.random.randn(32, 32)
    class DummyContract:
        observable = "output_tensor"
        preserve_shape = True
        top_k = None
        output_sparsity_mask = None
    report = engine.evaluate(workload, "output_test", DummyContract(), "OUTPUT_SENSITIVE_PRUNING")
    assert not report.applicable
    assert report.classification == "FULL_DENSE_OUTPUT_REQUIRED"

def test_memory_tiling_l1_fit_rejection():
    engine = OptimizationApplicabilityEngine()
    # 16x16 float64 matrix = 2048 bytes (fits easily in 32KB L1 cache)
    workload = np.zeros((16, 16), dtype=np.float64)
    class DummyContract:
        tolerance = 0.0
    report = engine.evaluate(workload, "tile_test", DummyContract(), "MEMORY_TILING")
    assert not report.applicable
    assert report.classification == "FITS_IN_L1_CACHE"

def test_baseline_floor_detector_roofline():
    from hyper_x.wormhole_compiler.baseline_floor_detector import BaselineFloorDetector
    detector = BaselineFloorDetector(default_peak_gflops=100.0, default_peak_bandwidth_gbps=40.0)
    
    # 1. Near floor: 128x128 matrix running in 0.03 ms (near hardware limit)
    mat = np.random.randn(128, 128).astype(np.float32)
    report_fast = detector.analyze(
        workload_name="gemm_128",
        baseline_impl="numpy.dot",
        baseline_time=4e-5,  # 0.04 ms
        hardware_scope="AVX2_CPU",
        contract_id="contract_exact",
        workload=mat
    )
    assert report_fast.status == "BASELINE_NEAR_PRACTICAL_FLOOR"
    assert report_fast.roofline_efficiency is not None
    
    # 2. Significant slack: 128x128 matrix artificially slowed to 100 ms
    report_slow = detector.analyze(
        workload_name="gemm_128",
        baseline_impl="naive_python_loop",
        baseline_time=0.100,  # 100 ms
        hardware_scope="AVX2_CPU",
        contract_id="contract_exact",
        workload=mat
    )
    assert report_slow.status == "BASELINE_HAS_SIGNIFICANT_SLACK"
    assert report_slow.optimization_slack > 0.09

def test_claim_validator_baseline_floor_and_forced_opt():
    from hyper_x.wormhole_compiler.claim_validator import ClaimValidator, ClaimStatus

    # 1. Baseline floor claim verification
    res_floor = ClaimValidator.audit_claim(
        statement="Current baseline is near practical floor",
        dimension="BASELINE_FLOOR",
        evidence={"status": "BASELINE_NEAR_PRACTICAL_FLOOR", "roofline_efficiency": 0.75}
    )
    assert res_floor.status == ClaimStatus.VERIFIED
    assert res_floor.evidence_valid

    # 2. Forced optimization claim rejection
    res_forced = ClaimValidator.audit_claim(
        statement="Claiming 10x speedup via low rank",
        dimension="WORK_ELIMINATION",
        evidence={"applicability_rejected": True, "proof_record_id": "PROOF_123"}
    )
    assert res_forced.status == ClaimStatus.INVALID
    assert not res_forced.evidence_valid

    # 3. Prohibited universality claim
    res_universal = ClaimValidator.audit_claim(
        statement="Universal optimization for all workloads",
        dimension="WORK_ELIMINATION",
        evidence={}
    )
    assert res_universal.status == ClaimStatus.INVALID

def test_scientific_auditor_hyper_omega_checks():
    from hyper_x.wormhole_compiler.scientific_auditor import ScientificAuditor

    # Prohibited universality statement
    findings = ScientificAuditor.audit_statement("This provides universal optimization across every workload.")
    assert any(f.category == "IMPOSSIBLE_CLAIM" for f in findings)

    # Forced optimization attempt in result record
    audit_report = ScientificAuditor.audit_result_record(
        workload_id="GEMM_RANDOM",
        contract_mode="BOUNDED_APPROXIMATION",
        numerical_error=1e-4,
        holdout_passed=True,
        provenance={"applicability_rejected": True},
        is_simulated=False,
        claimed_as_real_hardware=True
    )
    assert not audit_report.passed
    assert any(f.category == "FORCED_OPTIMIZATION" for f in audit_report.findings)

    # Negative control failure in result record
    audit_neg = ScientificAuditor.audit_result_record(
        workload_id="RANDOM_NOISE",
        contract_mode="BOUNDED_APPROXIMATION",
        numerical_error=1e-4,
        holdout_passed=True,
        provenance={"negative_control_passed": False},
        is_simulated=False,
        claimed_as_real_hardware=True
    )
    assert not audit_neg.passed
    assert any(f.category == "NEGATIVE_CONTROL_FAILURE" for f in audit_neg.findings)


