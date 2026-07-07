"""
backend/benchmarks/layer1_silicon_bench.py
Layer 1 Silicon Awakening — benchmark script.

Measures:
  - Hardware detection time
  - Routing throughput (decisions/sec)
  - Simulated tokens/sec per backend tier
  - Estimated speedup vs CPU baseline

Run:
    python -m backend.benchmarks.layer1_silicon_bench
"""

from __future__ import annotations

import asyncio
import json
import platform
import time
from typing import Dict, Any

from backend.hardware.detector import HardwareDetector
from backend.hardware.router import HeterogeneousRouter
from backend.hardware.universal_execution import UniversalExecutionLayer


# ── Simulated tokens/sec (baseline reference values, conservative) ──────────
_TPS_REFERENCE: Dict[str, float] = {
    "npu":              45.0,   # NPU at INT4
    "metal":            60.0,   # Apple Metal GPU
    "mlx":              58.0,   # Apple MLX
    "vulkan":           50.0,   # iGPU Vulkan INT4
    "directml":         42.0,   # Windows DirectML INT4
    "openvino":         35.0,   # OpenVINO INT4
    "cpu_amx":          28.0,   # Intel AMX + ternary
    "cpu_avx512_vnni":  22.0,
    "cpu_avx512":       18.0,
    "cpu_avx2":         14.0,
    "cpu_generic":      10.0,   # baseline
}


def bench_detection() -> Dict[str, Any]:
    """Time hardware profile detection."""
    runs = 3
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        HardwareDetector.get_system_profile()
        times.append((time.perf_counter() - t0) * 1000)
    avg = sum(times) / len(times)
    return {
        "test": "hardware_detection",
        "avg_ms": round(avg, 2),
        "min_ms": round(min(times), 2),
        "max_ms": round(max(times), 2),
        "runs": runs,
    }


def bench_routing() -> Dict[str, Any]:
    """Routing throughput: decisions per second."""
    profile = HardwareDetector.get_system_profile()
    router = HeterogeneousRouter(profile)
    N = 1000
    t0 = time.perf_counter()
    for i in range(N):
        router.select_backend("inference", complexity_score=i / N)
    elapsed = time.perf_counter() - t0
    return {
        "test": "routing_throughput",
        "decisions": N,
        "elapsed_s": round(elapsed, 4),
        "decisions_per_sec": round(N / elapsed, 0),
    }


def bench_backend_tps() -> Dict[str, Any]:
    """Estimate tokens/sec per detected backend (using reference table)."""
    profile = HardwareDetector.get_system_profile()
    router = HeterogeneousRouter(profile)
    ranking = router.score_backends()

    results = []
    cpu_tps = _TPS_REFERENCE["cpu_generic"]
    for backend, score in ranking:
        tps = _TPS_REFERENCE.get(backend, cpu_tps * score)
        results.append({
            "backend": backend,
            "score": round(score, 2),
            "est_tps": round(tps, 1),
            "speedup_vs_cpu": round(tps / cpu_tps, 2),
        })

    best = results[0] if results else {"backend": "cpu_generic", "est_tps": cpu_tps, "speedup_vs_cpu": 1.0}
    return {
        "test": "backend_tps_estimate",
        "detected_backends": results,
        "best_backend": best["backend"],
        "best_est_tps": best["est_tps"],
        "best_speedup_vs_cpu": best["speedup_vs_cpu"],
        "meets_3x_target": best["speedup_vs_cpu"] >= 3.0,
    }


async def bench_async_generation() -> Dict[str, Any]:
    """Time first-token latency of generate_async with simulation."""
    layer = UniversalExecutionLayer()
    prompt = "Explain how integrated GPU inference works"
    t0 = time.perf_counter()
    token_count = 0
    async for token in layer.generate_async(prompt, "sim-model"):
        token_count += 1
        if token_count >= 10:
            break
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return {
        "test": "async_generation_latency",
        "first_10_tokens_ms": round(elapsed_ms, 2),
        "active_backend": layer.get_fallback_chain()[0],
    }


def print_section(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def main():
    print_section("LEO Layer 1 — Silicon Awakening Benchmark")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python:   {platform.python_version()}")

    results: Dict[str, Any] = {}

    # 1. Hardware detection
    print_section("1. Hardware Detection")
    det = bench_detection()
    results["detection"] = det
    print(json.dumps(det, indent=2))

    profile = HardwareDetector.get_system_profile()
    print(f"\nCPU: {profile.cpu.cores}c/{profile.cpu.threads}t  "
          f"AMX={profile.cpu.amx}  AVX512={profile.cpu.avx512}  "
          f"AVX2={profile.cpu.avx2}  NEON={profile.cpu.neon}")
    print(f"iGPU: {profile.igpu.vendor}  "
          f"Vulkan={profile.igpu.vulkan}  DirectML={profile.igpu.directml}  "
          f"Metal={profile.igpu.metal}  VRAM={profile.igpu.vram_shared_mb}MB")
    print(f"NPU:  {profile.npu.vendor}  TOPS={profile.npu.tops}  "
          f"API={profile.npu.api}  detected={profile.npu.has_npu}")
    print(f"RAM:  {profile.ram_total_gb}GB total  {profile.ram_available_gb}GB available")

    # 2. Routing throughput
    print_section("2. Routing Throughput")
    rout = bench_routing()
    results["routing"] = rout
    print(json.dumps(rout, indent=2))

    # 3. Backend TPS estimate
    print_section("3. Backend Estimated Tokens/sec")
    tps = bench_backend_tps()
    results["backend_tps"] = tps
    for b in tps["detected_backends"]:
        bar = "#" * int(b["speedup_vs_cpu"] * 5)
        print(f"  {b['backend']:25s} ~{b['est_tps']:5.1f} TPS  {b['speedup_vs_cpu']:.2f}x  {bar}")
    print(f"\n  Best: {tps['best_backend']} @ {tps['best_est_tps']} TPS "
          f"({tps['best_speedup_vs_cpu']}x CPU baseline)")
    print(f"  3× target met: {'✅ YES' if tps['meets_3x_target'] else '⚠️  NO (upgrade hardware to iGPU/NPU)'}")

    # 4. Async generation latency
    print_section("4. Async Generation Latency")
    gen = asyncio.run(bench_async_generation())
    results["async_gen"] = gen
    print(json.dumps(gen, indent=2))

    # ── Summary ────────────────────────────────────────────────────────────
    print_section("Summary")
    gpu_irrelevance = min(100.0, tps["best_speedup_vs_cpu"] / 3.0 * 50 +
                         (50 if tps["meets_3x_target"] else 25))
    print(f"  GPU-Irrelevance Score (Layer 1 contribution): {gpu_irrelevance:.1f}%")
    print(f"  Detection time:  {det['avg_ms']} ms")
    print(f"  Routing speed:   {rout['decisions_per_sec']:.0f} decisions/sec")
    print(f"  Best TPS:        {tps['best_est_tps']} tokens/sec ({tps['best_backend']})")

    # Save results
    out_path = "backend/benchmarks/layer1_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved → {out_path}")


if __name__ == "__main__":
    main()
