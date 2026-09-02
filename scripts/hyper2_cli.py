"""
scripts/hyper2_cli.py
HYPER 2.0 Standalone Command-Line Interface (CLI).
"""

import sys
import os
import argparse
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from hyper_v2.api.orchestrator import Hyper2Orchestrator
from hyper_v2.audit.benchmark_runner import BenchmarkRunner
from hyper_v2.audit.holdout_runner import HoldoutRunner
from hyper_v2.audit.report_generator import ReportGenerator
from hyper_v2.execution.device_manager import DeviceManager
from hyper_v2.compiler.contract_compiler import ContractCompiler, ExecutionTrack
from hyper_v2.workloads.suite_15 import WorkloadSuite15


def main():
    parser = argparse.ArgumentParser(
        prog="hyper2",
        description="HYPER 2.0 Autonomous Computation Compiler & Heterogeneous Runtime CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. Hardware
    subparsers.add_parser("hardware", help="Display physical CPU and Intel UHD iGPU topology")

    # 2. Audit
    subparsers.add_parser("audit", help="Run full 15-workload dual-track benchmark audit")

    # 3. Holdout
    subparsers.add_parser("holdout", help="Run blind holdout and adversarial test suite")

    # 4. Report
    subparsers.add_parser("report", help="Generate all markdown, JSON, and CSV audit reports")

    # 5. Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze mathematical necessity of a workload")
    analyze_parser.add_argument("workload", type=str, default="gemm", nargs="?")

    # 6. Execute
    exec_parser = subparsers.add_parser("execute", help="Execute workload with autonomous strategy")
    exec_parser.add_argument("workload", type=str, default="gemm", nargs="?")
    exec_parser.add_argument("--track", type=str, choices=["exact", "contract"], default="contract")

    # 7. Benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Benchmark specific workload or all")
    bench_parser.add_argument("workload", type=str, default="all", nargs="?")

    args = parser.parse_args()

    if args.command == "hardware":
        hw = DeviceManager.get_hardware_profile()
        print(json.dumps(hw, indent=2))

    elif args.command == "audit":
        print("Running HYPER 2.0 Full Dual-Track Audit...")
        data = BenchmarkRunner.run_full_audit()
        print(json.dumps(data["summary"], indent=2))

    elif args.command == "holdout":
        print("Running HYPER 2.0 Blind Holdout Evaluation...")
        data = HoldoutRunner.run_blind_holdout()
        print(json.dumps(data, indent=2))

    elif args.command == "report":
        print("Generating HYPER 2.0 Audit Reports in reports/hyper_2_0/ ...")
        paths = ReportGenerator.generate_all_reports()
        print(json.dumps(paths, indent=2))

    elif args.command == "analyze":
        payload = {"contract": {"workload_id": args.workload}}
        report = Hyper2Orchestrator.analyze_workload(payload)
        print(json.dumps(report, indent=2))

    elif args.command == "execute":
        track = ExecutionTrack.TRACK_A_EXACT if args.track == "exact" else ExecutionTrack.TRACK_B_CONTRACT
        contract = ExecutionContract(workload_id=args.workload, track=track)
        if "gemm" in args.workload.lower():
            res = WorkloadSuite15.run_dense_fp32_gemm(contract)
        elif "fft" in args.workload.lower():
            res = WorkloadSuite15.run_fft_2d_spectral(contract)
        elif "nbody" in args.workload.lower():
            res = WorkloadSuite15.run_nbody_astrodynamics(contract)
        else:
            res = WorkloadSuite15.run_vector_reduction(contract)
        print(json.dumps(res, indent=2))

    elif args.command == "benchmark":
        data = BenchmarkRunner.run_full_audit()
        print(json.dumps(data["summary"], indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
