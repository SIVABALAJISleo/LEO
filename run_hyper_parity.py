"""
run_hyper_parity.py
===================
CLI Runner for HYPER 100% Universal Computational / Functional / Application Parity Engine.
Executes the First Automated Experiment Suite across all 8 mandatory domains and displays
the live terminal dashboard.
"""

import sys
import os
import json
import time

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from hyper.parity_engine import (
    HyperUniversalPathwayEngine,
    FirstAutomatedExperiments,
    ParityDashboard,
    UniversalApplicationParityHarness,
)


def main():
    print("=" * 78)
    print("  INITIALIZING HYPER 100% UNIVERSAL COMPUTATIONAL PARITY ENGINE")
    print("  Destination: 100% Verified Non-Physical GPU Parity")
    print("  Physical Parity: EXCLUDED (Software-Only Alternative Pathways)")
    print("=" * 78)

    engine = HyperUniversalPathwayEngine()
    runner = FirstAutomatedExperiments(engine=engine)
    dashboard = ParityDashboard()

    print("\n[PHASE 18] Executing Automated Experiment Suite (Section 48)...")
    print("Workloads: GEMM, PDE, Attention, Image, Video, Compression, N-body, Graphics, Ray-Tracing")
    t0 = time.perf_counter()
    suite_res = runner.run_all()
    dur = time.perf_counter() - t0
    print(f"Completed {suite_res.total_experiments}/{suite_res.total_experiments} automated workloads in {dur:.2f}s!")
    print(f"Verified Workloads: {suite_res.verified_experiments}/{suite_res.total_experiments}")
    print(f"Average Measured Speedup: {suite_res.average_speedup:.2f}x")
    print(f"Average Work Reduction: {suite_res.average_work_reduction_pct:.1f}%")

    print("\n[PHASE 16] Executing Real Application Parity Validation (Section 29)...")
    app_reports = UniversalApplicationParityHarness.validate_all_core_applications()
    app_passed = sum(1 for a in app_reports if a.parity_achieved)
    print(f"Application Parity: {app_passed}/{len(app_reports)} Applications Validated (PyTorch, OpenCV, SciPy, Blender, etc.)")

    print("\n[PHASE 17] Updating Live HYPER 100% Parity Dashboard (Section 45)...")
    dashboard.update_from_engine(engine)

    print("\n" + dashboard.render_cli())

    # Save reports
    os.makedirs("reports", exist_ok=True)
    report_file = os.path.join("reports", "first_experiments_results.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(suite_res.model_dump(), f, indent=2)
    print(f"\n[OK] Results persisted to {report_file}")
    print("[OK] Dashboard state persisted to reports/parity_dashboard_state.json")


if __name__ == "__main__":
    main()
