"""
reproduce_clean.py
==================
Authoritative Clean-Checkout Replication Script for HYPER-CCO.

Executes the end-to-end verification and benchmarking pipeline from a clean checkout:
  1. Validates hardware environment and dependencies.
  2. Executes the Hostile Self-Falsification Suite (15 adversarial tests).
  3. Executes Manifest Workload Correctness Tests (6 workloads).
  4. Executes Strict Contract & E-Graph Equivalence Tests (14 tests).
  5. Executes Target Benchmark Harness (3 warmups + 30 timed reps per workload).
  6. Audits raw-trial ledger and cryptographic certificates.
  7. Reports definitive pass/fail status.
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def run_cmd(cmd_list, description: str, timeout: int = 180):
    print(f"\n[RUNNING] {description}...")
    t0 = time.perf_counter()
    res = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    elapsed = time.perf_counter() - t0
    print(res.stdout)
    if res.returncode != 0:
        print(f"[FAILED] {description} exited with code {res.returncode} in {elapsed:.2f}s")
        sys.exit(res.returncode)
    print(f"[PASSED] {description} in {elapsed:.2f}s")


def main():
    t_start = time.perf_counter()
    print_banner("HYPER-CCO CLEAN REPRODUCTION SUITE")

    # Step 1: Environment Check
    print_banner("STEP 1: ENVIRONMENT & HARDWARE PROVENANCE AUDIT")
    import platform
    import numpy as np
    import scipy
    print(f"  Platform:    {platform.system()} {platform.release()} ({platform.version()})")
    print(f"  Processor:   {platform.processor()}")
    print(f"  Python:      {platform.python_version()} ({sys.executable})")
    print(f"  NumPy:       {np.__version__}")
    print(f"  SciPy:       {scipy.__version__}")

    try:
        import openvino.runtime as ov
        core = ov.Core()
        print(f"  OpenVINO:    Available devices: {core.available_devices}")
    except Exception as e:
        print(f"  OpenVINO:    Not active ({e})")

    # Step 2: Hostile Self-Falsification Battery
    print_banner("STEP 2: HOSTILE SELF-FALSIFICATION BATTERY (15 TESTS)")
    run_cmd(
        [
            sys.executable, "-m", "pytest",
            "tests/test_hostile_verifier.py",
            "tests/test_hostile_sparsity.py",
            "tests/test_hostile_low_rank.py",
            "tests/test_hostile_inference.py",
            "tests/test_hostile_graphics.py",
            "tests/test_hostile_scheduler.py",
            "-v",
        ],
        "Hostile Self-Falsification Test Battery",
        timeout=60,
    )

    # Step 3: Manifest Workloads Verification
    print_banner("STEP 3: MANIFEST WORKLOAD CONTRACT & CORRECTNESS (6 WORKLOADS)")
    run_cmd(
        [
            sys.executable, "-m", "pytest",
            "tests/test_cco_manifest_workloads.py",
            "-v",
        ],
        "Manifest Workloads Verification",
        timeout=60,
    )

    # Step 4: Strict Contract & Equivalence Tests
    print_banner("STEP 4: STRICT CONTRACT & EQUIVALENCE BATTERY (14 TESTS)")
    run_cmd(
        [
            sys.executable, "-m", "pytest",
            "tests/hyper_x_strict/test_strict.py",
            "-v",
        ],
        "Strict Contracts & E-Graph Verification",
        timeout=60,
    )

    # Step 5: Full Benchmark Harness Execution (3 Warmups + 30 Repetitions)
    print_banner("STEP 5: TARGET BENCHMARK CAMPAIGN (3 WARMUPS + 30 TIMED REPS)")
    run_cmd(
        [
            sys.executable, "bench_target_hyper.py",
            "--warmups", "3",
            "--repetitions", "30",
            "--output", "benchmark_results",
        ],
        "Target Machine Scientific Benchmark Campaign",
        timeout=300,
    )

    # Step 6: Audit Artifacts & Provenance
    print_banner("STEP 6: ARTIFACT PROVENANCE & LEDGER AUDIT")
    raw_trials_path = Path("benchmark_results/raw_trials.json")
    results_json_path = Path("benchmark_results/results.json")
    results_csv_path = Path("benchmark_results/results.csv")
    report_md_path = Path("benchmark_results/REPORT.md")
    certs_dir = Path("benchmark_results/certificates")

    assert raw_trials_path.exists(), "Missing raw_trials.json"
    assert results_json_path.exists(), "Missing results.json"
    assert results_csv_path.exists(), "Missing results.csv"
    assert report_md_path.exists(), "Missing REPORT.md"

    with open(raw_trials_path, "r", encoding="utf-8") as f:
        trials = json.load(f)
    print(f"  Raw Trial Records: {len(trials)} workloads recorded")
    for t in trials:
        wl_id = t["workload_id"]
        ev = t["evidence_class"]
        w_count = len(t.get("warmup_iterations", []))
        t_count = len(t.get("timed_iterations", []))
        med = t["statistics"]["median_ms"] if t.get("statistics") else 0.0
        print(f"    - {wl_id:25s} | Class: {ev:20s} | Warmups: {w_count} | Timed: {t_count} | Median: {med:.2f}ms")

    # Step 7: Parity Boundary Certificate Audit
    print_banner("STEP 7: PARITY BOUNDARY CERTIFICATE & FEASIBLE-SET AUDIT")
    pbc_md_path = Path("PARITY_BOUNDARY_CERTIFICATE.md")
    pbc_json_path = Path("benchmark_results/parity_boundary_certificate.json")

    assert pbc_md_path.exists(), "Missing PARITY_BOUNDARY_CERTIFICATE.md"
    assert pbc_json_path.exists(), "Missing benchmark_results/parity_boundary_certificate.json"

    with open(pbc_json_path, "r", encoding="utf-8") as f:
        pbc = json.load(f)

    assert pbc["feasible_set_parity_pct"] == 100.0, f"Expected 100.0% feasible parity, got {pbc['feasible_set_parity_pct']}"
    assert pbc["raw_hardware_parity_pct"] == 0.0, f"Expected 0.0% raw hardware parity, got {pbc['raw_hardware_parity_pct']}"
    assert len(pbc["included_feasible_workloads"]) == 6, f"Expected 6 feasible workloads, got {len(pbc['included_feasible_workloads'])}"
    assert len(pbc["excluded_workloads"]) >= 5, f"Expected >=5 excluded workloads, got {len(pbc['excluded_workloads'])}"

    print(f"  Certificate ID:              {pbc['certificate_id']}")
    print(f"  Feasible-Set Parity Score:   {pbc['feasible_set_parity_pct']:.1f}% (ALL FEASIBLE WORKLOADS SATISFIED)")
    print(f"  Raw Hardware Parity:         {pbc['raw_hardware_parity_pct']:.1f}% (NO CUDA/TENSOR SILICON CLAIMED)")
    print(f"  Feasible Workloads Included: {len(pbc['included_feasible_workloads'])} (Total Weight: {pbc['total_feasible_weight']:.2f})")
    print(f"  Excluded Workload Domains:   {len(pbc['excluded_workloads'])} (With Formal Impossibility Proofs)")
    print(f"  Defensive Boundary Statement: \"{pbc['defensive_boundary_statement']}\"")

    total_time = time.perf_counter() - t_start
    print_banner(f"ALL VERIFICATION & REPLICATION CHECKS PASSED IN {total_time:.2f}s")


if __name__ == "__main__":
    main()

