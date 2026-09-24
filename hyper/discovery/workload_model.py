"""
hyper/discovery/workload_model.py
=================================
Canonical Workload Schema & Contract Extractor Engine.

Implements Sections 5 & 6 of the Master Architecture:
- CanonicalWorkload: Complete, immutable representation of any computational workload
  (identity, input/output specs, contract, mathematical representation, dependency DAG,
   data movement, precision, determinism, tolerance budget, resource constraints).
- ContractExtractor: Extracts, verifies, and classifies workload contracts into:
  EXACT, NUMERICALLY_TOLERANT, SEMANTIC, PERCEPTUAL, APPROXIMATE, or CUSTOM.
  Strict discipline: Never silently relaxes an exact contract.
"""

from __future__ import annotations
import inspect
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np
from pydantic import BaseModel, Field


class ContractExactnessType(Enum):
    EXACT = "EXACT"
    NUMERICALLY_TOLERANT = "NUMERICALLY_TOLERANT"
    SEMANTIC = "SEMANTIC"
    PERCEPTUAL = "PERCEPTUAL"
    APPROXIMATE = "APPROXIMATE"
    CUSTOM = "CUSTOM"


class WorkloadPrecision(Enum):
    FP64 = "FP64"
    FP32 = "FP32"
    FP16 = "FP16"
    BF16 = "BF16"
    INT32 = "INT32"
    INT8 = "INT8"
    TERNARY = "TERNARY"
    EXACT_INTEGER = "EXACT_INTEGER"
    SYMBOLIC = "SYMBOLIC"


class WorkloadResourceConstraints(BaseModel):
    max_latency_ms: float = 5000.0
    min_throughput_ops: float = 1.0
    max_memory_mb: float = 4096.0
    max_bandwidth_gbps: float = 18.57  # Target dual-channel RAM bandwidth limit
    max_power_watts: float = 45.0      # Target Intel Core i5-12450H TDP envelope
    target_device: str = "CPU_IGPU_HYBRID"


class ExtractedContract(BaseModel):
    contract_id: str
    workload_id: str
    exactness_type: ContractExactnessType = ContractExactnessType.NUMERICALLY_TOLERANT
    precision: WorkloadPrecision = WorkloadPrecision.FP32
    absolute_tolerance: float = 1e-5
    relative_tolerance: float = 1e-4
    is_deterministic: bool = True
    preserves_ordering: bool = True
    allows_approximation: bool = False
    resource_constraints: WorkloadResourceConstraints = Field(default_factory=WorkloadResourceConstraints)
    relaxation_history: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def relax_to_tolerance(self, new_atol: float, new_rtol: float, rationale: str) -> None:
        """Explicitly records a contract relaxation without silent modification."""
        if self.exactness_type == ContractExactnessType.EXACT:
            raise ValueError("Forbidden: An EXACT contract cannot be silently relaxed.")
        old_atol = self.absolute_tolerance
        self.absolute_tolerance = new_atol
        self.relative_tolerance = new_rtol
        self.relaxation_history.append(
            f"Relaxed atol from {old_atol} to {new_atol} at {time.time()}: {rationale}"
        )


class CanonicalWorkload(BaseModel):
    """
    Canonical, unified representation of a computational workload.
    """
    identity: str
    name: str
    domain: str
    source_provenance: str = "USER_DEFINED"
    input_shape: List[int] = Field(default_factory=list)
    output_shape: List[int] = Field(default_factory=list)
    input_dtype: str = "float32"
    output_dtype: str = "float32"
    mathematical_representation: str = "f(x)"
    dependency_nodes: List[str] = Field(default_factory=list)
    data_movement_bytes: int = 0
    contract: ExtractedContract
    reference_gpu_baseline_ms: Optional[float] = None
    created_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def compute_workload_hash(self) -> str:
        """Computes a unique SHA-256 fingerprint for this workload."""
        content = f"{self.identity}:{self.name}:{self.domain}:{self.mathematical_representation}:{self.contract.exactness_type.value}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


class ContractExtractor:
    """
    Extracts and formalizes contracts from arbitrary functions or workload specifications.
    """

    @staticmethod
    def extract_from_callable(
        fn: Callable[[Any], Any],
        sample_input: Any,
        name: str = "Workload",
        domain: str = "GENERAL",
        force_exact: bool = False,
        target_precision: WorkloadPrecision = WorkloadPrecision.FP32,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CanonicalWorkload:
        meta = metadata or {}
        w_id = f"wl-{hashlib.sha256(name.encode()).hexdigest()[:8]}"

        # Infer input shape and type
        in_shape = []
        in_dtype = "unknown"
        if isinstance(sample_input, np.ndarray):
            in_shape = list(sample_input.shape)
            in_dtype = str(sample_input.dtype)
        elif isinstance(sample_input, list):
            in_shape = [len(sample_input)]
            in_dtype = "list"
        elif isinstance(sample_input, (int, float)):
            in_shape = [1]
            in_dtype = type(sample_input).__name__

        # Run sample trial to extract output shape
        out_shape = []
        out_dtype = "unknown"
        try:
            sample_out = fn(sample_input)
            if isinstance(sample_out, np.ndarray):
                out_shape = list(sample_out.shape)
                out_dtype = str(sample_out.dtype)
            elif isinstance(sample_out, list):
                out_shape = [len(sample_out)]
                out_dtype = "list"
            elif isinstance(sample_out, (int, float)):
                out_shape = [1]
                out_dtype = type(sample_out).__name__
        except Exception:
            pass

        # Determine exactness
        name_lower = name.lower()
        if force_exact or any(k in name_lower for k in ["sort", "hash", "search", "raster", "prefix", "exact"]):
            exactness = ContractExactnessType.EXACT
            atol = 0.0
            rtol = 0.0
            allows_approx = False
        elif any(k in name_lower for k in ["image", "video", "perceptual"]):
            exactness = ContractExactnessType.PERCEPTUAL
            atol = 1e-2
            rtol = 1e-2
            allows_approx = True
        elif any(k in name_lower for k in ["semantic", "embedding", "llm"]):
            exactness = ContractExactnessType.SEMANTIC
            atol = 1e-1
            rtol = 1e-1
            allows_approx = True
        else:
            exactness = ContractExactnessType.NUMERICALLY_TOLERANT
            atol = 1e-5
            rtol = 1e-4
            allows_approx = False

        contract = ExtractedContract(
            contract_id=f"cntr-{w_id}",
            workload_id=w_id,
            exactness_type=exactness,
            precision=target_precision,
            absolute_tolerance=atol,
            relative_tolerance=rtol,
            allows_approximation=allows_approx,
            metadata=meta,
        )

        workload = CanonicalWorkload(
            identity=w_id,
            name=name,
            domain=domain,
            input_shape=in_shape,
            output_shape=out_shape,
            input_dtype=in_dtype,
            output_dtype=out_dtype,
            mathematical_representation=f"{name}(x)",
            dependency_nodes=[f"input_{in_dtype}", "compute_core", f"output_{out_dtype}"],
            data_movement_bytes=int(np.prod(in_shape or [1]) * 4 + np.prod(out_shape or [1]) * 4),
            contract=contract,
            metadata=meta,
        )

        return workload
