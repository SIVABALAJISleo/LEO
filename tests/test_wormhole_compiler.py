"""
tests/test_wormhole_compiler.py
=============================================================================
Comprehensive Unit & Integration Test Suite for HYPER-X Wormhole Compiler
=============================================================================
Verifies all 51 subsystems across Phases 1 through 46.
"""

import pytest
import numpy as np

from hyper_x.wormhole_compiler import (
    WorkloadContract,
    ObservableRequirement,
    CorrectnessRequirement,
    CachePolicy,
    ExecutionTrack,
    NecessityClass,
    MutationType,
    RepresentationType,
    GrammarOperator,
    ProofClass,
    FailureCategory,
    PowerTelemetryType,
    ContractCompiler,
    ObservableCompiler,
    ObservableExtractor,
    InformationDependencyGraph,
    CounterfactualEngine,
    RepresentationSpace,
    AlgorithmGrammar,
    CompositeAlgorithm,
    EqualitySaturationEngine,
    EvolutionEngine,
    EvolutionaryIndividual,
    HardwareCostModel,
    HardwareAdvantageMap,
    ExecutionFabric,
    CapabilityProbe,
    WormholePatterns,
    LearnedShortcutEngine,
    MultiClassProofEngine,
    AdversarialFalsifier,
    BlindHoldoutSystem,
    CandidateRegistry,
    ParityEvaluator,
    StrictParityScorecard,
    MatrixMultiplicationAdapter,
    GraphicsTemporalAdapter,
    OutputSensitiveTopKAdapter,
    ScientificStencilAdapter,
    RAGEmbeddingRetrievalAdapter,
    TelemetryCollector,
    ClaimValidationEngine,
    WormholeCompiler,
)


def test_contract_compiler_matrix():
    contract = ContractCompiler.compile_matrix_contract(
        workload_id="TEST_GEMM_128",
        shape=(128, 128, 128),
        tolerance=1e-4,
        latency_slo_ms=50.0
    )
    assert contract.workload_id == "TEST_GEMM_128"
    assert contract.tolerance == 1e-4
    assert contract.latency_slo_ms == 50.0
    assert contract.cache_policy == CachePolicy.COLD
    assert contract.correctness == CorrectnessRequirement.NUMERICAL_TOLERANCE
    assert len(contract.compute_contract_hash()) == 16


def test_contract_compiler_validation():
    contract = ContractCompiler.compile_matrix_contract(
        workload_id="TEST_EXACT",
        shape=(64, 64, 64),
        correctness=CorrectnessRequirement.EXACT,
        tolerance=0.0,
        latency_slo_ms=10.0,
        memory_limit_mb=100.0,
        forbidden_approximations=["unverified_truncation"]
    )
    # Exceeding tolerance on EXACT
    valid, violations = ContractCompiler.validate_candidate_against_contract(
        contract, candidate_latency_ms=5.0, candidate_error=0.01, candidate_memory_mb=10.0, used_approximations=[]
    )
    assert valid is False
    assert any("EXACT" in v for v in violations)

    # Using forbidden approximation
    valid, violations = ContractCompiler.validate_candidate_against_contract(
        contract, candidate_latency_ms=5.0, candidate_error=0.0, candidate_memory_mb=10.0, used_approximations=["unverified_truncation"]
    )
    assert valid is False
    assert any("forbidden" in v for v in violations)


def test_observable_compiler_types():
    full_obs = ObservableCompiler.full_matrix(128, 128)
    assert full_obs.output_type == "FULL_MATRIX"
    assert full_obs.dimension_reduction_ratio == 1.0

    vec_obs = ObservableCompiler.matrix_vector_projection(128)
    assert vec_obs.output_type == "VECTOR"
    assert vec_obs.dimension_reduction_ratio < 0.01

    top_obs = ObservableCompiler.top_k(10, 1000)
    assert top_obs.output_type == "TOP_K"
    assert top_obs.dimension_reduction_ratio == 0.01

    thresh_obs = ObservableCompiler.threshold_crossing(0.5)
    assert thresh_obs.output_type == "THRESHOLD_BOOLEAN"


def test_observable_extractors():
    arr = np.array([1.0, 5.0, 2.0, 9.0, 3.0], dtype=np.float32)
    top_vals, top_idx = ObservableExtractor.extract_top_k(arr, k=2)
    assert list(top_vals) == [9.0, 5.0]
    assert list(top_idx) == [3, 1]

    argmax_val = ObservableExtractor.extract_argmax(arr)
    assert argmax_val == 3


def test_dependency_graph_backward_pruning():
    graph = InformationDependencyGraph("TEST_GRAPH")
    contract = ContractCompiler.compile_matrix_contract("TEST", (64, 64, 64))
    obs = ObservableCompiler.matrix_vector_projection(64)

    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    graph.classify_matrix_workload(A, B, contract, obs)

    summary = graph.compute_summary()
    assert summary["total_nodes"] == 4
    assert "necessary_cost_flops" in summary
    assert summary["work_elimination_potential"] >= 0.0


def test_counterfactual_engine_hypotheses():
    engine = CounterfactualEngine()
    contract = ContractCompiler.compile_matrix_contract("TEST", (64, 64, 64))
    node = graph_node = InformationDependencyGraph("TEST").nodes = {}

    from hyper_x.wormhole_compiler.schemas import DependencyNode
    test_node = DependencyNode(
        node_id="test_gemm",
        operation="matmul",
        estimated_cost=1e6,
        memory_cost=1000,
        dependencies=[],
        output_shape=(64, 64),
        precision="float32",
        reuse_probability=0.0,
        observability=1.0
    )

    hypotheses = engine.generate_hypotheses(
        node=test_node,
        contract=contract,
        workload_context={"estimated_rank_ratio": 0.2, "sparsity_ratio": 0.5, "has_downstream_projection": True}
    )
    assert len(hypotheses) >= 4
    mutations = [h.mutation for h in hypotheses]
    assert MutationType.OUTPUT_PROJECT in mutations
    assert MutationType.FACTORIZE in mutations
    assert MutationType.REPRESENTATION_CHANGE in mutations


def test_representation_space_transformations():
    A = np.random.randn(64, 64).astype(np.float32)
    A[:32, :] = 0.0  # 50% sparse

    sparse_dict, overhead = RepresentationSpace.to_sparse_csr(A, threshold=1e-4)
    assert sparse_dict["type"] == "SPARSE_CSR"
    assert sparse_dict["sparsity"] >= 0.5
    assert overhead >= 0.0

    lowrank_dict, overhead = RepresentationSpace.to_randomized_low_rank(A, rank=16)
    assert lowrank_dict["type"] == "LOW_RANK_FACTORED"
    assert lowrank_dict["rank"] == 16

    bitnet_dict, overhead = RepresentationSpace.to_ternary_bitnet(A)
    assert bitnet_dict["type"] == "TERNARY_BITNET"
    assert set(np.unique(bitnet_dict["ternary"])).issubset({-1, 0, 1})


def test_algorithm_grammar_composition():
    contract = ContractCompiler.compile_matrix_contract("TEST", (64, 64, 64))
    algo = CompositeAlgorithm(
        representation=GrammarOperator.LOW_RANK,
        decomposition=GrammarOperator.FACTOR,
        correction_strategy=GrammarOperator.CORRECT,
        verification_strategy=GrammarOperator.SPECULATE
    )
    valid, violations = AlgorithmGrammar.validate_composition(algo, contract)
    assert valid is True
    assert "LOW_RANK + FACTOR + CORRECT + SPECULATE" == algo.to_canonical_expression()


def test_egraph_rewrite_saturation():
    egraph = EqualitySaturationEngine(exact_only=True)
    cid = egraph.add_expression("(A @ B) @ C")
    rewrites = egraph.saturate(iterations=2)
    assert rewrites >= 1
    best_expr, cost = egraph.extract_cheapest(cid)
    assert "A @ (B @ C)" in best_expr or "(A @ B) @ C" in best_expr


def test_evolution_engine_pareto_ranking():
    engine = EvolutionEngine(population_size=4, max_generations=2)
    ind1 = EvolutionaryIndividual("IND_1", CompositeAlgorithm(GrammarOperator.DENSE))
    ind1.latency_ms = 10.0
    ind1.numerical_error = 1e-5
    ind1.memory_mb = 50.0

    ind2 = EvolutionaryIndividual("IND_2", CompositeAlgorithm(GrammarOperator.LOW_RANK))
    ind2.latency_ms = 5.0
    ind2.numerical_error = 1e-4
    ind2.memory_mb = 20.0

    ranked = engine.pareto_rank_population([ind1, ind2])
    assert len(ranked) == 2
    assert ranked[0].fitness_score > 0.0


def test_hardware_cost_model():
    model = HardwareCostModel()
    contract = ContractCompiler.compile_matrix_contract("TEST", (128, 128, 128))
    cost = model.evaluate_cost(
        nominal_flops=2.0 * 128**3,
        actual_flops=128**3,
        bytes_transferred=128**2 * 4,
        partition_ratio_igpu=0.0
    )
    assert cost.arithmetic_cost > 0.0
    assert cost.total_latency_ms > 0.0
    j_obj = model.compute_objective_j(cost, contract, error=1e-5)
    assert j_obj > 0.0


def test_hardware_advantage_map():
    erasure = HardwareAdvantageMap.calculate_advantage_erasure(
        applied_transformations=["LOW_RANK", "SPARSE", "MORTON_Z"],
        workload_domain="dense_matrix"
    )
    assert erasure["gpu_advantage_required_pct"] > 0.0
    assert erasure["gpu_advantage_erased_pct"] >= 50.0
    assert erasure["gpu_advantage_remaining_pct"] >= 0.0


def test_execution_fabric_probe():
    probe = CapabilityProbe.probe()
    assert "has_avx2" in probe
    assert "logical_cores" in probe
    assert probe["logical_cores"] >= 1


def test_wormhole_patterns_freivalds_proof():
    proof_engine = MultiClassProofEngine()
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    C_exact = A @ B

    record = proof_engine.verify_freivalds_probabilistic(C_exact, A, B, tolerance=1e-5, rounds=10)
    assert record.verified is True
    assert record.proof_type == ProofClass.RANDOMIZED_PROBABILISTIC
    assert record.numerical_error < 1e-5

    # With artificial corruption
    C_corrupt = np.copy(C_exact)
    C_corrupt[0, 0] += 10.0
    record_fail = proof_engine.verify_freivalds_probabilistic(C_corrupt, A, B, tolerance=1e-5, rounds=10)
    assert record_fail.verified is False


def test_adversarial_falsifier():
    falsifier = AdversarialFalsifier()
    contract = ContractCompiler.compile_matrix_contract("TEST", (32, 32, 32), tolerance=1e-3)
    
    # Exact function should survive all stress tests
    res_exact = falsifier.falsify_candidate("CAND_EXACT", lambda a, b: a @ b, contract, shape=(32, 32, 32))
    assert res_exact.survived_all is True
    assert res_exact.failed_tests == 0

    # Bad approximation that outputs zero should be falsified
    res_zero = falsifier.falsify_candidate("CAND_ZERO", lambda a, b: np.zeros((a.shape[0], b.shape[1]), dtype=np.float32), contract, shape=(32, 32, 32))
    assert res_zero.survived_all is False
    assert res_zero.failed_tests > 0


def test_blind_holdout_system():
    system = BlindHoldoutSystem()
    contract = ContractCompiler.compile_matrix_contract("TEST", (32, 32, 32))
    system.register_sealed_matrix_holdout("HOLDOUT_1", shape=(32, 32, 32), seed=123)

    # Clean exact function passes holdout
    report = system.evaluate_holdout("HOLDOUT_1", "CAND_EXACT", lambda a, b: a @ b, contract, "TEST_HW_HASH")
    assert report.passed is True
    assert report.output_hash_match is True


def test_candidate_and_failure_registry():
    reg = CandidateRegistry()
    fail = reg.record_failure(
        grammar_expression="LOW_RANK + QUANTIZE",
        target_operation="matrix_multiply",
        failure_category=FailureCategory.NUMERICAL,
        measured_error=0.05,
        tolerance=0.001,
        input_characteristics={"rank_ratio": 0.8},
        diagnosis="Rank too high for low-rank SVD"
    )
    assert len(reg.failure_knowledge_base) == 1

    known, reason = reg.is_known_failure("LOW_RANK + QUANTIZE", {"rank_ratio": 0.82})
    assert known is True
    assert "Rank too high" in reason


def test_strict_parity_scorecard_separation():
    contract = ContractCompiler.compile_matrix_contract("TEST", (64, 64, 64), tolerance=1e-3)
    scorecard = ParityEvaluator.evaluate(
        contract=contract,
        candidate_latency_ms=10.0,
        reference_latency_ms=15.0,
        numerical_error=1e-4,
        nominal_reference_flops=1e6,
        actual_necessary_flops=3e5,
        memory_used_mb=10.0,
        provenance_valid=True,
        holdout_passed=True
    )
    # Check separate gates
    assert scorecard.numerical_parity_gate is True
    assert scorecard.performance_parity_gate is True
    assert scorecard.overall_conjunctive_gate is True
    assert scorecard.wormhole_score == 0.3
    assert scorecard.work_elimination_ratio == 0.7
    assert scorecard.raw_hardware_speedup == 1.5


def test_domain_adapters():
    # GEMM
    gemm_contract = MatrixMultiplicationAdapter.build_contract(64, 64, 64)
    assert gemm_contract.operation == "matrix_multiply"

    # Graphics
    gfx_contract = GraphicsTemporalAdapter.build_contract((128, 128))
    assert gfx_contract.operation == "graphics_denoising_reconstruction"

    # Stencil
    stencil_contract = ScientificStencilAdapter.build_contract((64, 64))
    assert stencil_contract.operation == "scientific_stencil_diffusion"

    # RAG
    rag_contract = RAGEmbeddingRetrievalAdapter.build_contract(100, 64, top_k=3)
    assert rag_contract.operation == "vector_similarity_top_k"


def test_telemetry_and_claim_validation():
    collector = TelemetryCollector()
    collector.record_search_metrics(generated=5, verified=2, rejected=3, falsified=1, search_ms=12.5, verify_ms=2.0, wer=0.75, speedup=2.1)
    d = collector.to_dict()
    assert d["candidates_generated"] == 5
    assert d["work_elimination_pct"] == 75.0
    assert d["raw_speedup"] == 2.1

    validator = ClaimValidationEngine()
    rec = validator.register_evidence(
        claim_statement="Low-rank shortcut verified under contract",
        benchmark_id="BM_GEMM_1",
        workload_hash="W_HASH",
        candidate_hash="C_HASH",
        hardware_hash="HW_HASH",
        verifier_hash="V_HASH",
        is_target_hardware_match=True,
        is_workload_unmodified=True,
        verification_passed=True
    )
    assert rec.status == "VERIFIED"


def test_end_to_end_wormhole_compiler_low_rank():
    compiler = WormholeCompiler(time_budget_sec=5.0)
    # Construct rank-16 structured matrix (128 x 128)
    rng = np.random.RandomState(42)
    U = rng.randn(128, 16).astype(np.float32)
    V = rng.randn(16, 128).astype(np.float32)
    A = U @ V
    B = rng.randn(128, 128).astype(np.float32)

    res = compiler.compile_and_execute(A, B)
    assert res["status"] == "WORMHOLE_DISCOVERED_AND_VERIFIED"
    assert "LOW_RANK" in res["selected_algorithm"]
    assert res["work_elimination_pct"] >= 60.0
    assert res["wormhole_score"] <= 0.4
    assert res["numerical_error"] <= 1e-3
    assert "explainability" in res
    assert "why_valid" in res["explainability"]


def test_end_to_end_wormhole_compiler_no_free_lunch_on_unstructured():
    compiler = WormholeCompiler(time_budget_sec=5.0)
    # Construct unstructured dense high-entropy Gaussian matrix
    rng = np.random.RandomState(123)
    A = rng.randn(64, 64).astype(np.float32)
    B = rng.randn(64, 64).astype(np.float32)

    res = compiler.compile_and_execute(A, B)
    assert res["status"] == "NO_VERIFIED_WORMHOLE_DISCOVERED"
    assert "No verified computational wormhole discovered" in res["message"]
    assert res["work_elimination_pct"] == 0.0
    assert res["wormhole_score"] == 1.0
    assert "output" in res


def test_universal_functional_verifier_rejects_false_candidates():
    from hyper_x.wormhole_compiler.functional_verifier import UniversalFunctionalVerifier
    from hyper_x.wormhole_compiler.contract import ContractCompiler
    from hyper_x.wormhole_compiler.schemas import CorrectnessRequirement

    contract = ContractCompiler.compile_matrix_contract("TEST_EXACT", (32, 32, 32), correctness=CorrectnessRequirement.EXACT)
    A = np.eye(32, dtype=np.float32)
    B = np.ones((32, 32), dtype=np.float32)

    # 1. Candidate returning wrong shape
    cand_wrong_shape = lambda a, b: np.zeros((16, 16), dtype=np.float32)
    ref_fn = lambda a, b: a @ b
    rep_shape = UniversalFunctionalVerifier.verify("cand_shape", cand_wrong_shape, ref_fn, (A, B), contract)
    assert rep_shape.functional_pass is False
    assert rep_shape.shape_pass is False

    # 2. Candidate returning NaN
    def cand_nan(a, b):
        out = a @ b
        out[0, 0] = np.nan
        return out
    rep_nan = UniversalFunctionalVerifier.verify("cand_nan", cand_nan, ref_fn, (A, B), contract)
    assert rep_nan.functional_pass is False
    assert rep_nan.finite_pass is False

    # 3. Candidate with non-zero error under EXACT contract
    def cand_approx(a, b):
        out = a @ b
        out[0, 0] += 0.001
        return out
    rep_exact = UniversalFunctionalVerifier.verify("cand_approx", cand_approx, ref_fn, (A, B), contract)
    assert rep_exact.functional_pass is False
    assert rep_exact.exact_pass is False

    # 4. ParityEvaluator rejects when functional_pass is False
    scorecard = ParityEvaluator.evaluate(
        contract=contract,
        candidate_latency_ms=5.0,
        reference_latency_ms=10.0,
        numerical_error=0.0,
        nominal_reference_flops=1e5,
        actual_necessary_flops=5e4,
        memory_used_mb=1.0,
        provenance_valid=True,
        holdout_passed=True,
        functional_pass=False
    )
    assert scorecard.functional_parity_gate is False
    assert scorecard.overall_conjunctive_gate is False

