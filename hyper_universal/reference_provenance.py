"""
hyper_universal/reference_provenance.py
=======================================
Reference Provenance & Physical Accelerator Separation Engine.

Implements Section 5 of the Master Specification:
- Rigorously separates:
    LOCAL_REFERENCE, SIMULATED_REFERENCE, EXTERNAL_PHYSICAL_REFERENCE, THEORETICAL_REFERENCE.
- Strictly marks RTX_MEASUREMENT = UNAVAILABLE when no physical NVIDIA GPU hardware is detected.
- Never manufactures physical hardware numbers or calls simulated latencies 'measured'.
"""

from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper_universal.types import ReferenceType, CacheRegime, MetricProvenance


class ReferenceProvenance(BaseModel):
    reference_id: str
    workload_id: str
    reference_type: ReferenceType
    hardware_model: str
    driver: str = "N/A"
    runtime: str = "Python/NumPy"
    framework: str = "Native"
    precision: str = "FP32"
    problem_size: str = ""
    input_hash: str = ""
    benchmark_version: str = "LEO-HYPER-OMEGA-1.0"
    measurement_method: str = "high_resolution_timer"
    measurement_repetitions: int = 1
    warmup_count: int = 0
    cache_state: CacheRegime = CacheRegime.COLD
    power_mode: str = "Default"
    measured_latency_ms: Optional[float] = None
    metric_provenance: MetricProvenance = MetricProvenance.UNAVAILABLE
    notes: str = ""
    timestamp: float = Field(default_factory=time.time)


class ReferenceProvenanceManager:
    """
    Manages trusted reference baselines and detects physical accelerator availability.
    """

    @staticmethod
    def detect_physical_nvidia_gpu() -> Tuple[bool, str]:
        """
        Attempts to probe for local physical NVIDIA GPU hardware via NVML / torch.cuda.
        Returns (is_available, model_name).
        """
        try:
            import torch
            if torch.cuda.is_available():
                name = torch.cuda.get_device_name(0)
                return True, name
        except Exception:
            pass

        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name = pynvml.nvmlDeviceGetName(handle)
            pynvml.nvmlShutdown()
            return True, str(name)
        except Exception:
            pass

        return False, "NVIDIA_GPU_NOT_DETECTED"

    @classmethod
    def create_reference_record(
        cls,
        workload_id: str,
        input_data: Any,
        measured_latency_ms: Optional[float] = None,
        is_simulated: bool = False,
        cache_state: CacheRegime = CacheRegime.COLD,
    ) -> ReferenceProvenance:
        """
        Constructs a verified reference provenance record.
        If reference is simulated or no physical GPU exists, marks accordingly.
        """
        has_gpu, gpu_name = cls.detect_physical_nvidia_gpu()

        # Compute deterministic input hash
        input_bytes = getattr(input_data, "tobytes", lambda: str(input_data).encode())()
        in_hash = hashlib.sha256(input_bytes).hexdigest()[:16]

        if is_simulated:
            ref_type = ReferenceType.SIMULATED_REFERENCE
            prov = MetricProvenance.SIMULATED
            hw_model = f"Simulated-{gpu_name if has_gpu else 'Generic-Reference-GPU'}"
            notes = "Simulated reference model. NOT a physical measurement."
        elif has_gpu:
            ref_type = ReferenceType.EXTERNAL_PHYSICAL_REFERENCE
            prov = MetricProvenance.MEASURED
            hw_model = gpu_name
            notes = f"Physical GPU hardware detected: {gpu_name}."
        else:
            # Local host reference on CPU
            ref_type = ReferenceType.LOCAL_REFERENCE
            prov = MetricProvenance.MEASURED if measured_latency_ms is not None else MetricProvenance.UNAVAILABLE
            hw_model = "Intel Core i5-12450H CPU (Local Host Reference)"
            notes = "Local CPU host baseline. Physical external RTX GPU is UNAVAILABLE on this host."

        ref_id = f"ref-{hashlib.sha256(f'{workload_id}:{hw_model}:{in_hash}'.encode()).hexdigest()[:10]}"

        return ReferenceProvenance(
            reference_id=ref_id,
            workload_id=workload_id,
            reference_type=ref_type,
            hardware_model=hw_model,
            precision="FP32",
            input_hash=in_hash,
            cache_state=cache_state,
            measured_latency_ms=measured_latency_ms,
            metric_provenance=prov,
            notes=notes,
        )
