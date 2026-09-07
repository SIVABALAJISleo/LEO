"""
hyper_x/cli.py
=============================================================================
HYPER-X Command Line Interface
=============================================================================
Full CLI implementation supporting all research & benchmarking commands:
  - audit
  - hardware
  - contract
  - analyze
  - wormhole
  - discover
  - benchmark
  - verify
  - falsify
  - holdout
  - compare-nvidia
  - scorecard
  - claims
  - provenance
  - report
"""

from __future__ import annotations
import argparse
import sys
import json
from pathlib import Path
import numpy as np

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from hyper_x.hardware.fingerprint import HardwareFingerprint
from hyper_x.strict.contracts import ContractCompiler, CorrectnessMode
from hyper_x.info_boundary.compiler import InformationBoundaryCompiler
from hyper_x.cws.search import ComputationalWormholeSearch
from hyper_x.discovery.grammar import AlgorithmDiscoveryGrammar
from hyper_x.strict.verifier import VerificationHierarchy
from hyper_x.falsification.engine import ScientificFalsificationEngine
from hyper_x.holdout.blind_eval import BlindHoldoutEngine
from hyper_x.nvidia_db.database import NvidiaReferenceDatabase
from hyper_x.strict.scorecard import TotalParityScorecard
from hyper_x.master_engine import HyperXMasterEngine

def cmd_audit(args: argparse.Namespace) -> None:
    audit_file = Path("docs/hyper_x/REPOSITORY_ARCHITECTURE.md")
    if audit_file.exists():
        print(f"=== HYPER Repository Architecture Audit ({audit_file}) ===\n")
        with open(audit_file, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("Audit file not found. Run repository scanner.")

def cmd_hardware(args: argparse.Namespace) -> None:
    fp = HardwareFingerprint.detect()
    print("=== HYPER Dynamic Hardware Fingerprint ===\n")
    print(fp.to_json(indent=2))
    eligibility = fp.validate_benchmark_eligibility()
    print(f"\nTarget Hardware Eligibility: {eligibility['status']}")
    print(f"Details: {eligibility['message']}")

def cmd_contract(args: argparse.Namespace) -> None:
    c = ContractCompiler.compile(
        workload_id="GEMM_Standard",
        domain="dense_compute",
        correctness_mode=CorrectnessMode.NUMERICAL,
        tolerance_epsilon=1e-4,
        latency_limit_ms=10.0
    )
    print("=== Compiled Workload Contract ===\n")
    print(json.dumps(c.to_dict(), indent=2))

def cmd_analyze(args: argparse.Namespace) -> None:
    compiler = InformationBoundaryCompiler()
    dim = args.dim or 64
    A = np.random.randn(dim, dim).astype(np.float32)
    B = np.random.randn(dim, dim).astype(np.float32)
    graph = compiler.analyze_matrix_workload(A, B)
    summary = compiler.compile_summary(graph)
    print("=== Information Boundary Analysis ===\n")
    print(json.dumps(summary, indent=2))

def cmd_wormhole(args: argparse.Namespace) -> None:
    cws = ComputationalWormholeSearch()
    dim = args.dim or 128
    print(f"Running Computational Wormhole Search for GEMM {dim}x{dim}...\n")
    A = np.random.randn(dim, dim).astype(np.float32)
    B = np.random.randn(dim, dim).astype(np.float32)
    contract = ContractCompiler.compile(
        workload_id="CWS_GEMM",
        domain="matrix",
        correctness_mode=CorrectnessMode.NUMERICAL,
        tolerance_epsilon=1e-3
    )

    candidates = cws.search_matrix_wormholes(A, B, contract)
    ref_out = A @ B
    import time
    t0 = time.perf_counter()
    _ = A @ B
    base_ms = (time.perf_counter() - t0) * 1000.0

    print(f"{'Candidate ID':<25} | {'Speedup':<8} | {'Work Elim':<10} | {'Verified':<8} | {'CWS Score':<10}")
    print("-" * 75)
    for c in candidates:
        res = cws.evaluate_wormhole(c, ref_out, contract, base_ms)
        print(f"{res.candidate_id:<25} | {res.speedup:>7.2f}x | {res.work_elimination*100:>8.1f}% | {str(res.verified):<8} | {res.cws_score:>8.1f}%")

def cmd_discover(args: argparse.Namespace) -> None:
    disc = AlgorithmDiscoveryGrammar()
    expr = args.expr or "U @ (V @ B)"
    cand = disc.propose_candidate(
        name="Low-Rank Subspace Chain",
        family="bilinear_decomposition",
        expression=expr
    )
    print("=== Algorithm Discovery Candidate ===\n")
    print(f"Algorithm ID: {cand.algorithm_id}")
    print(f"Name:         {cand.name}")
    print(f"Family:       {cand.family}")
    print(f"Expression:   {cand.expression}")
    print(f"Novelty:      {cand.novelty.value}")
    print(f"Reference:    {cand.literature_reference}")

def cmd_benchmark(args: argparse.Namespace) -> None:
    print("Running HYPER-X Full End-to-End Benchmark Suite...")
    engine = HyperXMasterEngine()
    dim = 256
    A = np.random.randn(dim, dim).astype(np.float32)
    B = np.random.randn(dim, dim).astype(np.float32)
    res = engine.execute_workload_end_to_end(
        workload_id="HYPER_GEMM_256",
        A=A,
        B=B,
        domain="hpc_gemm",
        tolerance_epsilon=1e-3
    )
    print(f"\nWorkload:            {res['workload_id']}")
    print(f"Selected Pathway:    {res['selected_pathway']}")
    print(f"Transformations:     {', '.join(res['transformations'])}")
    print(f"Verified:            {res['verified']}")
    print(f"Speedup:             {res['speedup']}x")
    print(f"Work Elimination:    {res['work_elimination_pct']}%")
    print(f"CWS Score:           {res['cws_score']}%")
    print(f"Verification Info:   {res['verification_details']}")

def cmd_verify(args: argparse.Namespace) -> None:
    vh = VerificationHierarchy()
    dim = 64
    A = np.random.randn(dim, dim).astype(np.float32)
    B = np.random.randn(dim, dim).astype(np.float32)
    C = A @ B
    outcome = vh.verify_freivalds(C, A, B, rounds=15)
    print("=== Verification Hierarchy (Level 4 Freivalds Probe) ===\n")
    print(f"Level:      {outcome.level.name}")
    print(f"Passed:     {outcome.passed}")
    print(f"Confidence: {outcome.confidence:.6f}")
    print(f"Details:    {outcome.details}")

def cmd_falsify(args: argparse.Namespace) -> None:
    falsifier = ScientificFalsificationEngine()
    print("Executing Scientific Falsification Stress Battery...")
    res = falsifier.run_falsification_battery(
        candidate_id="CAND_GEMM_STRESS",
        workload_id="GEMM_FALSIFY",
        candidate_fn=lambda A, B: A @ B,
        reference_fn=lambda A, B: A @ B
    )
    print(f"\nCandidate: {res['candidate_id']}")
    print(f"Falsified: {res['falsified']}")
    print(f"Stress Tests Passed: {res['passed_tests']}/{res['total_stress_tests']}")

def cmd_holdout(args: argparse.Namespace) -> None:
    bhe = BlindHoldoutEngine()
    dim = 32
    A = np.random.randn(dim, dim).astype(np.float32)
    C_ref = A @ A
    bhe.register_sealed_workload("SEALED_GEMM_01", A, C_ref, "dense_compute")
    res = bhe.evaluate_holdout("SEALED_GEMM_01", lambda x: x @ x)
    print("=== Blind Holdout Evaluation & Anti-Leakage Audit ===\n")
    print(json.dumps(res, indent=2))

def cmd_compare_nvidia(args: argparse.Namespace) -> None:
    db = NvidiaReferenceDatabase()
    domain = (args.domain or "all").lower()
    print(f"=== NVIDIA Reference Platform Comparison ({domain.upper()}) ===\n")
    capabilities = ["CUDA_CORES", "TENSOR_CORES", "RT_CORES", "FP32_SIMD", "ZERO_COPY_USM", "CUBLAS", "NVENC_AV1"]
    for cap in capabilities:
        status = db.classify_capability(cap)
        print(f"  - {cap:<20}: {status.value}")

def cmd_scorecard(args: argparse.Namespace) -> None:
    sc = TotalParityScorecard()
    try:
        print(sc.format_terminal_status_box(use_ascii=False))
    except UnicodeEncodeError:
        print(sc.format_terminal_status_box(use_ascii=True))

def cmd_claims(args: argparse.Namespace) -> None:
    claims_file = Path("claims_registry.json")
    if claims_file.exists():
        with open(claims_file, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("Claims registry not found.")

def cmd_provenance(args: argparse.Namespace) -> None:
    prov_file = Path("PROVENANCE_REPORT.json")
    if prov_file.exists():
        with open(prov_file, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("Provenance report not found.")

def cmd_report(args: argparse.Namespace) -> None:
    report_file = Path("NVIDIA_TOTAL_PARITY_REPORT.md")
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("Report not found.")

def main() -> None:
    parser = argparse.ArgumentParser(description="HYPER-X Master CLI")
    subparsers = parser.add_subparsers(dest="subcommand")

    subparsers.add_parser("audit")
    subparsers.add_parser("hardware")
    subparsers.add_parser("contract")
    
    p_analyze = subparsers.add_parser("analyze")
    p_analyze.add_argument("--dim", type=int, default=64)

    p_wormhole = subparsers.add_parser("wormhole")
    p_wormhole.add_argument("--workload", type=str, default="GEMM")
    p_wormhole.add_argument("--dim", type=int, default=128)

    p_discover = subparsers.add_parser("discover")
    p_discover.add_argument("--expr", type=str, default="")

    subparsers.add_parser("benchmark")
    subparsers.add_parser("verify")
    subparsers.add_parser("falsify")
    subparsers.add_parser("holdout")

    p_comp = subparsers.add_parser("compare-nvidia")
    p_comp.add_argument("--domain", type=str, default="all")

    subparsers.add_parser("scorecard")
    subparsers.add_parser("claims")
    subparsers.add_parser("provenance")
    subparsers.add_parser("report")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    handlers = {
        "audit": cmd_audit,
        "hardware": cmd_hardware,
        "contract": cmd_contract,
        "analyze": cmd_analyze,
        "wormhole": cmd_wormhole,
        "discover": cmd_discover,
        "benchmark": cmd_benchmark,
        "verify": cmd_verify,
        "falsify": cmd_falsify,
        "holdout": cmd_holdout,
        "compare-nvidia": cmd_compare_nvidia,
        "scorecard": cmd_scorecard,
        "claims": cmd_claims,
        "provenance": cmd_provenance,
        "report": cmd_report,
    }

    handler = handlers.get(args.subcommand)
    if handler:
        handler(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
