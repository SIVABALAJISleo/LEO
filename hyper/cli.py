"""
hyper/cli.py
============
Official Command-Line Interface for LEO/HYPER.
Fulfills Phase 2 requirement:
    python -m hyper.cli hardware-profile
"""

import argparse
import json
import sys
from hyper.hardware import get_hardware_profile, validate_model_presence

def main():
    parser = argparse.ArgumentParser(
        prog="hyper",
        description="LEO/HYPER Verified Computation-Elimination Runtime CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # hardware-profile
    hw_parser = subparsers.add_parser(
        "hardware-profile",
        help="Report dynamic hardware, environment, and backend capabilities in JSON"
    )
    hw_parser.add_argument(
        "--pretty", action="store_true", default=True,
        help="Format JSON with indentation (default: True)"
    )

    # validate-model
    model_parser = subparsers.add_parser(
        "validate-model",
        help="Validate presence and readiness of an inference model"
    )
    model_parser.add_argument(
        "model_path", type=str,
        help="Path to model weights / ONNX / IR file"
    )

    # run-benchmarks
    bench_parser = subparsers.add_parser(
        "run-benchmarks",
        help="Run master verified benchmark suite across host hardware"
    )
    bench_parser.add_argument(
        "--runs", type=int, default=15,
        help="Number of measured benchmark runs (default: 15)"
    )

    args = parser.parse_args()

    if args.command == "hardware-profile":
        profile = get_hardware_profile()
        indent = 2 if args.pretty else None
        print(json.dumps(profile, indent=indent))
        sys.exit(0)

    elif args.command == "validate-model":
        res = validate_model_presence(args.model_path)
        print(json.dumps(res, indent=2))
        sys.exit(0 if res.get("model_valid") else 1)

    elif args.command == "run-benchmarks":
        from hyper.benchmark.master_benchmark import run_master_benchmarks
        res = run_master_benchmarks(warmup_runs=5, measured_runs=args.runs)
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
