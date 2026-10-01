"""
hyper/benchmark/canonical_runner.py
===================================
Canonical Benchmark Execution Engine for LEO/HYPER.
Executes the authoritative 7-Domain Workload Corpus through UniversalRouter,
producing reproducible benchmark results, certificates, and live coverage metrics.
"""

from __future__ import annotations
import json
import time
from typing import Any, Dict, List, Optional
import numpy as np

from hyper.workloads.canonical_corpus import CanonicalWorkloadCorpus, CanonicalWorkload
from hyper.router.universal_router import UniversalRouter, RouterResult, RouterOutcome
from hyper.coverage.coverage_engine import CoverageEngine, LiveCoverageMetrics
from hyper.evidence.evidence_ledger import EvidenceLedger
from hyper.certificates.certificate_engine import CertificateStore
from hyper.hardware import get_hardware_profile


def run_canonical_benchmark(
    warmup_trials: int = 2,
    measured_trials: int = 5,
    save_results_path: Optional[str] = "canonical_benchmark_results.json",
) -> Dict[str, Any]:
    """
    Executes all canonical workloads through UniversalRouter,
    measuring exact latency distributions, verification verdicts, and coverage.
    """
    hw = get_hardware_profile()
    ledger = EvidenceLedger()
    cert_store = CertificateStore()
    router = UniversalRouter(ledger=ledger, cert_store=cert_store)
    coverage_engine = CoverageEngine(ledger=ledger)

    workloads = CanonicalWorkloadCorpus.get_all_workloads()
    workload_ids = [w.workload_id for w in workloads]

    results: Dict[str, Any] = {}
    detailed_records: List[Dict[str, Any]] = []

    print("=" * 80)
    print("HYPER UNIVERSAL EXACT SEMANTIC REPLACEMENT ENGINE — BENCHMARK HARNESS")
    print(f"Target CPU: {hw.get('cpu_model')} ({hw.get('physical_cores')}P+{hw.get('logical_processors') - hw.get('physical_cores')}E Cores, {hw.get('logical_processors')} Threads)")
    print(f"Target iGPU: {hw.get('gpu_model')} | OpenVINO Devices: {hw.get('openvino_devices')}")
    print(f"RAM Total: {hw.get('ram_total_bytes') / (1024**3):.1f} GB | OS: {hw.get('os')}")
    print(f"Canonical Workloads: {len(workloads)} across 7 domains")
    print("=" * 80)

    for w in workloads:
        print(f"--> Executing [{w.domain}] {w.workload_id}: {w.description} ...")

        # Generate inputs
        inputs = w.input_generator()
        adv_inputs = w.adversarial_generator()

        # Warmup
        for _ in range(warmup_trials):
            router.route_and_execute(
                program=w.program,
                inputs=inputs,
                contract_id=f"CONTRACT_{w.workload_id}",
                exactness_level=w.exactness_level,
            )

        # Measured repeated trials
        trial_latencies = []
        last_result: Optional[RouterResult] = None
        for _ in range(measured_trials):
            t0 = time.perf_counter()
            last_result = router.route_and_execute(
                program=w.program,
                inputs=inputs,
                contract_id=f"CONTRACT_{w.workload_id}",
                exactness_level=w.exactness_level,
                adversarial_inputs=adv_inputs,
            )
            trial_latencies.append((time.perf_counter() - t0) * 1000.0)

        assert last_result is not None
        results[w.workload_id] = last_result

        p50 = float(np.percentile(trial_latencies, 50))
        p95 = float(np.percentile(trial_latencies, 95))
        min_l = float(np.min(trial_latencies))
        max_l = float(np.max(trial_latencies))

        rec = {
            "workload_id": w.workload_id,
            "domain": w.domain,
            "description": w.description,
            "outcome": last_result.outcome,
            "strategy_used": last_result.strategy_used,
            "exactness_level": last_result.exactness_level.value,
            "verification_passed": last_result.verification_passed,
            "backend_device": last_result.backend_device,
            "speedup": round(last_result.speedup, 2),
            "baseline_latency_ms": round(last_result.baseline_latency_ms, 4),
            "measured_candidate_latency_ms": round(last_result.actual_latency_ms, 4),
            "latencies_ms": {
                "min": round(min_l, 4),
                "p50": round(p50, 4),
                "p95": round(p95, 4),
                "max": round(max_l, 4),
            },
            "evidence_id": last_result.evidence_id,
            "certificate_id": last_result.certificate_id,
            "explanation": last_result.explanation,
        }
        detailed_records.append(rec)
        print(f"    Outcome: {last_result.outcome} | Strategy: {last_result.strategy_used} | Speedup: {last_result.speedup:.2f}x | Backend: {last_result.backend_device}")

    # Compute Live Coverage Metrics
    coverage_metrics = coverage_engine.compute_live_coverage(
        registered_workloads=workload_ids,
        execution_results=results,
    )

    summary = {
        "timestamp": time.time(),
        "hardware_profile": hw,
        "coverage_metrics": coverage_metrics.to_dict(),
        "workload_records": detailed_records,
    }

    if save_results_path:
        try:
            with open(save_results_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            print(f"\n[OK] Results saved to {save_results_path}")
        except Exception as e:
            print(f"[WARN] Could not save results file: {e}")

    print("\n" + "=" * 80)
    print("HYPER LIVE COVERAGE SUMMARY")
    print(f"Domain: {coverage_metrics.coverage_domain}")
    print(f"Represented Workloads:         {coverage_metrics.represented_workloads}")
    print(f"Exactly Executable Workloads:  {coverage_metrics.exactly_executable_workloads}")
    print(f"Proven Escape Workloads:       {coverage_metrics.proven_escape_workloads}")
    print(f"Exact Fallback Workloads:      {coverage_metrics.fallback_workloads}")
    print(f"Unsupported Workloads:         {coverage_metrics.unsupported_workloads}")
    print(f"Rejected Workloads:            {coverage_metrics.rejected_workloads}")
    print(f"Exact Semantic Coverage:       {coverage_metrics.exact_semantic_coverage_pct:.2f}%")
    print(f"Exact Escape Coverage:         {coverage_metrics.exact_escape_coverage_pct:.2f}%")
    print(f"Fallback Rate:                 {coverage_metrics.fallback_rate_pct:.2f}%")
    print(f"100% Gate Eligible:            {coverage_metrics.gate_100_eligible}")
    print("=" * 80)

    return summary
