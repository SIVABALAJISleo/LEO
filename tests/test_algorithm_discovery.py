"""
tests/test_algorithm_discovery.py
Unit tests for Strategy Candidate Generator, Complexity Transformer, and Evolutionary Loop.
"""

import pytest
from algorithm_discovery.generator import StrategyCandidateGenerator, AlgorithmStrategy
from algorithm_discovery.complexity_transformer import ComplexityTransformer
from algorithm_discovery.evolutionary_loop import EvolutionaryOptimizationLoop, CandidateIndividual


def test_candidate_generator():
    candidates = StrategyCandidateGenerator.generate_candidates("dense_gemm_fp32", allow_approx=True)
    assert len(candidates) >= 2
    exact = candidates[0]
    assert exact.algorithm_name == "reference_direct"
    assert exact.estimated_vwa == 0.0

    approx = [c for c in candidates if c.estimated_vwa > 0.0]
    assert len(approx) > 0


def test_complexity_transformer():
    nb = ComplexityTransformer.evaluate_nbody_transformation(2048)
    assert nb.original_complexity == "O(N^2)"
    assert nb.transformed_complexity == "O(N log N)"

    fft_res = ComplexityTransformer.evaluate_fft_transformation(16384, 32)
    assert fft_res.transformed_complexity == "O(k log N)"


def test_evolutionary_loop():
    loop = EvolutionaryOptimizationLoop(population_size=4, max_generations=2)

    # Dummy evaluation function
    def dummy_eval(strat: AlgorithmStrategy):
        # returns (latency_us, vwa, rel_err, is_valid)
        if strat.algorithm_name == "reference_direct":
            return (1000.0, 0.0, 0.0, True)
        return (500.0, 0.50, 0.05, True)

    res = loop.run_evolution("dense_gemm_fp32", dummy_eval, max_allowed_error=0.10)
    assert res["generations_evaluated"] == 2
    assert res["verified"] is True
    assert res["measured_vwa"] >= 0.0
