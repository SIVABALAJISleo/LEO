"""
hyper/v8/experiments/cpu_igpu_coop.py
=====================================
HYPER_CPU_IGPU_COOP Experiment.

Heterogeneous CPU + Intel UHD Co-Processing Experiment.
Measures real performance across:
1. CPU-Only (Intel Core i5-12450H)
2. Intel UHD iGPU (OpenCL Zero-Copy UVA, 48 EUs)
3. Hybrid Heterogeneous Partitioning (CPU + iGPU)

Hardware Target: Lenovo IdeaPad Slim 3 15IAH8
All measurements use time.perf_counter_ns().
Never claim speedup if OpenCL dispatch overhead exceeds kernel gains.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

import numpy as np

from hyper.v8.benchmark import BenchmarkHarnessV2
from hyper.v8.scheduler import HeterogeneousSchedulerV2


def run_cpu_igpu_coop_experiment(sizes: List[int] = [128, 256, 512, 1024]) -> Dict[str, Any]:
    print("=" * 78)
    print("HYPER v8 EXPERIMENT 4: HYPER_CPU_IGPU_COOP (HETEROGENEOUS BENCHMARK)")
    print("Evaluating CPU vs Intel UHD iGPU Zero-Copy vs Hybrid Partitioning")
    print("=" * 78)

    scheduler = HeterogeneousSchedulerV2(enable_igpu=True)
    cert = scheduler.get_device_certificate()

    print(f"Device Certificate:")
    print(f"  CPU:  {cert.cpu_model} ({cert.cpu_cores_physical} physical, {cert.cpu_cores_logical} logical cores)")
    print(f"  iGPU: {cert.igpu_name} ({cert.igpu_compute_units} Execution Units, Unified Memory: {cert.is_unified_memory})")
    print(f"  RAM:  {cert.ram_gb:.1f} GB Unified Physical Memory")
    print(f"  dGPU: {cert.is_dgpu} (STRICT AUDIT: No discrete GPU permitted)")

    harness = BenchmarkHarnessV2(warmup_runs=2, measurement_runs=5)
    results = []

    for N in sizes:
        print(f"\n[*] Matrix Dimension: {N}x{N}")
        rng = np.random.default_rng(500 + N)
        A = rng.standard_normal((N, N)).astype(np.float32)
        B = rng.standard_normal((N, N)).astype(np.float32)
        ref_C = A @ B

        # 1. CPU
        C_cpu, meta_cpu = scheduler.execute_gemm(A, B, force_backend="CPU")
        b_cpu = harness.benchmark(
            name=f"CPU_{N}",
            fn=lambda: scheduler.execute_gemm(A, B, force_backend="CPU")[0],
            problem_size=(N, N),
        )

        # 2. iGPU (if available)
        C_gpu, meta_gpu = scheduler.execute_gemm(A, B, force_backend="IGPU")
        b_gpu = harness.benchmark(
            name=f"IGPU_{N}",
            fn=lambda: scheduler.execute_gemm(A, B, force_backend="IGPU")[0],
            problem_size=(N, N),
        )

        # 3. Hybrid
        C_hyb, meta_hyb = scheduler.execute_gemm(A, B, force_backend="HYBRID")
        b_hyb = harness.benchmark(
            name=f"HYBRID_{N}",
            fn=lambda: scheduler.execute_gemm(A, B, force_backend="HYBRID")[0],
            problem_size=(N, N),
        )

        err_cpu = float(np.max(np.abs(C_cpu - ref_C)))
        err_gpu = float(np.max(np.abs(C_gpu - ref_C)))
        err_hyb = float(np.max(np.abs(C_hyb - ref_C)))

        row = {
            "dimension": N,
            "cpu_median_ms": round(b_cpu.median_ms, 4),
            "igpu_backend": meta_gpu["backend"],
            "igpu_median_ms": round(b_gpu.median_ms, 4),
            "hybrid_backend": meta_hyb["backend"],
            "hybrid_median_ms": round(b_hyb.median_ms, 4),
            "speedup_igpu_vs_cpu": round(b_cpu.median_ms / max(1e-9, b_gpu.median_ms), 2),
            "speedup_hybrid_vs_cpu": round(b_cpu.median_ms / max(1e-9, b_hyb.median_ms), 2),
            "max_abs_error_cpu": err_cpu,
            "max_abs_error_igpu": err_gpu,
            "max_abs_error_hybrid": err_hyb,
            "notes": meta_hyb.get("reason", ""),
        }
        results.append(row)

        print(f"  CPU Median:    {row['cpu_median_ms']:<8.4f} ms (Err: {err_cpu:.2e})")
        print(f"  iGPU Median:   {row['igpu_median_ms']:<8.4f} ms (Backend: {meta_gpu['backend']}, Speedup: {row['speedup_igpu_vs_cpu']}x, Err: {err_gpu:.2e})")
        print(f"  Hybrid Median: {row['hybrid_median_ms']:<8.4f} ms (Backend: {meta_hyb['backend']}, Speedup: {row['speedup_hybrid_vs_cpu']}x, Err: {err_hyb:.2e})")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "experiment_cpu_igpu_coop_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n[OK] HYPER_CPU_IGPU_COOP completed. Saved to:", out_file)
    return {"status": "SUCCESS", "results": results}


if __name__ == "__main__":
    run_cpu_igpu_coop_experiment()
