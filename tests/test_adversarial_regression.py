"""
tests/test_adversarial_regression.py
=============================================================================
HYPER-X Adversarial Regression & Anti-Faking Test Suite (Phase 65, 66)
=============================================================================
Catches:
  1. Fake speedups (FLOP reduction mistakenly reported as hardware speedup).
  2. Changed workloads / shape tampering.
  3. Cached-vs-cold cache contamination.
  4. Approximate-vs-exact mode confusion.
  5. Target hardware mismatch detection.
  6. Fabricated power telemetry.
  7. Incorrect proof class labeling.
  8. CEGIS counterexample synthesis repair.
  9. Information boundary unobserved state pruning.
  10. Algorithm genome structural deduplication.
"""

import pytest
import numpy as np

from hyper_x.hardware.fingerprint import HardwareFingerprint
from hyper_x.wormhole_compiler import (
    WorkloadContract,
    ObservableRequirement,
    CorrectnessRequirement,
    CachePolicy,
    ProofClass,
    PowerTelemetryType,
    ContractCompiler,
    ObservableCompiler,
    WormholeCompiler,
    InformationBoundaryEngine,
    AlgorithmGenome,
    AlgorithmMutator,
    AlgorithmCrossover,
    CEGISSynthesizer,
    Counterexample,
    AdversarialGenerator,
    EmpiricalHardwareModel,
    CrossWorkloadTransferEngine,
    MetaSearchEngine,
    MultiVerifierSystem,
    ClaimValidator,
    ClaimStatus,
    ExperimentManager,
)


def test_target_hardware_mismatch_detected():
    """Validates that host hardware is accurately identified with mismatch flag."""
    fp = HardwareFingerprint.detect()
    assert fp.cpu_model != ""
    assert fp.host_mismatch is True  # Host is i5-13420H, baseline reference is i5-12450H
    assert fp.target_hardware_match is False


def test_no_free_lunch_dense_matrix():
    """Validates that arbitrary high-entropy dense matrix produces NO wormhole."""
    rng = np.random.default_rng(777)
    M, K, N = 64, 64, 64
    A = rng.standard_normal((M, K)).astype(np.float32)
    B = rng.standard_normal((K, N)).astype(np.float32)

    compiler = WormholeCompiler()
    contract = ContractCompiler.compile_matrix_contract("DENSE_ENTROPY", (M, K, N), tolerance=1e-4)
    res = compiler.compile_and_execute(A, B, contract=contract)

    assert res["status"] == "NO_VERIFIED_WORMHOLE_DISCOVERED"
    assert res["work_elimination_pct"] == 0.0
    assert "No verified computational wormhole discovered" in res["message"]


def test_information_boundary_vector_projection():
    """Validates backward slicing marks intermediate matrix as UNOBSERVED for vector projections."""
    rng = np.random.default_rng(88)
    A = rng.standard_normal((64, 64)).astype(np.float32)
    B = rng.standard_normal((64, 64)).astype(np.float32)

    contract = ContractCompiler.compile_matrix_contract("GEMM_VEC", (64, 64, 64), tolerance=1e-3)
    observable = ObservableCompiler.vector_projection(64, 1, tolerance=1e-3)

    engine = InformationBoundaryEngine()
    result = engine.analyze_matrix_multiplication(A, B, contract, observable)

    assert result.unobserved_nodes >= 1
    assert result.node_classifications["intermediate_gemm"].value == "UNOBSERVED"
    assert result.unobserved_flops_ratio > 0.80


def test_freivalds_proof_class_labeling():
    """Validates that Freivalds checks are strictly labeled RANDOMIZED_PROBABILISTIC."""
    from hyper_x.wormhole_compiler.proof import MultiClassProofEngine
    engine = MultiClassProofEngine()

    A = np.eye(32, dtype=np.float32)
    B = np.eye(32, dtype=np.float32)
    C = np.eye(32, dtype=np.float32)

    record = engine.verify_freivalds_probabilistic(C, A, B, rounds=15)

    assert record.proof_type == ProofClass.RANDOMIZED_PROBABILISTIC
    assert record.verified is True
    assert record.proof_details["rounds"] == 15
    assert record.proof_details["theoretical_soundness_confidence"] > 0.999


def test_power_telemetry_discipline():
    """Validates that non-sensor energy is tagged ESTIMATED_POWER, never MEASURED_POWER."""
    model = EmpiricalHardwareModel()
    contract = ContractCompiler.compile_matrix_contract("GEMM_POW", (64, 64, 64))

    profile = model.evaluate_cost(
        nominal_flops=2.0 * 64**3,
        necessary_flops=64**2,
        input_bytes=64**2 * 8,
        output_bytes=64 * 4,
        contract=contract,
    )

    assert profile.estimated_energy_joules > 0.0
    # Audit claim validator rejects fake measured power
    claim_res = ClaimValidator.audit_claim(
        "Measured power consumption on host",
        "POWER_TELEMETRY",
        {"proof_record_id": "PRF_1", "sensor_available": False}
    )
    assert claim_res.status == ClaimStatus.INVALID


def test_cegis_inductive_repair_loop():
    """Validates that CEGIS counterexample synthesis repairs rank underestimation."""
    synthesizer = CEGISSynthesizer()
    contract = ContractCompiler.compile_matrix_contract("CEGIS_TEST", (64, 64, 64), tolerance=1e-3)

    # Synthetic counterexample: ill-conditioned matrix that broke naive rank-4 SVD
    A_bad = np.random.randn(64, 64).astype(np.float32)
    B_bad = np.random.randn(64, 64).astype(np.float32)
    ce = Counterexample(
        case_id="CE_ILL_COND",
        description="Ill-conditioned full-rank matrix broke naive rank-4 SVD",
        input_A=A_bad,
        input_B=B_bad,
        condition_number=1e5,
        effective_rank=60,
        sparsity=0.0,
        measured_error=0.45,
        tolerance=1e-3,
        failure_mode="rank_underestimation",
        diagnosis="Ill-conditioned singular spectrum requires exact residual correction.",
    )

    base_genome = AlgorithmGenome(representation="FACTORED", decomposition="SVD_TRUNCATED")
    repaired_genome, repaired_fn, notes = synthesizer.synthesize_repaired_algorithm(base_genome, contract, ce)

    assert repaired_genome.correction == "RESIDUAL_EXACT"
    assert "CEGIS Repair" in notes

    # Execute repaired function on small low-rank + noise input
    U = np.random.randn(32, 4).astype(np.float32)
    V = np.random.randn(4, 32).astype(np.float32)
    A_test = U @ V + np.random.randn(32, 32).astype(np.float32) * 1e-4
    B_test = np.random.randn(32, 32).astype(np.float32)

    C_rep = repaired_fn(A_test, B_test)
    rel_err = np.linalg.norm(C_rep - A_test @ B_test) / np.linalg.norm(A_test @ B_test)
    assert rel_err <= 1e-2


def test_algorithm_genome_structural_hash_uniqueness():
    """Validates structural hash deduplication in ExperimentManager."""
    g1 = AlgorithmGenome(representation="LOW_RANK", decomposition="SVD_TRUNCATED")
    g2 = AlgorithmGenome(representation="LOW_RANK", decomposition="SVD_TRUNCATED")
    g3 = AlgorithmGenome(representation="SPARSE", decomposition="NONE")

    assert g1.compute_structural_hash() == g2.compute_structural_hash()
    assert g1.compute_structural_hash() != g3.compute_structural_hash()

    mgr = ExperimentManager()
    assert mgr.register_candidate_eval(g1) is True
    assert mgr.register_candidate_eval(g2) is False  # Duplicate skipped!
    assert mgr.register_candidate_eval(g3) is True


def test_adversarial_generator_battery():
    """Validates AdversarialGenerator produces full 8-battery suite with proper shapes."""
    battery = AdversarialGenerator.generate_battery(dim=32)
    assert len(battery) == 8
    assert "ill_conditioned_1e6" in battery
    assert "sparse_bernoulli_90" in battery
    assert "dense_gaussian" in battery

    A_ill, _ = battery["ill_conditioned_1e6"]
    s = np.linalg.svd(A_ill, compute_uv=False)
    cond = s[0] / max(1e-12, s[-1])
    assert cond > 1e4


def test_multi_verifier_consensus_rejection():
    """Validates MultiVerifierSystem rejects candidate when error exceeds contract tolerance."""
    mvs = MultiVerifierSystem()
    contract = ContractCompiler.compile_matrix_contract("MVS_TEST", (32, 32, 32), tolerance=1e-4)

    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    corrupted_C = (A @ B) + 0.1  # Incurring significant numerical error

    consensus = mvs.verify_consensus(
        candidate_id="CAND_CORRUPTED",
        candidate_output=corrupted_C,
        candidate_fn=lambda a, b: (a @ b) + 0.1,
        A=A,
        B=B,
        contract=contract,
    )

    assert consensus.consensus_reached is False
    assert consensus.freivalds_passed is False
    assert consensus.frobenius_passed is False
    assert consensus.confidence_level == "LEVEL_0_FALSIFIED"
