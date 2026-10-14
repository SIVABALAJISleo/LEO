"""
leo/parity/__main__.py
======================
CLI entry point for the LEO / HYPER Contract Parity Engine.

Usage:
  python -m leo.parity run       # Run 3 warmup + 30 timed reps, output certificates
  python -m leo.parity cold      # Run zero-repetition cold suite (cache disabled)
  python -m leo.parity falsify   # Run full adversarial self-falsification suite
  python -m leo.parity soak      # Run sustained thermal soak test (default 10 min)
"""

from __future__ import annotations
import argparse
import sys
from .runner import ParityBenchmarkRunner
from .falsify import ParityFalsificationHarness


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LEO / HYPER: Contract-Driven, Falsifiable Parity Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # Command: run
    run_parser = subparsers.add_parser("run", help="Run 3 warmup + 30 timed reps and emit certificates")
    run_parser.add_argument("--warmup", type=int, default=3, help="Warmup repetitions (default: 3)")
    run_parser.add_argument("--reps", type=int, default=30, help="Timed repetitions (default: 30)")
    run_parser.add_argument("--contracts", type=str, default="contracts.yaml", help="Path to contracts.yaml")
    run_parser.add_argument("--output-dir", type=str, default="reports/parity_certificates", help="Output directory")

    # Command: cold
    cold_parser = subparsers.add_parser("cold", help="Run zero-repetition cold suite with cache disabled")
    cold_parser.add_argument("--contracts", type=str, default="contracts.yaml", help="Path to contracts.yaml")
    cold_parser.add_argument("--output-dir", type=str, default="reports/parity_certificates", help="Output directory")

    # Command: falsify
    falsify_parser = subparsers.add_parser("falsify", help="Run adversarial self-falsification batteries")
    falsify_parser.add_argument("--contracts", type=str, default="contracts.yaml", help="Path to contracts.yaml")

    # Command: soak
    soak_parser = subparsers.add_parser("soak", help="Run sustained thermal soak benchmark")
    soak_parser.add_argument("--duration-minutes", type=float, default=10.0, help="Duration in minutes (default: 10.0)")
    soak_parser.add_argument("--contracts", type=str, default="contracts.yaml", help="Path to contracts.yaml")

    args = parser.parse_args()

    if args.command == "run" or args.command is None:
        warmup = getattr(args, "warmup", 3)
        reps = getattr(args, "reps", 30)
        c_path = getattr(args, "contracts", "contracts.yaml")
        out_dir = getattr(args, "output_dir", "reports/parity_certificates")

        runner = ParityBenchmarkRunner(contracts_path=c_path)
        certs = runner.run_all(warmup_reps=warmup, timed_reps=reps, allow_cache=True, output_dir=out_dir)
        sys.exit(0 if all(c.status == "PASS" for c in certs) else 1)

    elif args.command == "cold":
        c_path = getattr(args, "contracts", "contracts.yaml")
        out_dir = getattr(args, "output_dir", "reports/parity_certificates")

        runner = ParityBenchmarkRunner(contracts_path=c_path)
        certs = runner.run_all(warmup_reps=0, timed_reps=10, allow_cache=False, output_dir=out_dir)
        sys.exit(0 if all(c.status == "PASS" for c in certs) else 1)

    elif args.command == "falsify":
        c_path = getattr(args, "contracts", "contracts.yaml")
        harness = ParityFalsificationHarness(contracts_path=c_path)
        report = harness.run_all_falsifications()
        sys.exit(0 if report["all_passed"] else 1)

    elif args.command == "soak":
        duration = getattr(args, "duration_minutes", 10.0)
        c_path = getattr(args, "contracts", "contracts.yaml")
        runner = ParityBenchmarkRunner(contracts_path=c_path)
        report = runner.run_soak(duration_minutes=duration)
        sys.exit(0 if not report["thermal_throttling_detected"] else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
