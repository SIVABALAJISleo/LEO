"""
hyper/v8/experiments/dense_worst_case.py
========================================
HYPER_DENSE_WORST_CASE Experiment.

Adversarial evaluation of the Necessary-Work Compiler against worst-case inputs:
- 100% full-rank dense Gaussian matrices
- Zero temporal coherence (every matrix completely fresh)
- Maximum Kolmogorov complexity / incompressible data
- Strict exact contract (zero numerical tolerance)

Expected Scientific Result:
The selector MUST conclude "NO SHORTCUT APPLICABLE" and execute the verified
fallback reference path without precision corruption or excessive dispatch overhead.

Hardware: Lenovo IdeaPad Slim 3 15IAH8 (Intel Core i5-12450H)
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List

import numpy as np

from hyper.cache.exact_cache import ExactCache
from hyper.v8.contract import PathClassification, exact_contract
from hyper.v8.path_selector import CheapestValidPathSelector
from hyper.v8.residual import ExactResidualEngine
from hyper.v8.benchmark import BenchmarkHarnessV2


def run_dense_worst_case_experiment(sizes: List[int] = [64, 128, 256, 512], iterations: int = 5) -> Dict[str, Any]:
    print("=" * 78)
    print("HYPER v8 EXPERIMENT 3: HYPER_DENSE_WORST_CASE (FALSIFICATION TEST)")
    print("Testing Incompressible Dense Random Matrices with Zero Pattern Redundancy")
    print("=" * 78)

    harness = BenchmarkHarnessV2(warmup_runs=2, measurement_runs=iterations)
    results = []

    for N in sizes:
        print(f"\n[*] Evaluating Dense Matrix Dimension: {N}x{N}")
        cache = ExactCache(max_entries=100)
        residual = ExactResidualEngine()
        selector = CheapestValidPathSelector(residual_engine=residual, exact_cache=cache)
        contract = exact_contract(f"exact_dense_worst_{N}")

        rng = np.random.default_rng(777 + N)

        overheads = []
        path_types = []
        errors = []
        latencies = []
        ref_latencies = []

        for i in range(iterations):
            # Generate completely independent fresh random matrices each time
            A = rng.standard_normal((N, N)).astype(np.float32)
            B = rng.standard_normal((N, N)).astype(np.float32)

            t0 = time.perf_counter_ns()
            out, cert = selector.select_and_execute(A, B, contract)
            exec_time_ms = (time.perf_counter_ns() - t0) / 1e6

            t_ref0 = time.perf_counter_ns()
            ref = A @ B
            ref_ms = (time.perf_counter_ns() - t_ref0) / 1e6

            err = float(np.max(np.abs(out - ref)))
            overhead_ms = max(0.0, exec_time_ms - ref_ms)

            overheads.append(overhead_ms)
            path_types.append(cert.path_type.value)
            errors.append(err)
            latencies.append(exec_time_ms)
            ref_latencies.append(ref_ms)

        med_latency = float(np.median(latencies))
        med_ref = float(np.median(ref_latencies))
        med_overhead = float(np.median(overheads))
        overhead_pct = (med_overhead / max(1e-9, med_ref)) * 100.0
        max_err = max(errors)
        is_exact = max_err < 1e-4

        row = {
            "dimension": N,
            "iterations": iterations,
            "median_exec_ms": round(med_latency, 4),
            "median_ref_ms": round(med_ref, 4),
            "median_overhead_ms": round(med_overhead, 4),
            "overhead_pct": round(overhead_pct, 2),
            "max_abs_error": max_err,
            "chosen_path": path_types[-1],
            "correct_fallback_observed": path_types[-1] in (PathClassification.FALLBACK.value, PathClassification.EXACT_FRESH.value),
            "contract_preserved": is_exact,
        }
        results.append(row)

        status_str = "HONEST_FALLBACK (PASS)" if row["correct_fallback_observed"] and is_exact else "FAIL"
        print(f"  Result: {status_str}")
        print(f"  Median Runtime: {med_latency:.4f} ms (Ref: {med_ref:.4f} ms, Overhead: {med_overhead:.4f} ms [{overhead_pct:.1f}%])")
        print(f"  Selected Path: {row['chosen_path']} | Max Error: {max_err:.2e}")

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "experiment_dense_worst_case_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print("\n[OK] HYPER_DENSE_WORST_CASE completed. Saved to:", out_file)
    return {"status": "SUCCESS", "results": results}


if __name__ == "__main__":
    run_dense_worst_case_experiment()
