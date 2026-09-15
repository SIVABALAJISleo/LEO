"""
hyper_x/ahce/workload_signature.py
==================================
Deterministic Workload Signature for AHCE (Section 6).
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Tuple, Optional
import numpy as np


@dataclass(frozen=True)
class StructuralFeatures:
    dimensions: Tuple[int, ...]
    dtype: str
    sparsity: float = 0.0
    density: float = 1.0
    estimated_effective_rank: Optional[int] = None
    condition_estimate: Optional[float] = None
    entropy: float = 1.0
    temporal_similarity: float = 0.0
    spatial_similarity: float = 0.0
    arithmetic_intensity: float = 1.0  # FLOPs / Byte
    repeated_inputs_detected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkloadSignature:
    workload_id: str
    input_hash: str
    operation_graph_hash: str
    model_hash: str
    contract_hash: str
    features: StructuralFeatures
    hardware_profile: Dict[str, Any]
    runtime_profile: Dict[str, Any]
    signature_digest: str = ""

    def __post_init__(self):
        if not self.signature_digest:
            self.signature_digest = self.compute_digest()

    def compute_digest(self) -> str:
        hasher = hashlib.sha256()
        hasher.update(self.workload_id.encode("utf-8"))
        hasher.update(self.input_hash.encode("utf-8"))
        hasher.update(self.operation_graph_hash.encode("utf-8"))
        hasher.update(self.model_hash.encode("utf-8"))
        hasher.update(self.contract_hash.encode("utf-8"))
        feat_str = json.dumps(self.features.to_dict(), sort_keys=True)
        hasher.update(feat_str.encode("utf-8"))
        return hasher.hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["features"] = self.features.to_dict()
        return d


def hash_array(arr: np.ndarray) -> str:
    """Compute fast cryptographic hash of an array."""
    hasher = hashlib.sha256()
    hasher.update(str(arr.shape).encode("utf-8"))
    hasher.update(str(arr.dtype).encode("utf-8"))
    # Hash bytes (or sample if massive)
    if arr.size > 2_000_000:
        # Uniform stride sample
        stride = arr.size // 200_000
        sample = np.ascontiguousarray(arr.flat[::stride])
        hasher.update(sample.tobytes())
    else:
        hasher.update(np.ascontiguousarray(arr).tobytes())
    return hasher.hexdigest()
