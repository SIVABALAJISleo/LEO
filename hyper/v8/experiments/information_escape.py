"""
hyper/v8/experiments/information_escape.py
==========================================
HYPER_INFORMATION_ESCAPE Experiment.

Scientific investigation of Information Escape:
Can matrix multiplication results be derived from a compressed lower-dimensional
representation without computing the full dense N x N intermediate state?

Hypothesis:
For rank-r matrices (r << N), factoring A into U (N x r) and V (r x N) enables
evaluating (U @ (V @ B)) in O(N^2 * r) FLOPs rather than O(N^3), achieving both
information compression and exact or bounded contract compliance.

Hardware Target: Lenovo IdeaPad Slim 3 15IAH8 (Intel Core i5-12450H)
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

import numpy as np

from hyper.v8.contract import numerical_contract, VerificationStatus
from hyper.v8.benchmark import BenchmarkHarnessV2


def run_information_escape_experiment(N: int = 256, ranks: List[int] = [1, 2, 4, 8, 16, 32, 64, 128]) -> Dict[str, Any]:
    print("=" * 78)
    print("HYPER v8 EXPERIMENT 2: HYPER_INFORMATION_ESCAPE (DIMENSIONALITY SWEEP)")
    print(f"Matrix Dimension: {N}x{N} | Tested Intrinsic Ranks: {ranks}")
    print("=" * 78)

    harness = BenchmarkHarnessV2(warmup_runs=3, measurement_runs=10)
    results = []

    rng = np.random.default_rng(2026)
    B = rng.standard_normal((N, N)).astype(np.float32)

    # Reference Dense GEMM time
    A_dense = rng.standard_normal((N, N)).astype(np.float32)
    ref_res = harness.benchmark(
        name="DENSE_BASELINE",
        fn=lambda: A_dense @ B,
        problem_size=(N, N),
    )
    dense_time_ms = ref_res.median_ms

    print(f"\nDense Reference Time: {dense_time_ms:.4f} ms | Baseline Storage: {N * N * 4 / 1024:.1f} KB")
    print(f"\n  {'Rank':<6} | {'Storage (KB)':<14} | {'Comp Ratio':<12} | {'Time (ms)':<10} | {'Speedup':<8} | {'Max Abs Err':<12} | {'Parity'}")
    print("  " + "-" * 76)

    for r in ranks:
        # Generate rank-r factors
        U = rng.standard_normal((N, r)).astype(np.float32)
        V = rng.standard_normal((r, N)).astype(np.float32)
        A_r = U @ V  # True rank r matrix

        # Storage: U + V = 2 * N * r floats vs N * N floats
        storage_bytes = (2 * N * r) * 4
        comp_ratio = (2 * r) / N

        # Measure Factored Execution: U @ (V @ B)
        # FLOPs = 2 * r * N^2 + 2 * N^2 * r = 4 * N^2 * r vs 2 * N^3
        factored_fn = lambda: U @ (V @ B)

        b_res = harness.benchmark(
            name=f"FACTORED_RANK_{r}",
            fn=factored_fn,
            ref_fn=lambda: A_r @ B,
            problem_size=(N, N),
            work_eliminated_pct=max(0.0, (1.0 - (2.0 * r / N)) * 100.0),
        )

        out = factored_fn()
        ref = A_r @ B
        max_err = float(np.max(np.abs(out - ref)))
        speedup = dense_time_ms / max(1e-9, b_res.median_ms)
        is_exact = max_err < 1e-4

        row = {
            "rank": r,
            "N": N,
            "storage_kb": round(storage_bytes / 1024, 2),
            "compression_ratio": round(comp_ratio, 4),
            "factored_median_ms": round(b_res.median_ms, 4),
            "dense_baseline_ms": round(dense_time_ms, 4),
            "speedup": round(speedup, 2),
            "max_abs_error": max_err,
            "parity_status": "EXACT_PARITY" if is_exact else "APPROX_PARITY",
            "break_even": b_res.median_ms < dense_time_ms,
        }
        results.append(row)

        print(f"  {r:<6} | {row['storage_kb']:<14.1f} | {row['compression_ratio']:<12.2%} | {row['factored_median_ms']:<10.4f} | {row['speedup']:<8.2f}x | {row['max_abs_error']:<12.2e} | {row['parity_status']}")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "experiment_information_escape_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n[OK] HYPER_INFORMATION_ESCAPE completed. Saved to:", out_file)
    return {"status": "SUCCESS", "results": results}


if __name__ == "__main__":
    run_information_escape_experiment()
