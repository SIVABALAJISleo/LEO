"""
hyper_x/cpce/telemetry.py
=========================
Benchmark Truth and Telemetry Instrumentation for CPCE.
Records empirical measurements with explicit provenance tags (MEASURED, DERIVED, CONFIGURED, SIMULATED, UNAVAILABLE).
"""

from __future__ import annotations

import dataclasses
import os
import platform
import time
import uuid
from typing import Any, Dict, List, Optional
import psutil

from hyper_x.cpce.result_schema import ProvenanceLabel


@dataclasses.dataclass
class TelemetryRecord:
    run_id: str
    timestamp: float
    workload_id: str
    backend_requested: str
    backend_used: str
    device_identity: str
    cpu_model: str
    python_version: str
    os_version: str
    setup_latency_ms: float
    execution_latency_ms: float
    verification_latency_ms: float
    total_latency_ms: float
    peak_memory_mb: float
    power_watts: Optional[float]  # None / UNAVAILABLE if no physical sensor
    energy_joules: Optional[float] # None / UNAVAILABLE if power unmeasured
    correctness_status: str
    optimizations_applied: List[str]
    provenance: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class CPCETelemetry:
    """Collects honest telemetry without simulating unmeasured physics."""

    @staticmethod
    def capture_record(
        workload_id: str,
        backend_requested: str,
        backend_used: str,
        device_identity: str,
        setup_ms: float,
        exec_ms: float,
        verify_ms: float,
        total_ms: float,
        peak_mem_mb: float,
        correctness_status: str,
        optimizations: List[str],
    ) -> TelemetryRecord:
        proc = platform.processor() or "Host CPU"
        run_id = f"RUN_{uuid.uuid4().hex[:12].upper()}"

        # Energy is marked UNAVAILABLE unless a genuine RAPL/battery sensor is queried
        return TelemetryRecord(
            run_id=run_id,
            timestamp=time.time(),
            workload_id=workload_id,
            backend_requested=backend_requested,
            backend_used=backend_used,
            device_identity=device_identity,
            cpu_model=proc,
            python_version=platform.python_version(),
            os_version=f"{platform.system()} {platform.release()}",
            setup_latency_ms=round(setup_ms, 3),
            execution_latency_ms=round(exec_ms, 3),
            verification_latency_ms=round(verify_ms, 3),
            total_latency_ms=round(total_ms, 3),
            peak_memory_mb=round(peak_mem_mb, 2),
            power_watts=None,  # Not fabricated
            energy_joules=None, # Not derived from fixed power assumptions
            correctness_status=correctness_status,
            optimizations_applied=optimizations,
            provenance={
                "latency": ProvenanceLabel.MEASURED.value,
                "memory": ProvenanceLabel.MEASURED.value,
                "power": ProvenanceLabel.UNAVAILABLE.value,
                "energy": ProvenanceLabel.UNAVAILABLE.value,
            },
        )
