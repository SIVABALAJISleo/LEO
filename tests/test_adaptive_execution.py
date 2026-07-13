"""
tests/test_adaptive_execution.py
Verifies adaptive computation scaling, early exit thresholds, and speculative decoding acceptance checks.
"""

import numpy as np
import pytest
from core_ai.adaptive_execution import AdaptiveExecutionEngine, TokenImportanceEstimator, AdaptiveComputeBudgeter
from core_ai.speculative_decoder import SpeculativeDecoder

def test_token_importance_estimator():
    estimator = TokenImportanceEstimator()
    tokens = ["The", "LEO", "inference", "kernel", "is", "fast", "."]
    scores = estimator.estimate_importance(tokens)
    
    # "The" is a stop word -> score = 0.25
    assert scores[0] == 0.25
    # "." is punctuation -> score = 0.15
    assert scores[6] == 0.15
    # "inference" is a long word -> score = 1.0
    assert scores[2] == 1.0

def test_adaptive_compute_budgeter():
    budgeter = AdaptiveComputeBudgeter(latency_slo_ms=100.0)
    
    # Plenty of budget left (0ms elapsed)
    params_plenty = budgeter.get_execution_parameters(0.0)
    assert params_plenty["early_exit_entropy_threshold"] == 0.05
    assert params_plenty["max_draft_tokens"] == 10
    
    # Budget violated (120ms elapsed)
    params_violated = budgeter.get_execution_parameters(120.0)
    assert params_violated["early_exit_entropy_threshold"] == 0.40
    assert params_violated["max_draft_tokens"] == 3

def test_adaptive_execution_engine():
    engine = AdaptiveExecutionEngine(num_layers=8)
    res = engine.run_layer_execution(["Hello", "LEO", "AI"], latency_slo_ms=500.0)
    
    assert "completed_layers" in res
    assert "early_exit_triggered" in res
    assert res["tokens_processed"] > 0

def test_speculative_decoder_execution():
    import os
    decoder = SpeculativeDecoder(in_dim=64, draft_dim=16, target_dim=64, max_draft_tokens=4, acceptance_threshold=0.99) # high threshold triggers fallback
    
    # Test fallback
    output_text, stats = decoder.generate("Sample prompt", max_tokens=15)
    assert stats["tokens_generated"] >= 15
    
    # Test flag disabled
    os.environ["LEO_SPECULATIVE"] = "0"
    output_text_no_spec, stats_no_spec = decoder.generate("Sample prompt", max_tokens=5)
    assert stats_no_spec["tokens_generated"] == 5
    os.environ.pop("LEO_SPECULATIVE", None)

    # Test prefix caching
    os.environ["LEO_PREFIX_CACHING"] = "1"
    output_text_cache, stats_cache = decoder.generate("Cached prompt", max_tokens=5)
    # Generate again to trigger cache hit trace log
    decoder.generate("Cached prompt", max_tokens=5)
    os.environ.pop("LEO_PREFIX_CACHING", None)


def test_hardware_tuner():
    from core_ai.hardware_tuner import LEOHardwareTuner
    tuner = LEOHardwareTuner()
    report = tuner.run_parameter_sweep("models/missing.gguf")
    
    assert "fingerprint" in report
    assert "modes" in report
    
    settings = tuner.get_optimized_settings("performance")
    assert settings["threads"] == 8
    assert settings["batch_size"] == 32


def test_benchmarker():
    from core_ai.benchmarker import LEOBenchmarker
    bench = LEOBenchmarker(model_path="models/missing.gguf", threads=4, use_gpu=False)
    report = bench.run_inference_benchmark(runs_count=2)
    
    assert report["benchmark_status"] == "ESTIMATED"
    assert report["threads"] == 4
    assert "metrics" in report
    assert len(report["raw_runs"]) == 3
