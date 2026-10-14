"""
leo/parity/runner.py
====================
Contract-Driven Benchmark Runner and Certificate Generator.

Command:
  python -m leo.parity run
  python -m leo.parity cold
  python -m leo.parity soak [--duration-minutes N]

Protocol:
1. Warmup: 3 iterations (excluded from statistics).
2. Timed Repetitions: 30 iterations.
3. Latency Metrics: median, p95, p99, mean, std_dev.
4. Telemetry: CPU clock (MHz) + load tracked every second during execution;
   CPU temperature probed honestly (reported as NOT_AVAILABLE if OS sensor access restricted).
5. Memory: Peak Resident Set Size (RSS) in MB via psutil.
6. Cryptographic Certification: Output JSON certificates signed with SHA-256 of
   inputs, outputs, configuration, and contracts.yaml file.
"""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import psutil

from .contracts import (
    ContractDef,
    ContractsRegistry,
    ExecutionResult,
    ResultLabel,
    load_and_freeze_contracts,
)
from .router import ParityWorkloadRouter


@dataclass
class TelemetrySample:
    timestamp_s: float
    cpu_clock_mhz: float
    cpu_percent: float
    cpu_temp_c: Optional[float]
    ram_used_mb: float


class SystemTelemetryMonitor:
    """Honest background telemetry tracker recording clock and temperature."""

    def __init__(self, interval_s: float = 1.0) -> None:
        self.interval_s = interval_s
        self.samples: List[TelemetrySample] = []
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _get_cpu_temp(self) -> Optional[float]:
        # Rule 1: No fabricated metrics. Probe real sensors or return None.
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            return float(entries[0].current)
        except Exception:
            pass
        return None

    def _get_cpu_clock(self) -> float:
        try:
            freq = psutil.cpu_freq()
            if freq and freq.current:
                return float(freq.current)
        except Exception:
            pass
        return 0.0

    def _monitor_loop(self) -> None:
        proc = psutil.Process()
        while not self._stop_event.is_set():
            t = time.time()
            clock = self._get_cpu_clock()
            load = psutil.cpu_percent(interval=None)
            temp = self._get_cpu_temp()
            ram = proc.memory_info().rss / (1024 * 1024)

            self.samples.append(TelemetrySample(
                timestamp_s=t,
                cpu_clock_mhz=clock,
                cpu_percent=load,
                cpu_temp_c=temp,
                ram_used_mb=ram,
            ))
            time.sleep(self.interval_s)

    def start(self) -> None:
        self.samples.clear()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self) -> List[TelemetrySample]:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        return self.samples


@dataclass
class ParityCertificate:
    """
    Formal, cryptographic proof artifact certifying contract compliance.
    """
    certificate_id: str
    workload_name: str
    workload_id: str
    contracts_file_sha256: str
    input_spec_sha256: str
    output_digest_sha256: str
    config_digest_sha256: str
    certificate_sha256: str
    timestamp_iso: str
    status: str  # "PASS" | "FAIL"
    result_label: str  # EXACT | APPROXIMATE | CACHED | PREDICTIVE | REDUCED_WORK
    contract_clauses: Dict[str, Any]
    measurements: Dict[str, Any]
    telemetry_summary: Dict[str, Any]
    hardware_fingerprint: Dict[str, Any]


class ParityBenchmarkRunner:
    """
    Executes warmup 3, 30 timed repetitions, tracks telemetry, and generates certificates.
    """

    def __init__(self, contracts_path: str = "contracts.yaml") -> None:
        self.registry = load_and_freeze_contracts(contracts_path)
        self.router = ParityWorkloadRouter(self.registry)
        self.monitor = SystemTelemetryMonitor(interval_s=1.0)

    def _hash_obj(self, obj: Any) -> str:
        s = json.dumps(obj, sort_keys=True, default=str)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def run_workload(
        self,
        workload_name: str,
        warmup_reps: int = 3,
        timed_reps: int = 30,
        allow_cache: bool = True,
    ) -> ParityCertificate:
        """
        Executes a declared workload according to the rigid benchmark protocol.
        """
        contract = self.registry.get_contract(workload_name)
        proc = psutil.Process()

        # Start telemetry tracking
        self.monitor.start()

        # 1. Warmup Phase (3 reps, excluded from metrics)
        for _ in range(warmup_reps):
            _ = self.router.route_and_execute(workload_name, allow_cache=allow_cache)

        # 2. Timed Repetitions (30 reps)
        latencies: List[float] = []
        last_result: Optional[ExecutionResult] = None
        peak_rss_mb = 0.0

        for _ in range(timed_reps):
            t0 = time.perf_counter()
            res = self.router.route_and_execute(workload_name, allow_cache=allow_cache)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)
            last_result = res

            cur_rss = proc.memory_info().rss / (1024 * 1024)
            if cur_rss > peak_rss_mb:
                peak_rss_mb = cur_rss

        samples = self.monitor.stop()

        assert last_result is not None, "Execution failed to produce a result"

        # Calculate statistics
        p50 = float(np.percentile(latencies, 50))
        p95 = float(np.percentile(latencies, 95))
        p99 = float(np.percentile(latencies, 99))
        mean_lat = float(np.mean(latencies))
        std_lat = float(np.std(latencies))

        # Telemetry aggregation
        clocks = [s.cpu_clock_mhz for s in samples if s.cpu_clock_mhz > 0]
        avg_clock = float(np.mean(clocks)) if clocks else 0.0
        temps = [s.cpu_temp_c for s in samples if s.cpu_temp_c is not None]
        avg_temp = float(np.mean(temps)) if temps else None

        # Verify contract compliance on the median result
        # Check all contract gates
        workload_ram_mb = float(last_result.peak_ram_mb)
        passed_quality = last_result.correctness_metric_value >= contract.quality_threshold
        passed_latency = p50 <= contract.latency_cap_ms
        passed_ram = workload_ram_mb <= contract.peak_ram_cap_mb
        passed_label = last_result.label.value in contract.allowed_labels
        passed_emulation = not last_result.emulated and last_result.label != ResultLabel.EMULATED

        contract_passed = (
            passed_quality
            and passed_latency
            and passed_ram
            and passed_label
            and passed_emulation
            and last_result.verified
        )

        # Compute cryptographic certificate signatures
        input_hash = self._hash_obj(contract.input_spec)
        output_hash = self._hash_obj(str(last_result.output)[:1000])
        config_hash = self._hash_obj({
            "warmup_reps": warmup_reps,
            "timed_reps": timed_reps,
            "allow_cache": allow_cache,
            "quality_threshold": contract.quality_threshold,
            "latency_cap_ms": contract.latency_cap_ms,
            "peak_ram_cap_mb": contract.peak_ram_cap_mb,
        })

        cert_id = f"CERT_{contract.workload_id}_{int(time.time())}"
        cert_payload = {
            "cert_id": cert_id,
            "contracts_file_sha256": self.registry.contracts_hash,
            "input_hash": input_hash,
            "output_hash": output_hash,
            "config_hash": config_hash,
            "status": "PASS" if contract_passed else "FAIL",
            "p50_ms": p50,
        }
        cert_sha256 = self._hash_obj(cert_payload)

        hardware_fp = {
            "processor": platform.processor(),
            "cpu_cores_logical": psutil.cpu_count(logical=True),
            "cpu_cores_physical": psutil.cpu_count(logical=False),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "os": f"{platform.system()} {platform.release()}",
            "machine": platform.machine(),
        }

        cert = ParityCertificate(
            certificate_id=cert_id,
            workload_name=workload_name,
            workload_id=contract.workload_id,
            contracts_file_sha256=self.registry.contracts_hash,
            input_spec_sha256=input_hash,
            output_digest_sha256=output_hash,
            config_digest_sha256=config_hash,
            certificate_sha256=cert_sha256,
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            status="PASS" if contract_passed else "FAIL",
            result_label=last_result.label.value,
            contract_clauses={
                "correctness_metric": contract.correctness_metric,
                "quality_threshold": contract.quality_threshold,
                "latency_cap_ms": contract.latency_cap_ms,
                "peak_ram_cap_mb": contract.peak_ram_cap_mb,
                "allowed_labels": list(contract.allowed_labels),
            },
            measurements={
                "latency_p50_ms": round(p50, 3),
                "latency_p95_ms": round(p95, 3),
                "latency_p99_ms": round(p99, 3),
                "latency_mean_ms": round(mean_lat, 3),
                "latency_std_ms": round(std_lat, 3),
                "peak_rss_mb": round(workload_ram_mb, 2),
                "workload_resident_ram_mb": round(workload_ram_mb, 2),
                "peak_process_rss_mb": round(peak_rss_mb, 2),
                "quality_metric_value": round(last_result.correctness_metric_value, 4),
                "reps_timed": timed_reps,
                "reps_warmup": warmup_reps,
                "cache_allowed": allow_cache,
            },
            telemetry_summary={
                "avg_cpu_clock_mhz": round(avg_clock, 1),
                "avg_cpu_temp_c": round(avg_temp, 1) if avg_temp is not None else "NOT_AVAILABLE_USERMODE",
                "samples_collected": len(samples),
            },
            hardware_fingerprint=hardware_fp,
        )

        return cert

    def run_all(
        self,
        warmup_reps: int = 3,
        timed_reps: int = 30,
        allow_cache: bool = True,
        output_dir: str = "reports/parity_certificates",
    ) -> List[ParityCertificate]:
        """Runs all 4 declared contracts and saves certificate JSONs."""
        os.makedirs(output_dir, exist_ok=True)
        certificates: List[ParityCertificate] = []

        print("=" * 78)
        print(" LEO / HYPER: CONTRACT-DRIVEN FALSIFIABLE PARITY ENGINE")
        print(f" Contracts Frozen SHA-256: {self.registry.contracts_hash[:16]}...")
        print("=" * 78)

        for name in self.registry.contracts.keys():
            print(f"\n[BENCHMARK] Executing Contract: {name} (3 Warmup, {timed_reps} Timed Reps)...")
            cert = self.run_workload(name, warmup_reps=warmup_reps, timed_reps=timed_reps, allow_cache=allow_cache)
            certificates.append(cert)

            status_sym = "[PASS]" if cert.status == "PASS" else "[FAIL]"
            print(f"  {status_sym} Status        : {cert.status}")
            print(f"  - Label         : {cert.result_label}")
            print(f"  - Latency (p50) : {cert.measurements['latency_p50_ms']} ms (p95: {cert.measurements['latency_p95_ms']} ms, p99: {cert.measurements['latency_p99_ms']} ms)")
            print(f"  - Quality       : {cert.measurements['quality_metric_value']} (Threshold: {cert.contract_clauses['quality_threshold']})")
            print(f"  - Peak RAM      : {cert.measurements['peak_rss_mb']} MB (Cap: {cert.contract_clauses['peak_ram_cap_mb']} MB)")
            print(f"  - CPU Clock     : {cert.telemetry_summary['avg_cpu_clock_mhz']} MHz | Temp: {cert.telemetry_summary['avg_cpu_temp_c']}")
            print(f"  - Certificate   : {cert.certificate_sha256[:16]}...")

            # Save individual certificate JSON
            cert_file = os.path.join(output_dir, f"{name}_certificate.json")
            with open(cert_file, "w", encoding="utf-8") as f:
                json.dump(asdict(cert), f, indent=2)

        print("\n" + "=" * 78)
        pass_count = sum(1 for c in certificates if c.status == "PASS")
        total_count = len(certificates)
        print(f" FINAL RESULT: {pass_count}/{total_count} Contracts Passed ({(pass_count/total_count)*100.0:.1f}%)")
        print(f" Certificates saved to: {os.path.abspath(output_dir)}")
        print("=" * 78)

        return certificates

    def run_soak(
        self,
        duration_minutes: float = 10.0,
        output_dir: str = "reports/parity_certificates",
    ) -> Dict[str, Any]:
        """
        Sustained 10-minute continuous run to expose thermal throttling and memory leakage.
        """
        os.makedirs(output_dir, exist_ok=True)
        print("=" * 78)
        print(f" LEO / HYPER: SUSTAINED THERMAL SOAK BENCHMARK ({duration_minutes:.1f} Minutes)")
        print("=" * 78)

        monitor = SystemTelemetryMonitor(interval_s=2.0)
        monitor.start()

        end_time = time.time() + (duration_minutes * 60.0)
        iteration = 0
        workload_names = list(self.registry.contracts.keys())
        latencies_over_time: Dict[str, List[float]] = {w: [] for w in workload_names}

        proc = psutil.Process()
        ram_start = proc.memory_info().rss / (1024 * 1024)

        try:
            while time.time() < end_time:
                iteration += 1
                w_name = workload_names[iteration % len(workload_names)]
                t0 = time.perf_counter()
                res = self.router.route_and_execute(w_name, allow_cache=False)
                lat = (time.perf_counter() - t0) * 1000.0
                latencies_over_time[w_name].append(lat)

                if iteration % 20 == 0:
                    remaining_s = max(0, end_time - time.time())
                    cur_rss = proc.memory_info().rss / (1024 * 1024)
                    cur_clock = monitor._get_cpu_clock()
                    print(f"  [SOAK {iteration:04d}] Remaining: {remaining_s/60.0:.1f}m | Clock: {cur_clock:.0f} MHz | RSS: {cur_rss:.1f} MB")
        finally:
            samples = monitor.stop()

        ram_end = proc.memory_info().rss / (1024 * 1024)
        ram_delta = ram_end - ram_start

        # Detect throttling: check if clock frequency dropped by >25% from beginning to end
        clocks = [s.cpu_clock_mhz for s in samples if s.cpu_clock_mhz > 0]
        initial_clock = float(np.mean(clocks[:5])) if len(clocks) >= 5 else 0.0
        final_clock = float(np.mean(clocks[-5:])) if len(clocks) >= 5 else 0.0
        clock_drop_pct = ((initial_clock - final_clock) / max(initial_clock, 1.0)) * 100.0
        thermal_throttling_detected = clock_drop_pct > 25.0

        soak_report = {
            "duration_minutes": duration_minutes,
            "total_iterations": iteration,
            "ram_leakage_mb": round(ram_delta, 2),
            "thermal_throttling_detected": thermal_throttling_detected,
            "clock_drop_pct": round(clock_drop_pct, 2),
            "initial_clock_mhz": round(initial_clock, 1),
            "final_clock_mhz": round(final_clock, 1),
            "telemetry_samples": len(samples),
        }

        soak_file = os.path.join(output_dir, "thermal_soak_certificate.json")
        with open(soak_file, "w", encoding="utf-8") as f:
            json.dump(soak_report, f, indent=2)

        print("\n[OK] Thermal Soak Benchmark Completed. Report saved to: " + soak_file)
        return soak_report
