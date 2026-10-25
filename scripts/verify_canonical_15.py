"""
scripts/verify_canonical_15.py
==============================
Canonical 15-Workload Independent Verification & Gate Runner CLI.

Executes strict fail-closed 5-state machine across all 15 canonical workloads.
Validates candidate implementations against textbook independent oracles
under primary, edge, and adversarial test vectors.

Usage:
    python scripts/verify_canonical_15.py [--output reports/canonical_15_verification.json] [--seed 42]
"""

import argparse
from datetime import datetime, timezone
import json
import os
import sys
import time

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hyper.canonical.workload_registry import CANONICAL_REGISTRY, CANONICAL_15_WORKLOAD_IDS
from hyper.canonical.verification_state_machine import StrictVerificationRunner, VerificationStatus
from hyper.canonical.hardware_backends import HARDWARE_BACKEND
from hyper.canonical.verified_cache import VERIFIED_CACHE


def run_verification(output_path: str, seed: int = 42, prefer_igpu: bool = True, verbose: bool = False) -> int:
    print("=" * 70)
    print("LEO/HYPER — Strict Canonical 15-Workload Independent Verification")
    print("=" * 70)

    t0 = time.perf_counter()
    report = StrictVerificationRunner.verify_all_canonical_workloads(seed=seed, prefer_igpu=prefer_igpu)
    total_duration_ms = (time.perf_counter() - t0) * 1000.0

    print(f"\nVerification executed in {total_duration_ms:.2f}ms across {report.total_workloads} workloads.\n")
    print(f"{'#':<3} {'Workload ID':<28} {'Exactness':<24} {'Backend':<22} {'Adv':<10} {'Status':<8}")
    print("-" * 98)

    for i, wid in enumerate(CANONICAL_15_WORKLOAD_IDS, start=1):
        rec = report.records.get(wid)
        if rec:
            adv_str = f"{rec.adversarial_cases_passed}/{rec.adversarial_cases_tested}"
            print(f"{i:<3} {rec.workload_id:<28} {rec.exactness_class:<24} {rec.backend_used:<22} {adv_str:<10} {rec.status.value:<8}")
        else:
            print(f"{i:<3} {wid:<28} {'UNKNOWN':<24} {'NONE':<22} {'0/0':<10} {'NOT_RUN':<8}")

    print("-" * 98)
    print(f"Summary: {report.pass_count} PASS | {report.fail_count} FAIL | {report.unknown_count} UNKNOWN | {report.unsupported_count} UNSUPPORTED | {report.blocked_count} BLOCKED")
    print(f"15/15 Aggregate Result: {'VERIFIED PASS' if report.is_15_of_15_verified else 'FAILED'}")

    # Prepare structured JSON
    profile = HARDWARE_BACKEND.profile
    out_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "reproducibility_seed": seed,
        "total_workloads": report.total_workloads,
        "pass_count": report.pass_count,
        "fail_count": report.fail_count,
        "unknown_count": report.unknown_count,
        "unsupported_count": report.unsupported_count,
        "blocked_count": report.blocked_count,
        "not_run_count": report.not_run_count,
        "is_15_of_15_verified": report.is_15_of_15_verified,
        "status_summary": report.status_summary,
        "hardware_environment": profile.to_dict(),
        "disclosures": {
            "igpu_execution": "VERIFIED (Physical Intel UHD Graphics via OpenVINO)" if profile.probe_test_passed else "NOT_AVAILABLE",
            "discrete_gpu_parity": "NOT_MEASURED (No discrete NVIDIA GPU present on host laptop)",
            "universal_gpu_replacement": "NOT_ESTABLISHED (Scientific Boundary: Subsumption applies only when mathematical invariants are proven)",
        },
        "records": {k: v.to_dict() for k, v in report.records.items()},
        "cache_telemetry": VERIFIED_CACHE.stats(),
    }

    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print(f"\n[OK] Canonical 15 Verification Report written to: {output_path}")

    return 0 if report.is_15_of_15_verified else 1


def main():
    parser = argparse.ArgumentParser(description="LEO/HYPER Canonical 15 Independent Verifier")
    parser.add_argument("--output", "-o", default="reports/canonical_15_verification.json", help="Path for JSON report")
    parser.add_argument("--seed", "-s", type=int, default=42, help="Deterministic random seed")
    parser.add_argument("--prefer-igpu", action="store_true", default=True, help="Prefer iGPU for supported workloads")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose execution logging")
    args = parser.parse_args()

    exit_code = run_verification(output_path=args.output, seed=args.seed, prefer_igpu=args.prefer_igpu, verbose=args.verbose)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
