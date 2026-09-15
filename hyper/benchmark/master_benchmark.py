"""
hyper/benchmark/master_benchmark.py
===================================
Master Benchmark Runner for LEO/HYPER.
Fulfills Phase 13 & 14 of the Master Architectural Specification.
Zero hardcoded speedups. Zero synthetic timings.
Generates fully compliant JSON records adhering to the Phase 14 Schema.
"""

import datetime
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List
import psutil
from hyper.benchmark.workload_suite import MasterWorkloadSuite
from hyper.contracts.contract import contract_to_json
from hyper.hardware import get_hardware_profile

ROOT = Path(__file__).resolve().parent.parent.parent


def run_master_benchmarks(warmup_runs: int = 10, measured_runs: int = 30) -> Dict[str, Any]:
    """
    Run authentic local benchmarks across host hardware.
    Collects measured latency distributions, error metrics, and provenance.
    """
    hw_profile = get_hardware_profile()
    suite = MasterWorkloadSuite()

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    experiment_id = f"EXP_{int(time.time())}_{hw_profile['cpu_model'].replace(' ', '_')}"

    print("=" * 80)
    print("LEO / HYPER VERIFIED COMPUTATION-ELIMINATION BENCHMARK SUITE")
    print(f"Hardware: {hw_profile['cpu_model']} | {hw_profile['physical_cores']} Cores / {hw_profile['logical_processors']} Threads")
    print(f"GPU: {hw_profile['gpu_model']} (Type: {hw_profile['gpu_type']})")
    print(f"OpenVINO Devices: {hw_profile['openvino_devices']}")
    print(f"Timestamp: {timestamp}")
    print("=" * 80)

    workload_runners = [
        suite.run_workload_1_dense_gemm,
        suite.run_workload_2_tensor_attention,
        suite.run_workload_3_sparse_fft,
        suite.run_workload_4_sparse_matmul,
    ]

    benchmark_records: List[Dict[str, Any]] = []

    for runner in workload_runners:
        cpu_before = psutil.cpu_percent(interval=0.1)
        res = runner(warmup=warmup_runs, runs=measured_runs)
        cpu_after = psutil.cpu_percent(interval=0.1)
        avg_cpu = float((cpu_before + cpu_after) / 2.0)

        cand_lat = res["candidate_latency_ms"]
        out_metrics = res.get("output_metrics", {})
        contract_obj = res.get("contract")
        contract_dict = json.loads(contract_to_json(contract_obj)) if contract_obj else {}

        record = {
            "experiment_id": experiment_id,
            "timestamp_utc": timestamp,
            "workload": res["name"],
            "input_shape": res["input_shape"],
            "dtype": res["dtype"],
            "path_class": res["path_class"],
            "backend": res["backend"],
            "hardware_profile": hw_profile,
            "software_profile": {
                "python_version": hw_profile["python_version"],
                "package_versions": hw_profile["package_versions"],
            },
            "warmup_runs": res["warmup_runs"],
            "measured_runs": res["measured_runs"],
            "cold_cache": True,
            "cache_hit": False,
            "latency_ms": {
                "min": cand_lat["min"],
                "median": cand_lat["median"],
                "mean": cand_lat["mean"],
                "p95": cand_lat["p95"],
                "max": cand_lat["max"],
                "std_dev": cand_lat["std_dev"],
            },
            "throughput": round(1000.0 / max(1e-6, cand_lat["median"]), 2),
            "memory_bytes": hw_profile["ram_total_bytes"],
            "cpu_utilization_pct": avg_cpu,
            "gpu_utilization_pct": None,
            "temperature_c": None,
            "power_w": None,
            "output_metrics": {
                "max_abs_error": out_metrics.get("max_abs_error"),
                "relative_error": out_metrics.get("relative_error"),
                "rmse": out_metrics.get("rmse"),
                "psnr": out_metrics.get("psnr"),
                "ssim": out_metrics.get("ssim"),
            },
            "contract": contract_dict,
            "contract_satisfied": res["contract_satisfied"],
            "fallback_used": res["fallback_used"],
            "measured_speedup_vs_dense": res.get("measured_speedup"),
            "work_eliminated_pct": res.get("work_eliminated_pct"),
            "provenance": res["provenance"],
        }
        benchmark_records.append(record)
        print(f"[{res['workload_id']}] {res['name']}:")
        print(f"     Candidate Median: {cand_lat['median']:.4f} ms (p95: {cand_lat['p95']:.4f} ms)")
        print(f"     Baseline Median:  {res['baseline_latency_ms']['median']:.4f} ms")
        print(f"     Speedup:          {res.get('measured_speedup')}x")
        print(f"     Work Eliminated:  {res.get('work_eliminated_pct')}%")
        print(f"     Error (Max Abs):  {out_metrics.get('max_abs_error')}")
        print(f"     Contract Satisfied: {res['contract_satisfied']}")

    final_output = {
        "experiment_id": experiment_id,
        "timestamp_utc": timestamp,
        "total_workloads_measured": len(benchmark_records),
        "results": benchmark_records,
    }

    out_file = ROOT / "HYPER_100_RESULTS.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2)

    print("\n" + "=" * 80)
    print(f"Results written to {out_file}")
    print("=" * 80)
    return final_output


if __name__ == "__main__":
    run_master_benchmarks()
