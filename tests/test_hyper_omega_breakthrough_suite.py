"""
Comprehensive Test Suite for HYPER Ω Breakthrough Architecture:
Tests the 7 Escape Classes, Search Space Compiler, AlphaTensor/AlphaDev Discovery,
Program Evolution, Meta-Search, Candidate Genealogy, Breakthrough/Falsification Duels,
Counterexample Minimization & Failure-to-Knowledge, Theorem Prover, Instant-Path Routing,
and End-to-End Orchestration.
"""
import pytest
import numpy as np

from hyper_universal.contract_ir import ContractIR, ContractType
from hyper_universal.workload import UniversalWorkload, WorkloadFamily
from hyper_universal.types import ResultTaxonomy

from hyper_omega.escape_engine.engine import ComputationalEscapeEngine, EscapeHypothesis
from hyper_omega.escape_engine.types import EscapeClass
from hyper_omega.search_space_compiler.compiler import SearchSpaceCompiler
from hyper_omega.algorithm_discovery.engine import AlgorithmDiscoveryEngine
from hyper_omega.algorithm_discovery.strategies import (
    AlphaTensorBilinearDiscovery,
    AlphaDevLowLevelDiscovery,
)
from hyper_omega.program_evolution.engine import ProgramEvolutionEngine
from hyper_omega.program_evolution.genome import ProgramGenome, ProgramMutator, ProgramCrossover
from hyper_omega.meta_search.engine import MetaSearchEngine
from hyper_omega.meta_search.strategy_genome import SearchStrategyGenome
from hyper_omega.genealogy.graph import CandidateGenealogyGraph, CandidateNode
from hyper_omega.agents.breakthrough_agent import BreakthroughAgent
from hyper_omega.agents.falsification_agent import FalsificationAgent
from hyper_omega.agents.duel import AgentDiscoveryDuel
from hyper_omega.counterexamples.database import CounterexampleDatabase
from hyper_omega.theorem_engine.engine import TheoremDiscoveryEngine, TheoremStatus
from hyper_omega.instant_path.engine import InstantPathEngine, ExecutionMode
from hyper_omega.orchestrator import HyperOmegaOrchestrator


def test_computational_escape_seven_classes():
    """Verify that all 7 escape classes are generated and verifiable."""
    engine = ComputationalEscapeEngine()
    contract = ContractIR(
        contract_type=ContractType.EXACT,
        description="Exact output equality",
        deterministic=True
    )
    hypotheses = engine.generate_hypotheses("test_matrix_op", contract)
    assert len(hypotheses) == 7
    classes = {h.escape_class for h in hypotheses}
    assert classes == {
        EscapeClass.A_ELIMINATION,
        EscapeClass.B_SUBSTITUTION,
        EscapeClass.C_REUSE,
        EscapeClass.D_COMPRESSION,
        EscapeClass.E_PREDICTION_CORRECTION,
        EscapeClass.F_REPRESENTATION_ESCAPE,
        EscapeClass.G_ALGORITHMIC_ESCAPE,
    }

    # Test executing an elimination candidate
    elim_code = """
def candidate(x):
    import numpy as np
    return np.asarray(x)
"""
    test_inputs = [np.array([1, 2, 3]), np.array([4, 5, 6])]
    res = engine.execute_and_verify_escape(
        hypotheses[0],
        elim_code,
        test_inputs,
        lambda x: np.asarray(x),
        contract
    )
    assert res.executed is True
    assert res.verification_passed is True
    assert res.status in [ResultTaxonomy.VERIFIED, ResultTaxonomy.FOUND]


def test_search_space_compiler_dimensions():
    """Verify 9-dimensional compilation and discrete configuration count."""
    compiler = SearchSpaceCompiler()
    contract = ContractIR(contract_type=ContractType.NUMERICAL)
    workload = UniversalWorkload(
        workload_id="gemm_dense",
        name="Dense Matrix Multiplication",
        workload_family=WorkloadFamily.LINEAR_ALGEBRA,
        contract=contract,
        input_schema={"A": (64, 64), "B": (64, 64)},
    )
    space = compiler.compile(workload, contract)


    assert len(space.mathematical_space) > 0
    assert len(space.algorithm_space) > 0
    assert len(space.representation_space) > 0
    assert len(space.program_space) > 0
    assert len(space.compiler_space) > 0
    assert len(space.schedule_space) > 0
    assert len(space.memory_layout_space) > 0
    assert len(space.precision_space) >= 4  # Reduced precision allowed under numerical tolerance
    assert len(space.execution_space) > 0
    assert space.total_discrete_configurations() > 100


def test_alphatensor_and_alphadev_discovery():
    """Verify AlphaTensor bilinear discovery and AlphaDev branchless sorting discovery."""
    contract = ContractIR(contract_type=ContractType.EXACT)

    # 1. AlphaTensor
    tensor_strat = AlphaTensorBilinearDiscovery()
    def eval_strassen(code):
        return True, 1.14, False

    cands, metrics = tensor_strat.search("gemm_2x2", contract, budget=5, eval_fn=eval_strassen)
    assert len(cands) == 1
    assert "m1 =" in cands[0].code
    assert cands[0].algorithm_hash == "strassen_rank_7_bilinear"
    assert metrics.novelty >= 0.90

    # 2. AlphaDev
    dev_strat = AlphaDevLowLevelDiscovery()
    def eval_sort(code):
        return True, 1.35, False

    cands_dev, metrics_dev = dev_strat.search("sort_3", contract, budget=5, eval_fn=eval_sort)
    assert len(cands_dev) == 1
    assert "branchless" in cands_dev[0].description.lower() or "swap" in cands_dev[0].description.lower()
    assert metrics_dev.novelty >= 0.90


def test_program_evolution_mutations_and_crossover():
    """Verify AST mutations, crossover, and evolutionary population update."""
    engine = ProgramEvolutionEngine(population_size=5)
    seed_code = """
def candidate(x):
    import numpy as np
    return np.asarray(x) * 2
"""
    engine.seed_population(seed_code)
    assert len(engine.population) == 1

    test_inputs = [np.array([1, 2]), np.array([3, 4])]
    ref_fn = lambda x: np.asarray(x) * 2
    contract = ContractIR(contract_type=ContractType.EXACT)

    pop = engine.evolve_generation(test_inputs, ref_fn, contract)
    assert len(pop) >= 1
    assert pop[0].verified is True


def test_meta_search_adaptation():
    """Verify MetaSearchEngine adjusts parameters and detects saturation."""
    meta = MetaSearchEngine()
    initial_budget = meta.current_strategy.candidate_budget

    def dummy_runner(genome: SearchStrategyGenome) -> float:
        # Returns a flat score to trigger stagnation
        return 10.0

    strat, status = meta.run_meta_iteration(dummy_runner)
    assert status == ResultTaxonomy.FOUND

    # Run two more times to trigger saturation
    meta.run_meta_iteration(dummy_runner)
    strat_final, status_final = meta.run_meta_iteration(dummy_runner)
    assert status_final == ResultTaxonomy.SEARCH_SATURATED


def test_breakthrough_vs_falsification_duel():
    """Verify competitive duel between BreakthroughAgent and FalsificationAgent."""
    duel_engine = AgentDiscoveryDuel()
    contract = ContractIR(contract_type=ContractType.EXACT)

    def ref_gemm(inputs):
        A, B = inputs
        return np.asarray(A) @ np.asarray(B)

    # 2x2 nominal inputs
    nominal_inputs = [
        (np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([[5.0, 6.0], [7.0, 8.0]])),
        (np.array([[2.0, 0.0], [1.0, 3.0]]), np.array([[1.0, 1.0], [0.0, 2.0]])),
    ]

    results = duel_engine.execute_duel("gemm_2x2", contract, nominal_inputs, ref_gemm)
    assert len(results) > 0

    # The Strassen candidate should survive Cauchy noise and boundary tests
    strassen_res = [r for r in results if r.breakthrough_class == "bilinear_rank_reduction"][0]
    assert strassen_res.survived_falsification is True
    assert strassen_res.final_status == ResultTaxonomy.VERIFIED


def test_counterexample_minimization_and_failure_knowledge():
    """Verify automatic input minimization and creation of negative search constraints."""
    db = CounterexampleDatabase()
    large_matrix = np.ones((10, 10))

    cx = db.record_counterexample(
        candidate_id="bad_cand_01",
        failure_type="boundary_divergence",
        failed_contract="EXACT",
        failed_assumption="matrix_positive_definite",
        raw_input=large_matrix,
        severity="HIGH"
    )

    assert cx.minimal_counterexample.shape == (2, 2)  # Reduced from 10x10 to 2x2
    constraints = db.get_active_constraints()
    assert len(constraints) == 1
    assert "Disallow bad_cand_01" in constraints[0].learned_rule


def test_theorem_discovery_conjecture_and_proof():
    """Verify TheoremDiscoveryEngine tracks mathematical statements and proof status."""
    engine = TheoremDiscoveryEngine()
    contract = ContractIR(contract_type=ContractType.EXACT)

    thm = engine.form_conjecture(
        theorem_id="thm_horner_poly",
        transformation_name="horner_rule",
        precondition="well_conditioned_real_polynomial",
        contract=contract,
        assumptions=["distributivity"],
        proof_obligations=["exact_polynomial_eval"]
    )
    assert thm.status == TheoremStatus.CONJECTURE

    # Prove symbolically
    engine.attempt_symbolic_proof(
        theorem_id="thm_horner_poly",
        proof_artifact="Verified via Horner polynomial recurrence identity",
        symbolic_verified=True
    )
    assert engine.theorems["thm_horner_poly"].status == TheoremStatus.PROVEN


def test_instant_path_routing_hierarchy():
    """Verify hierarchical dispatch: Known Theorem -> Instant Specialization, else fallback."""
    instant_engine = InstantPathEngine()
    contract = ContractIR(contract_type=ContractType.EXACT)

    # 1. Match known theorem for 2x2 matrix
    res_instant = instant_engine.route_workload(
        pattern_signature="bilinear_matrix_multiplication_2x2",
        contract=contract,
        mode=ExecutionMode.ONLINE_EXECUTION
    )
    assert res_instant.dispatch_path == "INSTANT_SPECIALIZATION"
    assert res_instant.candidate_code is not None

    # 2. Unknown pattern in online mode -> clean UNKNOWN fallback
    res_unknown = instant_engine.route_workload(
        pattern_signature="quantum_lattice_gauge_theory",
        contract=contract,
        mode=ExecutionMode.ONLINE_EXECUTION
    )
    assert res_unknown.dispatch_path == "FALLBACK_ONLINE"
    assert res_unknown.status == ResultTaxonomy.UNKNOWN


def test_full_hyper_omega_orchestration_loop():
    """Verify the complete Section 59 implementation loop runs end-to-end."""
    orchestrator = HyperOmegaOrchestrator()
    contract = ContractIR(contract_type=ContractType.EXACT)
    workload = UniversalWorkload(
        workload_id="bilinear_matrix_multiplication_2x2",
        name="2x2 Matrix Multiplication",
        workload_family=WorkloadFamily.LINEAR_ALGEBRA,
        contract=contract,
        input_schema={"A": (2, 2), "B": (2, 2)},
    )


    nominal_inputs = [
        (np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([[5.0, 6.0], [7.0, 8.0]])),
        (np.array([[0.5, -1.0], [2.0, 3.5]]), np.array([[1.2, 0.0], [-0.5, 4.0]])),
    ]
    ref_fn = lambda inp: inp[0] @ inp[1]

    summary = orchestrator.run_full_omega_loop(
        workload=workload,
        contract=contract,
        nominal_inputs=nominal_inputs,
        reference_fn=ref_fn,
        mode=ExecutionMode.OFFLINE_RESEARCH
    )

    assert summary.instant_path_dispatch == "INSTANT_SPECIALIZATION"
    assert len(summary.duel_results) > 0
    assert summary.theorems_discovered >= 1
    assert summary.wall_time_seconds > 0.0
    assert summary.final_status in [
        ResultTaxonomy.PROVEN,
        ResultTaxonomy.VERIFIED,
        ResultTaxonomy.GENERALIZED,
        ResultTaxonomy.COUNTEREXAMPLE_FOUND,
        ResultTaxonomy.UNKNOWN,
    ]
