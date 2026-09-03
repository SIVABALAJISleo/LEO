"""
tests/test_hyper_mvc_dar_search.py
Unit tests for Strategy Genome, Evolutionary Search, Fallback Ladder, Strategy Memory, and Irreducibility.
"""

import pytest
from hyper_mvc_dar import (
    StrategyGenome,
    StrategySearchEngine,
    StrategyMemory,
    FallbackLevel,
    FallbackLadder,
    IrreducibilityEngine,
    HardwareProfiler,
    PredictVerifyAcceptEngine,
    AdaptiveComputeEngine,
)


def test_strategy_genome_mutation_and_evolution():
    genome = StrategyGenome(
        strategy_id="strat_0",
        algorithm="DenseTiled",
        representation="Dense",
        precision="FP32",
        tile_size=64,
        cpu_ratio=0.7,
        igpu_ratio=0.3,
        sampling_strength=1.0,
        verification_method="Freivalds"
    )
    mutant = genome.mutate()
    assert mutant.strategy_id != genome.strategy_id

    search = StrategySearchEngine(population_size=4)
    assert len(search.population) == 4
    gen1 = search.evolve_generation()
    assert len(gen1) == 4


def test_fallback_ladder_cascade():
    # Level 1 fails verification, cascades down to Level 8
    dispatchers = {
        FallbackLevel.LEVEL_1_EXACT_SIMPLIFICATION: lambda: "corrupted_output",
        FallbackLevel.LEVEL_8_EXACT_FALLBACK: lambda: "reference_gold_output",
    }

    def verifier(val):
        return val == "reference_gold_output"

    res = FallbackLadder.execute_with_ladder("test_op", dispatchers, verifier)
    assert res["passed"] is True
    assert res["final_executed_level"] == int(FallbackLevel.LEVEL_8_EXACT_FALLBACK)
    assert res["result"] == "reference_gold_output"


def test_strategy_memory_commit_and_transfer():
    memory = StrategyMemory()
    fp = memory.get_fingerprint("matmul", (1024, 1024), "exact")
    assert memory.retrieve_strategy(fp) is None

    memory.commit_strategy(fp, {"algorithm": "AVX2_Tiled"}, measured_speedup=3.5)
    strat = memory.retrieve_strategy(fp)
    assert strat is not None
    assert strat["measured_speedup"] == 3.5

    transferred = memory.transfer_knowledge("matmul", (512, 512))
    assert transferred is not None
    assert transferred["algorithm"] == "AVX2_Tiled"


def test_irreducibility_certificate_generation():
    cert = IrreducibilityEngine.generate_certificate(
        workload_name="Dense_GEMM_FullRank_Exact",
        contract_class="EXACT",
        bottleneck="MATHEMATICAL_FULL_RANK",
        attempted=["RandomizedSVD", "Sparsity"],
        unavoidable_flops=1000000,
        unavoidable_bytes=4000000
    )
    assert cert.certificate_id.startswith("CERT-IRR-")
    assert cert.verdict == "PHYSICALLY_IRREDUCIBLE_UNDER_GIVEN_CONTRACT"
    json_str = cert.to_json()
    assert "MATHEMATICAL_FULL_RANK" in json_str


def test_predict_verify_accept_loop():
    # Case A: Confidence high and verification passes
    pred_fn_pass = lambda: ("predicted_answer", 0.95)
    verif_fn_pass = lambda x: x == "predicted_answer"
    fb_fn = lambda: "fallback_answer"

    out, stats = PredictVerifyAcceptEngine.execute_adaptive(pred_fn_pass, verif_fn_pass, fb_fn, 0.90)
    assert out == "predicted_answer"
    assert stats["path_executed"] == "PREDICTION_ACCEPTED"

    # Case B: Confidence low -> falls back to exact
    pred_fn_low = lambda: ("low_confidence_guess", 0.60)
    out_fb, stats_fb = PredictVerifyAcceptEngine.execute_adaptive(pred_fn_low, verif_fn_pass, fb_fn, 0.90)
    assert out_fb == "fallback_answer"
    assert stats_fb["path_executed"] == "FALLBACK_EXACT"


def test_adaptive_compute_sampling_and_resolution():
    # Sampling convergence
    converged, needed = AdaptiveComputeEngine.evaluate_adaptive_sampling(
        current_samples=10000,
        sample_variance=1.0,
        target_error=0.01  # Std error = sqrt(1 / 10000) = 0.01
    )
    assert converged is True
    assert needed == 0

    # Resolution scaling under high frame time
    scale = AdaptiveComputeEngine.select_resolution_scale(target_fps=60.0, current_frame_time_ms=25.0)
    assert scale <= 0.75
