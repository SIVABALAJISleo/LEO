"""
hyper/v8/experiments/adversarial.py
===================================
HYPER_ADVERSARIAL Experiment.

Runs the SelfFalsificationEngine across 12 pathological categories:
1.  RANDOM_DENSE_FULL_RANK
2.  IDENTITY_AND_PERMUTATION
3.  PATHOLOGICAL_SPARSITY
4.  ILL_CONDITIONED_MATRIX
5.  EXTREME_DYNAMIC_RANGE
6.  NAN_INF_INJECTION
7.  EXACT_DUPLICATE_REPETITION
8.  ADVERSARIAL_CACHE_COLLISION
9.  HIGH_FREQUENCY_ALTERNATING
10. RANK_1_PERTURBATION
11. NEAR_EPSILON_DELTA
12. ZERO_MATRIX

Scientific Requirement:
Must prove that under adversarial conditions, HYPER v8 never outputs corrupted
data, detects edge cases, preserves mathematical contracts, and falls back safely.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, List

import numpy as np

from hyper.cache.exact_cache import ExactCache
from hyper.v8.falsification import SelfFalsificationEngine
from hyper.v8.path_selector import CheapestValidPathSelector
from hyper.v8.residual import ExactResidualEngine


def run_adversarial_experiment(dimensions: List[int] = [64, 128]) -> Dict[str, Any]:
    print("=" * 78)
    print("HYPER v8 EXPERIMENT 5: HYPER_ADVERSARIAL (12-CATEGORY FALSIFICATION SUITE)")
    print("Stress Testing Resilience, Safe Fallbacks, and Contract Enforcement")
    print("=" * 78)

    cache = ExactCache(max_entries=100)
    residual = ExactResidualEngine()
    selector = CheapestValidPathSelector(residual_engine=residual, exact_cache=cache)
    engine = SelfFalsificationEngine(selector=selector)

    all_results = []
    total_tests = 0
    passed_tests = 0

    for N in dimensions:
        print(f"\n[*] Running Adversarial Gauntlet at Dimension: {N}x{N}")
        suite_res = engine.run_all(N=N)

        print(f"  {'Category':<34} | {'Status':<8} | {'Path':<18} | {'Max Err':<10} | {'Duration (ms)'}")
        print("  " + "-" * 82)

        for r in suite_res:
            total_tests += 1
            if r.passed:
                passed_tests += 1
            status_str = "PASS" if r.passed else "FAIL"
            err_str = f"{r.max_abs_error:.2e}" if not (r.max_abs_error != r.max_abs_error) else "NaN"
            print(f"  {r.category:<34} | {status_str:<8} | {r.observed_path.value:<18} | {err_str:<10} | {r.duration_ms:<8.3f}")

            item = r.as_dict()
            item["dimension"] = N
            all_results.append(item)

    print("\n" + "=" * 78)
    print(f"Adversarial Suite Summary: {passed_tests} / {total_tests} Tests Passed ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 78)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "experiment_adversarial_results.json")
    with open(out_file, "w") as f:
        json.dump(all_results, f, indent=2, default=lambda x: bool(x) if isinstance(x, (np.bool_, bool)) else str(x))

    print("[OK] HYPER_ADVERSARIAL completed. Saved to:", out_file)
    return {
        "status": "SUCCESS" if passed_tests == total_tests else "PARTIAL",
        "passed": passed_tests,
        "total": total_tests,
        "results": all_results,
    }


if __name__ == "__main__":
    run_adversarial_experiment()
