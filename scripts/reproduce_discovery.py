"""
scripts/reproduce_discovery.py
==============================
Independent Scientific Reproduction CLI for UCTDE (Phase 19).

Implements Section 58 and Section 75 specifications:
Automatically captures environment provenance and executes end-to-end verification
of discovered computational pathways.
"""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hyper.discovery.engine import UniversalComputationalDiscoveryEngine
from hyper.discovery.discovery_experiments import DiscoveryExperimentSuite
from hyper.discovery.capability_registry import CapabilityRegistry


def get_git_commit() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return "git_unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description="LEO / HYPER Discovery Reproduction CLI")
    parser.add_argument("--quick", action="store_true", help="Run fast verification suite")
    parser.add_argument("--export-report", type=str, default="reports/discovery_reproduction_report.json")
    args = parser.parse_args()

    print("=================================================================")
    print(" LEO / HYPER OMEGA - UNIVERSAL COMPUTATIONAL DISCOVERY REPRODUCTION ")
    print("=================================================================")

    provenance = {
        "git_commit": get_git_commit(),
        "python_version": platform.python_version(),
        "os": platform.platform(),
        "cpu": platform.processor(),
        "target_hardware": "Intel Core i5-12450H (8 cores / 12 threads) + Intel UHD Graphics (48 EUs) + 16GB RAM",
        "timestamp": time.time(),
    }
    print(f"Commit: {provenance['git_commit']}")
    print(f"Platform: {provenance['os']}")
    print(f"Target: {provenance['target_hardware']}\n")

    # 1. Capability Registry Check
    registry = CapabilityRegistry()
    maturity = registry.get_system_maturity_level()
    print(f"[*] Capability Registry: {len(registry.list_features())} features registered.")
    print(f"[*] Verified System Maturity Level: {maturity.value}\n")

    # 2. Run Discovery Experiments
    print("[*] Executing multi-domain discovery suite under baseline discipline...")
    suite = DiscoveryExperimentSuite()
    res = suite.run_suite()

    print(f"[+] Completed {res['experiments_run']} experiments.")
    print(f"[+] All Pathways Verified: {res['all_verified']}")

    for exp in res["results"]:
        print(f"    - {exp['workload_name']}: {exp['measured_speedup']}x speedup | Verified: {exp['is_verified']} | Proof: {exp['proof_status']}")

    # 3. Export reproduction record
    os.makedirs(os.path.dirname(args.export_report), exist_ok=True)
    report = {
        "provenance": provenance,
        "system_maturity_level": maturity.value,
        "experiment_results": res,
    }
    with open(args.export_report, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] Scientific reproduction report exported to: {args.export_report}")
    print("=================================================================")


if __name__ == "__main__":
    main()
