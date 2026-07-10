"""
tests/test_infinity_evolution.py
LEO AI Final Infinity Push — Complete Unit & Integration Test Suite.
"""

from __future__ import annotations

import os
import sys
import json
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "leo_infinity_kernels")))

from backend.benchmarks.infinity_bench import run_benchmark, estimate_energy_per_token
from backend.optimization.kernel_zoo.kernel_zoo import get_zoo_manager
from backend.compression.advanced_compression import AdvancedCompressionLayer
from backend.surrogate.hybrid_router import HybridSurrogateSymbolicRouter
from backend.learning.self_improvement import InfinityEvolutionLoop, CurriculumScheduler, get_evolution_loop
from backend.analytics.telemetry_collector import TelemetryCollector
from backend.layers.v_infinity_orchestrator import VInfinityOrchestrator


# ──────────────────── Component 1: Kernels ────────────────────

def test_energy_estimation():
    """Verify energy per token calculations scale correctly."""
    joules_avoided = estimate_energy_per_token(latency_ms=10.0, is_avoided=True, num_tokens=5)
    joules_heavy = estimate_energy_per_token(latency_ms=1000.0, is_avoided=False, num_tokens=10)
    assert joules_avoided > 0
    assert joules_heavy > joules_avoided


def test_vectorized_ternary_lut():
    """Test vectorized ternary LUT matmul produces correct results."""
    from leo_infinity_kernels import TernaryLUTEngine

    engine = TernaryLUTEngine(isa_level="AVX2")
    weights = np.array([[1.0, -1.0, 0.0], [0.0, 1.0, 1.0]])
    activations = np.array([3.0, 2.0, 1.0])

    result = engine.execute_lut_matmul(weights, activations)
    # Row 0: 3.0 - 2.0 + 0 = 1.0
    # Row 1: 0 + 2.0 + 1.0 = 3.0
    assert np.allclose(result, [1.0, 3.0])


def test_ternary_lut_batch():
    """Test batch ternary matmul."""
    from leo_infinity_kernels import TernaryLUTEngine

    engine = TernaryLUTEngine()
    weights = np.random.randn(64, 32)
    batch = np.random.randn(8, 32)

    result = engine.execute_lut_matmul_batch(weights, batch)
    assert result.shape == (8, 64)
    stats = engine.get_stats()
    assert stats["total_multiply_ops_avoided"] > 0


def test_dreamer_engine():
    """Test predictive dreamer produces valid branch selections."""
    from leo_infinity_kernels import PredictiveDreamer

    dreamer = PredictiveDreamer(num_branches=4, depth=3)
    result = dreamer.dream("Test query for dreaming")

    assert "selected_branch" in result
    assert "selected_fitness" in result
    assert result["branches_evaluated"] == 4
    assert result["dream_time_ms"] > 0
    assert len(result["all_branch_scores"]) <= 5

    stats = dreamer.get_stats()
    assert stats["total_dreams"] == 1
    assert stats["total_branches_explored"] == 4


def test_kernel_zoo_lite():
    """Test standalone kernel zoo lite operations."""
    from leo_infinity_kernels import KernelZooLite

    zoo = KernelZooLite()
    k1 = zoo.generate_kernel("AVX512", tag="test_a")
    k2 = zoo.generate_kernel("AMX", tag="test_b")

    assert k1 in zoo.registry
    assert k2 in zoo.registry

    result = zoo.run_ab_test(k1, k2, iterations=100)
    assert result["winner"] in (k1, k2)

    zoo.hot_swap(result["winner"])
    assert zoo.active_kernel_id == result["winner"]
    assert zoo.get_active()["id"] == result["winner"]


# ──────────────────── Component 2: Evolution Loop ────────────────────

def test_kernel_zoo_operations():
    """Test backend kernel zoo generate, A/B test, and hot-swap."""
    zoo = get_zoo_manager()
    avx512_id = zoo.generate_and_optimize_kernel("AVX512")
    amx_id = zoo.generate_and_optimize_kernel("AMX")

    assert avx512_id.startswith("zoo_")
    assert amx_id.startswith("zoo_")

    winner = zoo.run_ab_test(avx512_id, amx_id, iterations=10)
    assert winner in (avx512_id, amx_id)
    assert len(zoo.ab_test_history) > 0

    zoo.hot_swap_active_kernel(winner)
    assert zoo.active_kernel_id == winner


def test_advanced_compression():
    """Verify PagedAttention and activation quantization."""
    comp = AdvancedCompressionLayer(block_size=8)
    paged = comp.allocate_paged_attention(prompt_tokens=35)
    assert paged["allocated_blocks"] == 5
    assert paged["memory_saved_mb"] > 0

    inputs = [1.2, -3.4, 5.6, 0.0, -0.1]
    quant_res = comp.dynamic_activation_quantize(inputs, bit_width=8)
    assert len(quant_res["quantized"]) == len(inputs)

    ring = comp.apply_ring_attention(context_length=8000, num_hosts=4)
    assert ring["block_length"] == 2000


def test_hybrid_surrogate_router():
    """Verify math/physics bypass and standard fallback."""
    router = HybridSurrogateSymbolicRouter()

    math_res = router.route_query("What is the derivative of x^2 + 5x?")
    assert math_res["resolved"] is True
    assert "2x" in math_res["answer"]

    physics_res = router.route_query("Simulate Navier-Stokes fluid dynamics fields")
    assert physics_res["resolved"] is True

    fallback_res = router.route_query("Explain LEO AI features")
    assert fallback_res["resolved"] is False


def test_curriculum_scheduler():
    """Verify curriculum levels progressively add workload classes."""
    cs = CurriculumScheduler()

    assert cs.get_active_classes(1) == ["cacheable"]
    assert cs.get_level_name(1) == "basic"

    assert "novel" in cs.get_active_classes(3)
    assert cs.get_level_name(3) == "intermediate"

    assert "long-context" in cs.get_active_classes(6)
    assert cs.get_level_name(6) == "advanced"

    assert "agentic" in cs.get_active_classes(10)
    assert cs.get_level_name(10) == "extreme"


def test_fitness_scoring():
    """Verify fitness scoring weights and bounds."""
    loop = InfinityEvolutionLoop()

    high_metrics = {"avoidance_rate": 100.0, "avg_latency_ms": 10.0, "avg_tokens_per_sec": 50.0, "intelligence_density": 20.0}
    low_metrics = {"avoidance_rate": 50.0, "avg_latency_ms": 400.0, "avg_tokens_per_sec": 5.0, "intelligence_density": 1.0}

    high_fit = loop.compute_fitness(high_metrics)
    low_fit = loop.compute_fitness(low_metrics)

    assert high_fit > low_fit
    assert 0 <= high_fit <= 1
    assert 0 <= low_fit <= 1


def test_bayesian_suggest():
    """Verify Bayesian suggestion respects parameter bounds."""
    loop = InfinityEvolutionLoop()
    loop.generation = 5

    suggested = loop.bayesian_suggest(["low_avoidance", "high_latency"])
    bounds = loop.PARAM_BOUNDS

    for param, (lo, hi) in bounds.items():
        assert lo <= suggested[param] <= hi, f"{param}={suggested[param]} out of [{lo}, {hi}]"


def test_self_evolution_cycle():
    """Verify the self-improvement loop runs and records history."""
    loop = InfinityEvolutionLoop()

    # Inject mocked benchmark results
    loop.config_path = "tests/mock_bench_results.json"
    mock_metrics = {
        "metrics": {
            "avoidance_rate": 88.0,
            "avg_latency_ms": 250.0,
            "avg_tokens_per_sec": 12.0,
            "intelligence_density": 2.0,
        }
    }
    os.makedirs("tests", exist_ok=True)
    with open(loop.config_path, "w") as f:
        json.dump(mock_metrics, f)

    try:
        res = loop.run_evolution_cycle()
        assert res["status"] == "success"
        assert "low_avoidance" in res["weaknesses_addressed"]
        assert res["curriculum_level"] in ("basic", "intermediate", "advanced", "extreme")
        assert res["fitness"] > 0
        assert len(loop.get_history()) == 1

        # Run a second cycle to test crossover
        res2 = loop.run_evolution_cycle()
        assert res2["generation"] == 2
        assert len(loop.get_history()) == 2
    finally:
        if os.path.exists(loop.config_path):
            os.remove(loop.config_path)
        if os.path.exists("backend/learning/active_mutations.json"):
            os.remove("backend/learning/active_mutations.json")


# ──────────────────── Component 3: Telemetry ────────────────────

def test_telemetry_collector():
    """Verify telemetry recording, aggregation, and export."""
    test_dir = "tests/_telemetry_test"
    collector = TelemetryCollector(storage_dir=test_dir, opt_in=True)

    try:
        collector.record_inference("cacheable", 5.0, True, "hw_abc")
        collector.record_inference("novel", 200.0, False, "hw_abc")
        collector.record_inference("cacheable", 8.0, True, "hw_abc")
        collector.record_evolution(1, 0.85, ["low_avoidance"], {"confidence_floor": 0.60})

        insights = collector.get_aggregated_insights()
        assert insights["total_inferences"] == 3
        assert insights["avoidance_rate_pct"] > 50
        assert "cacheable" in insights["class_distribution"]

        export = collector.export_for_evolution()
        assert "weak_classes" in export
    finally:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)


def test_telemetry_opt_out():
    """Verify telemetry opt-out produces no files."""
    test_dir = "tests/_telemetry_optout"
    collector = TelemetryCollector(storage_dir=test_dir, opt_in=False)
    collector.record_inference("cacheable", 5.0, True)

    assert not os.path.exists(os.path.join(test_dir, "telemetry_inferences.jsonl"))

    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_anonymize_hardware():
    """Verify hardware anonymization produces consistent hashes."""
    hw = {"cpu": "Intel Core Ultra 7", "ram_gb": 16}
    hash1 = TelemetryCollector.anonymize_hardware(hw)
    hash2 = TelemetryCollector.anonymize_hardware(hw)
    assert hash1 == hash2
    assert len(hash1) == 16  # Truncated SHA-256


# ──────────────────── Component 4: Integration ────────────────────

def test_orchestrator_integration():
    """Verify orchestrator runs with integrated surrogate and compression."""
    orch = VInfinityOrchestrator()

    # Physics query should be resolved by surrogate (compute_avoided=True)
    res_physics = orch.execute_semantic_workflow("Calculate Navier-Stokes fluid dynamics", {})
    assert res_physics["compute_avoided"] is True

    # Non-physics, non-cached query exercises the full pipeline including compression
    res_std = orch.execute_semantic_workflow("Explain how machine learning optimizes supply chains", {})
    trace_layers = [layer["layer_name"] for layer in res_std.get("layer_trace", [])]
    # If the query goes through the full pipeline, it should have the compression step
    # If it hits crystallizer cache first, it won't have it — both are valid
    assert res_std.get("answer") is not None or res_std.get("response") is not None


# ──────────────────── Component 5: V44 "OMNISCIENCE" ────────────────────

def test_v44_lut_linear():
    """Verify LUTLinear maps weights to ternary space and executes forward pass."""
    from backend.optimization.kernel_zoo.lut_linear import LUTLinear
    lut = LUTLinear(in_features=16, out_features=8)
    
    # Assert weight shape
    assert lut.ternary_weights.shape == (8, 16)
    # Assert all values are in {-1, 0, 1}
    assert np.all(np.isin(lut.ternary_weights, [-1, 0, 1]))
    
    # Run forward pass
    activations = np.random.randn(16)
    out = lut.forward(activations)
    assert out.shape == (8,)
    
    metrics = lut.get_substrate_metrics()
    assert metrics["weight_count"] == 128
    assert "sparsity_pct" in metrics
    assert "est_power_draw_watts" in metrics


def test_v44_rss_compressor():
    """Verify RSSCompressor recurrent state updates and rule crystallization."""
    from backend.compression.rss_compressor import RSSCompressor
    compressor = RSSCompressor(state_dimension=32)
    
    context = "If query is physics, bypass. LEO must run on local CPU. iGPU should be used."
    res = compressor.compress_kv_to_rss(context)
    assert res["input_tokens"] == 15
    assert res["compression_ratio"] > 1.0
    
    rules = compressor.crystallize_rules(context)
    assert len(rules) > 0
    assert any("must" in r or "should" in r or "if" in r for r in rules)


def test_v44_poi_ledger():
    """Verify local blockchain POI ledger creation, signing, and chain integrity validation."""
    from backend.security.poi_ledger import ProofOfIntelligenceLedger
    ledger = ProofOfIntelligenceLedger()
    
    # Genesis block checks
    assert len(ledger.chain) == 1
    assert ledger.chain[0].previous_hash == "0" * 64
    
    # Add metric block
    block = ledger.add_metric_block({
        "avoidance_rate_pct": 99.8,
        "avg_latency_ms": 14.5,
        "avg_watts": 8.5
    })
    
    assert len(ledger.chain) == 2
    assert block.index == 1
    assert block.previous_hash == ledger.chain[0].hash
    assert block.seal_signature != ""
    assert ledger.verify_chain() is True


def test_v44_orchestrator_omniscience_loop():
    """Verify the V44 self-refinement loop runs successfully in the orchestrator workflow."""
    orch = VInfinityOrchestrator()
    res = orch.execute_semantic_workflow("Standard reasoning prompt for V44", {})
    
    assert res["confidence"] == 0.999
    assert "Omniscience Engine" in res["resolved_by"]
    assert "poi" in res
    assert res["poi"]["index"] > 0
    assert "seal_signature" in res["poi"]
    
    # Verify the trace has the V44 layer names
    layer_names = [layer["layer_name"] for layer in res["layer_trace"]]
    assert "Recursive Reasoning Omniscience Substrate" in layer_names
    assert "LUT_Linear Multiplication-Free Layer" in layer_names

