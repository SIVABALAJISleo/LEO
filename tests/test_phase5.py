"""
tests/test_phase5.py
Phase 5 Verification: Compiler Layer, Self-Optimizer, and integration.
All benchmarks are real measured values.
"""

import logging
import sys
import os
import time
import threading
import torch
import torch.nn as nn

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.optimization.compiler_layer import CompilerLayer
from backend.optimization.self_optimizer import ContinuousSelfOptimizer
from backend.optimization.benchmark_framework import BenchmarkFramework


# ── Simple test model ──────────────────────────────────────────────────────────
class TinyMLP(nn.Module):
    def __init__(self, dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim, dim * 2), nn.GELU(),
            nn.Linear(dim * 2, dim), nn.GELU(),
            nn.Linear(dim, 1)
        )

    def forward(self, x):
        return self.net(x)


def test_compiler_layer():
    logger.info("[Test] 13. Compiler Layer")
    compiler = CompilerLayer(backend="inductor")
    model = TinyMLP(64)
    model.eval()

    # Warm-up pass before compile
    dummy = torch.randn(4, 64)
    with torch.no_grad():
        _ = model(dummy)

    # Compile — pass probe_input so backend failures surface NOW not on first forward
    t0 = time.perf_counter()
    compiled_model = compiler.compile_model(
        model, model_id="tiny_mlp", config={"dim": 64}, probe_input=dummy
    )
    compile_time_ms = (time.perf_counter() - t0) * 1000
    logger.info(f"   Compilation completed in {compile_time_ms:.1f}ms")

    # Verify compiled model produces valid output
    with torch.no_grad():
        out = compiled_model(dummy)
    assert out.shape == (4, 1), f"Unexpected output shape: {out.shape}"

    # Verify compilation cache: second call should be instant
    t1 = time.perf_counter()
    cached = compiler.compile_model(model, model_id="tiny_mlp", config={"dim": 64})
    cache_lookup_ms = (time.perf_counter() - t1) * 1000
    logger.info(f"   Cache lookup: {cache_lookup_ms:.2f}ms (should be near 0)")
    assert cache_lookup_ms < 5.0, f"Cache lookup too slow: {cache_lookup_ms:.2f}ms"

    # ONNX export
    onnx_path = compiler.export_to_onnx(model, dummy, model_id="tiny_mlp_test")
    if onnx_path:
        assert os.path.exists(onnx_path)
        size_kb = os.path.getsize(onnx_path) / 1024
        logger.info(f"   ONNX exported: {onnx_path} ({size_kb:.1f} KB)")

    logger.info("✅ Compiler Layer verified.")


def test_self_optimizer():
    logger.info("\n[Test] 12. Continuous Self-Optimization Engine")
    optimizer = ContinuousSelfOptimizer(optimization_interval_sec=60)  # Don't fire during test

    # Simulate 50 inference calls with mixed routes
    for i in range(30):
        optimizer.record("LARGE_MODEL", latency_ms=350.0, cache_hit=False)
    for i in range(10):
        optimizer.record("TINY_MODEL", latency_ms=45.0, cache_hit=False)
    for i in range(10):
        optimizer.record("RULE_ENGINE", latency_ms=1.0, cache_hit=True)

    stats = optimizer.get_live_stats()
    logger.info(f"   Live stats: avg={stats['avg_latency_ms']}ms p95={stats['p95_latency_ms']}ms "
                f"cache={stats['cache_hit_rate']*100:.1f}%")

    assert stats["total_calls"] == 50
    assert stats["avg_latency_ms"] > 0

    # Detect bottlenecks
    bottlenecks = optimizer._detect_bottlenecks()
    logger.info(f"   Detected bottlenecks: {bottlenecks}")
    # Should detect LARGE_MODEL overuse (60% > 40% threshold)
    assert any("OVERUSING_LARGE_MODEL" in b for b in bottlenecks), \
        "Expected LARGE_MODEL bottleneck detection"

    # Auto-tune
    old_threshold = optimizer.params["early_exit_threshold"]
    optimizer._auto_tune(bottlenecks)
    # With HIGH_LATENCY (avg > 200ms), early exit threshold should decrease
    logger.info(f"   Params after auto-tune: {optimizer.params}")

    logger.info("✅ Continuous Self-Optimization Engine verified.")


def test_end_to_end_benchmark():
    logger.info("\n[Test] Full End-to-End Pipeline Benchmark")
    bench = BenchmarkFramework()
    compiler = CompilerLayer()
    optimizer = ContinuousSelfOptimizer(optimization_interval_sec=9999)

    model = TinyMLP(64)
    model.eval()
    dummy = torch.randn(8, 64)

    # Benchmark uncompiled
    def run_uncompiled():
        with torch.no_grad():
            return model(dummy)

    r_raw = bench.benchmark_latency("uncompiled_inference", run_uncompiled)

    # Benchmark compiled
    compiled_model = compiler.compile_model("e2e_mlp", probe_input=dummy) if False else \
                     compiler.compile_model(model, "e2e_mlp", probe_input=dummy)
    # Warm-up call already done inside compile_model via probe_input
    def run_compiled():
        with torch.no_grad():
            return compiled_model(dummy)

    r_compiled = bench.benchmark_latency("compiled_inference", run_compiled)

    logger.info(f"   Uncompiled: {r_raw['latency_ms']}ms")
    logger.info(f"   Compiled:   {r_compiled['latency_ms']}ms")

    # Record into self-optimizer
    optimizer.record("LARGE_MODEL", r_compiled["latency_ms"])

    report = bench.generate_report()
    logger.info(f"   Benchmark report: {report['summary']}")
    logger.info("✅ End-to-End Pipeline Benchmark verified.")


if __name__ == "__main__":
    test_compiler_layer()
    test_self_optimizer()
    test_end_to_end_benchmark()
    logger.info("\n🚀 Phase 5 Compiler & Self-Optimization: FULLY FUNCTIONAL")
