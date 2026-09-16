"""
scripts/reproduce_experiment.py
===============================
Section 43: Universal Experiment Reproducibility CLI.
Usage:
    python scripts/reproduce_experiment.py <WORKLOAD_ID>
Examples:
    python scripts/reproduce_experiment.py HYPER_OMEGA_001
    python scripts/reproduce_experiment.py HYPER_OMEGA_GRAPHICS_001
    python scripts/reproduce_experiment.py HYPER_OMEGA_LLM_001
    python scripts/reproduce_experiment.py HYPER_OMEGA_SCIENCE_001

Outputs:
    PASS / FAIL / UNKNOWN / INVALID
along with raw timing measurements, cryptographic hashes, and verification certificate.
"""

from __future__ import annotations
import sys
import os
import json

# Ensure root directory in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from benchmarks.hyper_omega_001_gemm import run_gemm_benchmark
from benchmarks.hyper_omega_graphics_001 import run_graphics_benchmark
from benchmarks.hyper_omega_llm_001 import run_llm_benchmark
from benchmarks.hyper_omega_science_001 import run_science_benchmark


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/reproduce_experiment.py <WORKLOAD_ID>")
        print("Available workloads:")
        print("  - HYPER_OMEGA_001 (or HYPER_OMEGA_001_GEMM)")
        print("  - HYPER_OMEGA_GRAPHICS_001")
        print("  - HYPER_OMEGA_LLM_001")
        print("  - HYPER_OMEGA_SCIENCE_001")
        sys.exit(1)

    workload = sys.argv[1].upper().strip()
    print(f"\n=======================================================")
    print(f"  REPRODUCING HYPER-Ω EXPERIMENT: {workload}")
    print(f"=======================================================\n")

    result = None
    if "001" in workload and "GRAPHICS" not in workload and "LLM" not in workload and "SCIENCE" not in workload:
        result = run_gemm_benchmark()
    elif "GRAPHICS" in workload:
        result = run_graphics_benchmark()
    elif "LLM" in workload:
        result = run_llm_benchmark()
    elif "SCIENCE" in workload:
        result = run_science_benchmark()
    else:
        print(f"[-] Unknown workload ID: {workload}")
        print("RESULT: INVALID")
        sys.exit(2)

    status = result.get("status", "UNKNOWN")
    v_result = result.get("verification_result", "UNKNOWN")
    adv_result = result.get("adversarial_result", "UNKNOWN")
    hold_result = result.get("holdout_result", "UNKNOWN")
    cert_hash = result.get("certificate_hash", "")
    in_hash = result.get("input_hash", "")
    out_hash = result.get("candidate_output_hash", "")
    lat = result.get("candidate_latency_ms", 0.0)

    print("\n" + "=" * 55)
    print("           REPRODUCIBILITY SUMMARY REPORT            ")
    print("=" * 55)
    print(f"Workload ID:           {workload}")
    print(f"Overall Status:        {status}")
    print(f"Verification Result:   {v_result}")
    print(f"Adversarial Result:    {adv_result}")
    print(f"Holdout Result:        {hold_result}")
    print(f"Candidate Latency:     {lat:.3f} ms")
    print(f"Input Hash:            {in_hash[:16]}...")
    print(f"Output Hash:           {out_hash[:16]}...")
    print(f"Certificate Hash:      {cert_hash}")
    print("=" * 55)

    if status in ("VERIFIED", "VERIFIED_EXACT", "VERIFIED_CONTRACT"):
        print("\nFINAL VERDICT: PASS")
        sys.exit(0)
    elif status == "INVALID":
        print("\nFINAL VERDICT: INVALID")
        sys.exit(3)
    elif status == "FAILED":
        print("\nFINAL VERDICT: FAIL")
        sys.exit(4)
    else:
        print(f"\nFINAL VERDICT: {status}")
        sys.exit(5)


if __name__ == "__main__":
    main()
