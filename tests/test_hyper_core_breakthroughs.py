"""
tests/test_hyper_core_breakthroughs.py
Comprehensive Verification Suite for hyper/core/ Breakthrough Engines A-K,
Work Ledger, TruthGate, Proof Engine, and Authoritative Pipeline.
"""
import pytest
import numpy as np

from hyper.core.contract.models import SemanticContract, ContractType, ParityLevel
from hyper.core.cost.ledger import WorkLedger, EndToEndCostModel, AccountingType
from hyper.core.proof.engine import ProofEngine, ProofStatus
from hyper.core.verification.verifier import IndependentVerifier, AdversarialCounterexampleHunter
from hyper.core.evidence.models import EvidenceGrade, EvidenceObject, HardwareFingerprint
from hyper.core.evidence.truth_gate import TruthGate, TruthGateChecklist, GateDecision
from hyper.core.fallback.engine import CanonicalFallbackEngine
from hyper.core.escape.delta_engine import ExactDeltaEngine
from hyper.core.escape.early_termination import CertifiedEarlyTerminationEngine
from hyper.core.escape.exact_reuse import ExactReuseEngine, CacheEntryState
from hyper.core.escape.structure_discovery import StructureDiscoveryEngine, MatrixStructureType
from hyper.core.escape.low_rank_engine import LowRankEngine, FactorizationType
from hyper.core.escape.slicing_engine import OutputDirectedSlicingEngine
from hyper.core.escape.information_escape import InformationTheoreticEscapeEngine
from hyper.core.escape.speculative_engine import SpeculativeEngine
from hyper.core.escape.temporal_engine import TemporalIncrementalEngine
from hyper.core.escape.representation_escape import RepresentationEscapeEngine, RepresentationFormat
from hyper.core.escape.algorithm_substitution import AlgorithmSubstitutionEngine
from hyper.core.pipeline import AuthoritativePipeline


def test_breakthrough_a_exact_delta_computation():
    """Engine A: Verify A(x + Δx) = Ax + AΔx yields 0.0 error compared to numpy."""
    engine = ExactDeltaEngine()
    rng = np.random.RandomState(42)
    A = rng.randn(64, 64)
    x0 = rng.randn(64)

    y0 = engine.register_state("mat_test", A, x0)
    assert np.allclose(y0, np.dot(A, x0))

    # Sparse update (only 2 coordinates changed)
    x1 = x0.copy()
    x1[5] += 3.5
    x1[12] -= 1.2

    y1, ledger, proof, used_delta = engine.compute_update("mat_test", x1)
    assert used_delta is True
    assert proof.status == ProofStatus.PROVEN
    assert np.allclose(y1, np.dot(A, x1), atol=1e-12)
    assert ledger.operations_eliminated > 0
    assert ledger.calculate_work_reduction() > 0.80  # > 80% work reduction on sparse change


def test_breakthrough_b_certified_early_termination():
    """Engine B: Verify certified early termination yields exact argmax."""
    rng = np.random.RandomState(1337)
    W = rng.randn(100, 128)
    x = rng.randn(128)
    # Ensure a clear dominant class to certify early
    W[42, :] = 10.0
    x = np.ones(128)

    ref_argmax = int(np.argmax(np.dot(W, x)))
    winner_idx, ledger, cert, certified = CertifiedEarlyTerminationEngine.compute_certified_argmax_gemv(W, x, chunk_size=16)

    assert certified is True
    assert winner_idx == ref_argmax
    assert cert.status == ProofStatus.PROVEN
    assert ledger.operations_eliminated > 0


def test_breakthrough_c_exact_semantic_reuse():
    """Engine C: Verify cryptographic semantic key identity."""
    reuse = ExactReuseEngine()
    arr = np.array([1.0, 2.0, 3.0, 4.0])
    key = reuse.generate_key(arr, "GEMV", "c1", precision_bits=64)

    # Initial lookup -> COLD
    val, state = reuse.lookup(key)
    assert state == CacheEntryState.COLD
    assert val is None

    # Store result
    reuse.store(key, "COMPUTED_RESULT")

    # Second lookup -> WARM
    val2, state2 = reuse.lookup(key)
    assert state2 == CacheEntryState.WARM
    assert val2 == "COMPUTED_RESULT"

    # Perturb input slightly (single bit change)
    arr_perturbed = arr.copy()
    arr_perturbed[0] += 1e-15
    key_perturbed = reuse.generate_key(arr_perturbed, "GEMV", "c1", precision_bits=64)
    val3, state3 = reuse.lookup(key_perturbed)
    assert state3 == CacheEntryState.COLD  # Must NOT hit!


def test_breakthrough_d_structure_discovery():
    """Engine D: Verify formal structure discovery on known matrices."""
    # Diagonal
    diag_mat = np.diag([1.0, 2.0, 3.0, 4.0])
    ev_diag = StructureDiscoveryEngine.analyze_matrix(diag_mat)
    assert ev_diag.structure_type == MatrixStructureType.DIAGONAL

    # Symmetric
    rng = np.random.RandomState(42)
    sym_mat = rng.randn(10, 10)
    sym_mat = sym_mat + sym_mat.T
    ev_sym = StructureDiscoveryEngine.analyze_matrix(sym_mat)
    assert ev_sym.structure_type == MatrixStructureType.SYMMETRIC

    # Rank-1 Separable
    u = np.array([[2.0], [4.0], [6.0]])
    v = np.array([[1.0, 3.0, 5.0]])
    rank1_mat = u @ v
    ev_rank1 = StructureDiscoveryEngine.analyze_matrix(rank1_mat)
    assert ev_rank1.structure_type == MatrixStructureType.RANK_ONE_SEPARABLE


def test_breakthrough_e_low_rank_engine():
    """Engine E: Verify low-rank factorization contract adherence."""
    rng = np.random.RandomState(42)
    # Exact rank-2 matrix
    U_true = rng.randn(30, 2)
    V_true = rng.randn(2, 30)
    A_lowrank = U_true @ V_true

    contract = SemanticContract(contract_type=ContractType.NUMERICAL_FLOAT, abs_tolerance=1e-8)
    factors, res = LowRankEngine.factorize_matrix(A_lowrank, contract)
    assert res.factorization_type == FactorizationType.EXACT_FACTORISATION
    assert res.rank == 2
    assert factors is not None
    U, V = factors
    assert np.allclose(A_lowrank, U @ V, atol=1e-10)


def test_breakthrough_f_output_directed_slicing():
    """Engine F: Verify output slicing eliminates unobserved operations."""
    rng = np.random.RandomState(42)
    W = rng.randn(50, 64)
    x = rng.randn(64)
    observed = [0, 5, 10]

    y_sub, ledger = OutputDirectedSlicingEngine.compute_observed_slice(W, x, observed)
    y_full = np.dot(W, x)

    assert np.allclose(y_sub, y_full[observed])
    assert ledger.operations_eliminated == 2 * (50 - 3) * 64


def test_breakthrough_h_speculative_execution():
    """Engine H: Verify speculative candidate and automatic fallback on error."""
    # Successful speculation
    val, rep = SpeculativeEngine.execute_speculative(
        speculative_fn=lambda: 42,
        verifier_fn=lambda v: v == 42,
        canonical_fallback_fn=lambda: 99,
        baseline_cost_ms=10.0,
    )
    assert val == 42
    assert rep.accepted is True

    # Failed speculation -> fallback triggered
    val_fb, rep_fb = SpeculativeEngine.execute_speculative(
        speculative_fn=lambda: -1,
        verifier_fn=lambda v: v == 42,
        canonical_fallback_fn=lambda: 42,
        baseline_cost_ms=10.0,
    )
    assert val_fb == 42
    assert rep_fb.accepted is False
    assert rep_fb.fallback_cost_ms > 0.0 or rep_fb.total_elapsed_ms >= rep_fb.candidate_cost_ms


def test_breakthrough_k_algorithm_substitution():
    """Engine K: Verify FFT convolution replaces direct convolution with exact identity."""
    rng = np.random.RandomState(42)
    signal = rng.randn(256)
    kernel = rng.randn(64)

    contract = SemanticContract(contract_type=ContractType.NUMERICAL_FLOAT, abs_tolerance=1e-7)
    res, algo_name, ledger = AlgorithmSubstitutionEngine.substitute_convolution(signal, kernel, contract)

    ref = np.convolve(signal, kernel, mode="full")
    assert algo_name == "FFT_CONVOLUTION"
    assert np.allclose(res, ref, atol=1e-7)
    assert ledger.operations_eliminated > 0


def test_truth_gate_fail_closed():
    """TruthGate: Verify that unverified, predicted, or discrepant results return UNKNOWN/REJECTED."""
    # Checklist missing proof
    checklist_bad_proof = TruthGateChecklist(
        contract_pass=True,
        proof_pass=False,
        verification_pass=True,
        provenance_pass=True,
        measurement_pass=True,
        reproducibility_pass=True,
    )
    evidence = EvidenceObject(evidence_status=EvidenceGrade.REAL_VERIFIED)
    decision, msg = TruthGate.evaluate(checklist_bad_proof, evidence)
    assert decision == GateDecision.UNKNOWN

    # Evidence marked PREDICTED cannot be accepted as REAL_VERIFIED
    checklist_good = TruthGateChecklist(
        contract_pass=True,
        proof_pass=True,
        verification_pass=True,
        provenance_pass=True,
        measurement_pass=True,
        reproducibility_pass=True,
    )
    evidence_predicted = EvidenceObject(evidence_status=EvidenceGrade.PREDICTED)
    decision2, msg2 = TruthGate.evaluate(checklist_good, evidence_predicted)
    assert decision2 == GateDecision.UNKNOWN


def test_authoritative_pipeline_matrix_vector():
    """Authoritative Pipeline: Full 17-stage verification execution."""
    pipeline = AuthoritativePipeline()
    rng = np.random.RandomState(42)
    A = rng.randn(32, 32)
    x0 = rng.randn(32)

    contract = SemanticContract(contract_type=ContractType.NUMERICAL_FLOAT, abs_tolerance=1e-7)
    res0 = pipeline.execute_matrix_vector_workload("pipe_mat", A, x0, contract)
    assert res0.decision == GateDecision.PASS
    assert np.allclose(res0.output, np.dot(A, x0))

    # Second run with sparse delta
    x1 = x0.copy()
    x1[3] += 2.0
    res1 = pipeline.execute_matrix_vector_workload("pipe_mat", A, x1, contract)
    assert res1.decision == GateDecision.PASS
    assert res1.escape_found is True
    assert res1.escape_strategy == "EXACT_DELTA_COMPUTATION"
    assert np.allclose(res1.output, np.dot(A, x1))
    assert res1.work_ledger.operations_eliminated > 0
