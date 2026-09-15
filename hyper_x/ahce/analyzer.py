"""
hyper_x/ahce/analyzer.py
========================
Workload Analyzer Harness for AHCE (Section 5).

Measures:
- analysis latency
- analysis memory overhead
- feature extraction accuracy
- builds deterministic WorkloadSignature
"""

from __future__ import annotations
import time
import psutil
from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple, Optional
import numpy as np

from .feature_extractor import AHCEFeatureExtractor
from .workload_signature import WorkloadSignature, hash_array
from .contract import AHCEContract
from hyper.hardware import get_hardware_profile


@dataclass
class AnalysisTelemetry:
    analysis_latency_ms: float
    analysis_ram_mb: float
    features: Dict[str, Any]
    signature_digest: str


class AHCEWorkloadAnalyzer:
    """Fast workload analysis engine with explicit overhead accounting."""

    def __init__(self):
        self.extractor = AHCEFeatureExtractor()
        self._cached_hw = get_hardware_profile()

    def analyze_matrix_workload(
        self,
        workload_id: str,
        A: np.ndarray,
        B: Optional[np.ndarray] = None,
        contract: Optional[AHCEContract] = None,
        model_hash: str = "none",
        op_graph_hash: str = "matmul_2d"
    ) -> Tuple[WorkloadSignature, AnalysisTelemetry]:
        t0 = time.perf_counter_ns()
        mem_before = psutil.virtual_memory().used / (1024 * 1024)

        # Extract features from A
        features = self.extractor.extract_matrix_features(A)

        # Hash input
        input_hash = hash_array(A)
        if B is not None:
            input_hash = f"{input_hash[:16]}_{hash_array(B)[:16]}"

        contract_hash = contract.contract_id if contract else "default_exact"

        sig = WorkloadSignature(
            workload_id=workload_id,
            input_hash=input_hash,
            operation_graph_hash=op_graph_hash,
            model_hash=model_hash,
            contract_hash=contract_hash,
            features=features,
            hardware_profile={"cpu": self._cached_hw.get("cpu_model"), "gpu": self._cached_hw.get("gpu_model")},
            runtime_profile={"python": self._cached_hw.get("python_version")}
        )

        elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
        mem_after = psutil.virtual_memory().used / (1024 * 1024)
        delta_mem = max(0.0, mem_after - mem_before)

        telem = AnalysisTelemetry(
            analysis_latency_ms=round(elapsed_ms, 3),
            analysis_ram_mb=round(delta_mem, 2),
            features=features.to_dict(),
            signature_digest=sig.signature_digest
        )

        return sig, telem
