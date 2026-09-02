"""
hyper_v2/compiler/contract_compiler.py
Formal immutable contract specification, parser, and validator for HYPER 2.0.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import hashlib
import json


class ExecutionTrack(str, Enum):
    TRACK_A_EXACT = "TRACK_A_EXACT"
    TRACK_B_CONTRACT = "TRACK_B_CONTRACT"


class PrecisionTarget(str, Enum):
    FP64 = "FP64"
    FP32 = "FP32"
    FP16 = "FP16"
    INT8 = "INT8"
    TERNARY = "TERNARY"  # {-1, 0, +1}
    BINARY = "BINARY"   # {0, 1}
    ADAPTIVE = "ADAPTIVE"


@dataclass(frozen=True)
class ExecutionContract:
    workload_id: str
    version: str = "2.0.0"
    track: ExecutionTrack = ExecutionTrack.TRACK_B_CONTRACT
    exactness_required: bool = False
    numerical_tolerance: float = 1e-3  # Relative error epsilon: ||Y - Y*|| / ||Y*|| <= eps
    perceptual_threshold: float = 0.95  # SSIM / PSNR >= threshold
    latency_target_ms: float = 33.3  # Max allowable latency (e.g. 30 FPS target)
    throughput_target_ops: float = 0.0
    memory_limit_mb: float = 16384.0  # Max 16GB unified RAM
    energy_limit_joules: Optional[float] = None
    allowed_transformations: Set[str] = field(default_factory=lambda: {
        "reuse", "sparsity", "low_rank", "ternary_quantization",
        "temporal_accumulation", "spatial_subsampling", "denoising",
        " Barnes_Hut_expansion", "sobol_quasi_mc", "intel_quicksync_asic",
        "cpu_igpu_split", "kernel_fusion", "speculative_decoding"
    })
    forbidden_transformations: Set[str] = field(default_factory=set)
    fallback_allowed: bool = True
    verification_required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Deterministic fingerprint of immutable contract."""
        data = {
            "workload_id": self.workload_id,
            "track": self.track.value,
            "exactness": self.exactness_required,
            "numerical_tolerance": self.numerical_tolerance,
            "perceptual_threshold": self.perceptual_threshold,
            "latency_target_ms": self.latency_target_ms,
            "allowed": sorted(list(self.allowed_transformations)),
            "forbidden": sorted(list(self.forbidden_transformations))
        }
        raw = json.dumps(data, sort_keys=True)
        return hashlib.sha256(raw.encode(), usedforsecurity=False).hexdigest()[:16]

    def is_transformation_permitted(self, transform_name: str) -> bool:
        if self.exactness_required or self.track == ExecutionTrack.TRACK_A_EXACT:
            # Exact track only permits mathematically identical reformulations
            return transform_name in {"exact_algebraic", "blocking", "simd_vectorization", "cpu_igpu_split", "fused_simd"}
        if transform_name in self.forbidden_transformations:
            return False
        return transform_name in self.allowed_transformations


class ContractCompiler:
    """Parses, validates, and compiles input contract specifications."""

    @staticmethod
    def compile_contract(spec: Dict[str, Any]) -> ExecutionContract:
        track_str = spec.get("track", "TRACK_B_CONTRACT")
        track = ExecutionTrack.TRACK_A_EXACT if track_str == "TRACK_A_EXACT" else ExecutionTrack.TRACK_B_CONTRACT
        exactness = spec.get("exactness_required", track == ExecutionTrack.TRACK_A_EXACT)

        allowed = set(spec.get("allowed_transformations", []))
        if not allowed and not exactness:
            allowed = {
                "reuse", "sparsity", "low_rank", "ternary_quantization",
                "temporal_accumulation", "spatial_subsampling", "denoising",
                "Barnes_Hut_expansion", "sobol_quasi_mc", "intel_quicksync_asic",
                "cpu_igpu_split", "kernel_fusion", "speculative_decoding"
            }
        forbidden = set(spec.get("forbidden_transformations", []))

        return ExecutionContract(
            workload_id=spec.get("workload_id", "generic-workload"),
            version=spec.get("version", "2.0.0"),
            track=track,
            exactness_required=exactness,
            numerical_tolerance=float(spec.get("numerical_tolerance", 0.0 if exactness else 1e-3)),
            perceptual_threshold=float(spec.get("perceptual_threshold", 1.0 if exactness else 0.95)),
            latency_target_ms=float(spec.get("latency_target_ms", 33.3)),
            throughput_target_ops=float(spec.get("throughput_target_ops", 0.0)),
            memory_limit_mb=float(spec.get("memory_limit_mb", 16384.0)),
            allowed_transformations=allowed,
            forbidden_transformations=forbidden,
            fallback_allowed=spec.get("fallback_allowed", True),
            verification_required=spec.get("verification_required", True),
            metadata=spec.get("metadata", {})
        )
