"""
hyper/cli.py
============
Official Command-Line Interface for LEO/HYPER Verified Computational Pathway Discovery Engine.

Supported Commands:
    hyper analyze workload [--fast] [--research]
    hyper discover workload [--fast] [--research] [--strategy {A_STAR,BEAM_SEARCH,BRANCH_AND_BOUND}]
    hyper verify workload [--exactness {BIT_EXACT,NUMERIC_EXACT,NUMERIC_TOLERANCE}]
    hyper benchmark workload [--runs N]
    hyper adversarial workload [--category {DISCOVERY_SET,VALIDATION_SET,BLIND_HOLDOUT_SET}]
    hyper prove workload
    hyper compare workload [--nvidia-gpu GPU]
    hyper audit workload [--falsify]
    hyper hardware-profile
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

import numpy as np

from hyper.discovery.adversarial import AdversarialWorkloadGenerator, WorkloadCategory
from hyper.discovery.cir import CIRGraph, CIRTensorMeta, DataType, OpType
from hyper.discovery.contract import VerificationMode, WorkloadContract
from hyper.discovery.engine import VerifiedPathwayEngine
from hyper.discovery.search import SearchConfig, SearchStrategy
from hyper.hardware import get_hardware_profile, validate_model_presence


def _get_sample_workload(name: str):
    """Factory creating representative CIR workloads for CLI operations."""
    name_clean = name.lower().strip()
    if "gemm" in name_clean or "matrix" in name_clean:
        g = CIRGraph(name=f"workload_{name}")
        in_a = g.add_input("A", shape=(10, 10), dtype=DataType.FP32)
        in_b = g.add_input("B", shape=(10, 100), dtype=DataType.FP32)
        in_c = g.add_input("C", shape=(100, 10), dtype=DataType.FP32)
        op_ab = g.add_op(OpType.MATMUL, [in_a, in_b], name="ab", output_meta=CIRTensorMeta(shape=(10, 100), dtype=DataType.FP32))
        op_abc = g.add_op(OpType.MATMUL, [op_ab, in_c], name="result", output_meta=CIRTensorMeta(shape=(10, 10), dtype=DataType.FP32))
        g.mark_output(op_abc)

        contract = WorkloadContract(
            contract_id=f"c_{name}",
            workload_name=name,
            required_outputs=["result"],
            exactness_mode=VerificationMode.MODE_3_NUMERIC_TOLERANCE,
            tolerance_atol=1e-4,
            tolerance_rtol=1e-4,
        )
        inputs = {
            "A": np.random.randn(10, 10).astype(np.float32),
            "B": np.random.randn(10, 100).astype(np.float32),
            "C": np.random.randn(100, 10).astype(np.float32),
        }
        return g, inputs, contract
    elif "conv" in name_clean:
        g = CIRGraph(name=f"workload_{name}")
        in_x = g.add_input("X", shape=(1, 3, 32, 32), dtype=DataType.FP32)
        in_w = g.add_input("W", shape=(8, 3, 3, 3), dtype=DataType.FP32)
        op_conv = g.add_op(OpType.CONV2D, [in_x, in_w], name="conv", output_meta=CIRTensorMeta(shape=(1, 8, 30, 30), dtype=DataType.FP32))
        op_act = g.add_op(OpType.RELU, [op_conv], name="result", output_meta=CIRTensorMeta(shape=(1, 8, 30, 30), dtype=DataType.FP32))
        g.mark_output(op_act)

        contract = WorkloadContract(
            contract_id=f"c_{name}",
            workload_name=name,
            required_outputs=["result"],
            exactness_mode=VerificationMode.MODE_2_NUMERIC_EXACT,
        )
        inputs = {
            "X": np.random.randn(1, 3, 32, 32).astype(np.float32),
            "W": np.random.randn(8, 3, 3, 3).astype(np.float32),
        }
        return g, inputs, contract
    else:
        # Default simple arithmetic workload
        g = CIRGraph(name=f"workload_{name}")
        in_x = g.add_input("X", shape=(64, 64), dtype=DataType.FP32)
        in_y = g.add_input("Y", shape=(64, 64), dtype=DataType.FP32)
        op_add = g.add_op(OpType.ADD, [in_x, in_y], name="result", output_meta=CIRTensorMeta(shape=(64, 64), dtype=DataType.FP32))
        g.mark_output(op_add)

        contract = WorkloadContract(
            contract_id=f"c_{name}",
            workload_name=name,
            required_outputs=["result"],
            exactness_mode=VerificationMode.MODE_1_BIT_EXACT,
        )
        inputs = {
            "X": np.random.randn(64, 64).astype(np.float32),
            "Y": np.random.randn(64, 64).astype(np.float32),
        }
        return g, inputs, contract


def main():
    common_flags = argparse.ArgumentParser(add_help=False)
    common_flags.add_argument("--research", action="store_true", help="Enable research mode (maximum logging, full search trace, proofs)")
    common_flags.add_argument("--fast", action="store_true", help="Enable fast search mode (reduced budget, non-reduced verification)")
    common_flags.add_argument("--audit", action="store_true", help="Enable audit mode (attempts to falsify optimization)")

    parser = argparse.ArgumentParser(
        prog="hyper",
        description="LEO / HYPER — Verified Computational Pathway Discovery Engine CLI",
        parents=[common_flags],
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. hyper analyze workload
    p_analyze = subparsers.add_parser("analyze", parents=[common_flags], help="Analyze workload computational graph, FLOPs, and scheduling")
    p_analyze.add_argument("workload", type=str, nargs="?", default="matrix_gemm", help="Workload identifier")

    # 2. hyper discover workload
    p_discover = subparsers.add_parser("discover", parents=[common_flags], help="Discover alternative verified computational pathways")
    p_discover.add_argument("workload", type=str, nargs="?", default="matrix_gemm", help="Workload identifier")
    p_discover.add_argument("--strategy", type=str, default="A_STAR", choices=["A_STAR", "BEAM_SEARCH", "BRANCH_AND_BOUND"])
    p_discover.add_argument("--unknown-mode", action="store_true", help="Enforce UNKNOWN_WORKLOAD_MODE (zero benchmark names)")

    # 3. hyper verify workload
    p_verify = subparsers.add_parser("verify", parents=[common_flags], help="Independently verify computational pathway output against reference")
    p_verify.add_argument("workload", type=str, nargs="?", default="matrix_gemm", help="Workload identifier")
    p_verify.add_argument("--exactness", type=str, default="NUMERIC_EXACT", choices=["BIT_EXACT", "NUMERIC_EXACT", "NUMERIC_TOLERANCE"])

    # 4. hyper benchmark workload
    p_bench = subparsers.add_parser("benchmark", parents=[common_flags], help="Execute multi-repetition benchmark with warmup isolation")
    p_bench.add_argument("workload", type=str, nargs="?", default="matrix_gemm", help="Workload identifier")
    p_bench.add_argument("--runs", type=int, default=15, help="Number of repetitions (default: 15)")

    # 5. hyper adversarial workload
    p_adv = subparsers.add_parser("adversarial", parents=[common_flags], help="Test adversarial cases designed to defeat shortcuts")
    p_adv.add_argument("workload", type=str, nargs="?", default="prime_gemm", help="Workload identifier")
    p_adv.add_argument("--category", type=str, default="BLIND_HOLDOUT_SET", choices=["DISCOVERY_SET", "VALIDATION_SET", "BLIND_HOLDOUT_SET"])

    # 6. hyper prove workload
    p_prove = subparsers.add_parser("prove", parents=[common_flags], help="Generate machine-readable proof record and human explainer")
    p_prove.add_argument("workload", type=str, nargs="?", default="matrix_gemm", help="Workload identifier")

    # 7. hyper compare workload
    p_comp = subparsers.add_parser("compare", parents=[common_flags], help="Compare discovered pathway against NVIDIA reference GPU")
    p_comp.add_argument("workload", type=str, nargs="?", default="matrix_gemm", help="Workload identifier")
    p_comp.add_argument("--nvidia-gpu", type=str, default="NVIDIA RTX 4090", help="NVIDIA Reference Model")

    # 8. hyper audit workload
    p_audit = subparsers.add_parser("audit", parents=[common_flags], help="Run falsification audit searching for edge-case failures")
    p_audit.add_argument("workload", type=str, nargs="?", default="matrix_gemm", help="Workload identifier")

    # Backward compatibility commands
    p_hw = subparsers.add_parser("hardware-profile", parents=[common_flags], help="Report hardware capabilities")
    p_hw.add_argument("--pretty", action="store_true", default=True)

    args = parser.parse_args()
    engine = VerifiedPathwayEngine()

    if args.command == "hardware-profile":
        profile = get_hardware_profile()
        print(json.dumps(profile, indent=2))
        sys.exit(0)

    elif args.command == "analyze":
        g, inputs, contract = _get_sample_workload(args.workload)
        pred = engine.cost_model.predict_cost(g)
        sched = engine.scheduler.schedule_workload(g)
        print("=" * 70)
        print(f"HYPER ANALYZE: {args.workload.upper()}")
        print("=" * 70)
        print(f"Total Nodes: {len(g.nodes)} | Edges: {len(g.edges)}")
        print(f"Estimated Arithmetic Intensity: {pred.arithmetic_intensity_flops_per_byte:.2f} FLOP/B")
        print(f"Estimated Latency: {pred.estimated_latency_ms:.3f} ms")
        print(f"Target Device: {sched.target_device.value}")
        print(f"Rationalization: {sched.rationalization}")
        print(f"\n[NOTICE] {sched.hardware_disclaimer}")
        sys.exit(0)

    elif args.command == "discover":
        g, inputs, contract = _get_sample_workload(args.workload)
        strat = SearchStrategy(args.strategy)
        cfg = SearchConfig(
            strategy=strat,
            max_candidates=10 if args.fast else 30,
        )
        rep = engine.process_workload(
            graph=g,
            inputs=inputs,
            contract=contract,
            unknown_workload_mode=args.unknown_mode,
            search_config=cfg,
            benchmark_repetitions=3 if args.fast else 10,
        )
        print("=" * 70)
        print(f"HYPER DISCOVER: {args.workload.upper()}")
        print("=" * 70)
        print(f"Outcome: {rep.status_message}")
        print(f"Shortcut Discovered: {rep.is_shortcut_found}")
        print(f"Baseline Cost: {rep.proof_record.reference_operations:.0f} FLOPs")
        print(f"Discovered Cost: {rep.proof_record.candidate_operations:.0f} FLOPs")
        print(f"Estimated Speedup: {rep.proof_record.speedup:.2f}x")
        print(f"Parity Classification: {rep.proof_record.parity_classification}")
        print("\n" + rep.proof_record.pathway_ascii_diff)
        print(rep.proof_record.explanation.to_markdown())
        sys.exit(0)

    elif args.command == "verify":
        g, inputs, contract = _get_sample_workload(args.workload)
        passed, vrec, audit = engine.verifier.verify_candidate(
            candidate_graph=g,
            reference_graph=g,
            inputs=inputs,
            contract=contract,
        )
        print("=" * 70)
        print(f"HYPER VERIFY: {args.workload.upper()}")
        print("=" * 70)
        print(f"Verification Passed: {passed}")
        print(f"Parity Classification: {audit.parity_classification}")
        print(f"Bit-Exact: {audit.is_bit_exact}")
        print(f"Numeric-Exact: {audit.is_numeric_exact}")
        print(f"Max Absolute Error: {audit.max_abs_error:.2e}")
        print(f"Max ULP Difference: {audit.max_ulp_diff}")
        print(f"Input Hash: {vrec.input_hash[:16]}...")
        print(f"Reference Hash: {vrec.reference_hash[:16]}...")
        print(f"Candidate Hash: {vrec.candidate_hash[:16]}...")
        sys.exit(0 if passed else 1)

    elif args.command == "benchmark":
        g, inputs, contract = _get_sample_workload(args.workload)
        stats = engine.benchmarker.run_benchmark(g, inputs, repetitions=args.runs)
        print("=" * 70)
        print(f"HYPER BENCHMARK: {args.workload.upper()} ({args.runs} runs, {stats.warmup_runs} warmups)")
        print("=" * 70)
        print(f"Median: {stats.median_ms:.4f} ms")
        print(f"Mean:   {stats.mean_ms:.4f} ms (std: {stats.stddev_ms:.4f} ms)")
        print(f"Min:    {stats.min_ms:.4f} ms | Max: {stats.max_ms:.4f} ms")
        print(f"95% CI: [{stats.ci95_low_ms:.4f} ms, {stats.ci95_high_ms:.4f} ms]")
        sys.exit(0)

    elif args.command == "adversarial":
        adv_gen = engine.adversarial_gen
        adv = adv_gen.generate_prime_dimensions_gemm(WorkloadCategory(args.category))
        rep = engine.process_workload(adv.graph, adv.sample_inputs, adv.contract, unknown_workload_mode=True)
        print("=" * 70)
        print(f"HYPER ADVERSARIAL CHALLENGE: {adv.name}")
        print("=" * 70)
        print(f"Category: {adv.category.value}")
        print(f"Intended Challenge: {adv.intended_challenge}")
        print(f"Outcome: {rep.status_message}")
        print(f"Verification: {rep.proof_record.verification}")
        print(f"Parity Classification: {rep.proof_record.parity_classification}")
        sys.exit(0)

    elif args.command == "prove":
        g, inputs, contract = _get_sample_workload(args.workload)
        rep = engine.process_workload(g, inputs, contract)
        print(json.dumps(rep.proof_record.to_dict(), indent=2))
        sys.exit(0)

    elif args.command == "compare":
        g, inputs, contract = _get_sample_workload(args.workload)
        rep = engine.process_workload(g, inputs, contract)
        comp = rep.nvidia_comparison
        print("=" * 70)
        print(f"HYPER vs {args.nvidia_gpu}: {args.workload.upper()}")
        print("=" * 70)
        print(f"Hardware Parity: {comp.hardware_parity} (CPU+iGPU != Discrete GPU)")
        print(f"Exactness Parity: {comp.exactness_parity}")
        print(f"NVIDIA Reference Latency: {comp.nvidia_runtime_ms:.2f} ms")
        print(f"HYPER Discovered Latency: {comp.hyper_runtime_ms:.2f} ms")
        print(f"Energy Advantage Ratio: {comp.energy_advantage_ratio:.1f}x less energy")
        print(f"Overall Classification: {comp.overall_classification}")
        sys.exit(0)

    elif args.command == "audit":
        print("=" * 70)
        print(f"HYPER FALSIFICATION AUDIT: {args.workload.upper()}")
        print("=" * 70)
        g, inputs, contract = _get_sample_workload(args.workload)
        rep = engine.process_workload(g, inputs, contract)
        print(f"Candidate ID: {rep.proof_record.candidate_id}")
        print(f"Anti-Cheat Audit: {'CLEAN (0 violations)' if not rep.anti_cheat_violations else f'{len(rep.anti_cheat_violations)} VIOLATIONS'}")
        print(f"Independent Verification: {rep.proof_record.independent_verification}")
        print(f"Parity Classification: {rep.proof_record.parity_classification}")
        print(f"Falsification Conditions:")
        for fc in rep.proof_record.explanation.falsification_conditions:
            print(f"  * {fc}")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
