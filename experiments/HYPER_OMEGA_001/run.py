"""
experiments/HYPER_OMEGA_001/run.py
==================================
Phase 23: Canonical HYPER-OMEGA GEMM Breakthrough Experiment.
Problem: C = A x B
Conditions:
- Full output
- Exact declared precision (FP32)
- Random dense matrices
- Cache disabled (cold start)
- No precomputation
- No external compute
- No approximation
- Independent Freivalds-style randomized verification
- Hostile adversarial matrix falsification
- Out-of-distribution holdout evaluation
- Complete measurement of FLOPs, memory bytes, latencies, and CPU/iGPU utilization.
"""

import os
import sys
import json

# Ensure root directory in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from benchmarks.hyper_omega_001_gemm import run_gemm_benchmark


def main():
    print("\n" + "=" * 65)
    print("  LAUNCHING PHASE 23: EXPERIMENT HYPER_OMEGA_001")
    print("=" * 65 + "\n")
    results = run_gemm_benchmark()
    out_dir = os.path.dirname(os.path.abspath(__file__))
    res_file = os.path.join(out_dir, "results.json")
    with open(res_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[*] Experiment HYPER_OMEGA_001 completed. Manifest: {res_file}")


if __name__ == "__main__":
    main()
