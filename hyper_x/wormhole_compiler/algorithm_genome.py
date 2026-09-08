"""
hyper_x/wormhole_compiler/algorithm_genome.py
=============================================================================
HYPER-X Algorithm Genome (Phase 9)
=============================================================================
Defines the canonical, serializable, hashable, and evolvable genetic
representation of discovered algorithm compositions.

Fields:
  - representation: RepresentationType / str (e.g. LOW_RANK, SPARSE, DENSE)
  - decomposition: str (e.g. SVD_TRUNCATED, BLOCK_4x4, WAVELET, NONE)
  - ordering: str (e.g. MORTON_Z, ROW_MAJOR, CACHE_TILED)
  - reuse: str (e.g. TEMPORAL_DELTA, STATIC_WEIGHT_CACHE, NONE)
  - prediction: str (e.g. SPECTRAL_SURROGATE, LINEAR_EXTRAPOLATE, NONE)
  - approximation: str (e.g. ADAPTIVE_RANK, THRESHOLD_1E3, NONE)
  - correction: str (e.g. RESIDUAL_EXACT, BILATERAL_GUARD, NONE)
  - communication: str (e.g. ZERO_COPY_SHARED_USM, LOCAL_TILED)
  - memory: str (e.g. IN_PLACE, STREAMING_SCRATCH)
  - execution: str (e.g. CPU_AVX2, INTEL_IGPU, HYBRID_DYNAMIC)
  - verification: str (e.g. FREIVALDS_15R, FROBENIUS_EXACT, PERCEPTUAL_SSIM)
"""

from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class AlgorithmGenome:
    """Canonical genetic definition of an algorithm pathway."""
    representation: str = "DENSE"
    decomposition: str = "NONE"
    ordering: str = "ROW_MAJOR"
    reuse: str = "NONE"
    prediction: str = "NONE"
    approximation: str = "NONE"
    correction: str = "NONE"
    communication: str = "LOCAL_TILED"
    memory: str = "IN_PLACE"
    execution: str = "CPU_AVX2"
    verification: str = "FREIVALDS_15R"
    parameters: Dict[str, Any] = field(default_factory=dict)

    def compute_structural_hash(self) -> str:
        """
        Computes an immutable canonical SHA-256 hash representing the algorithm structure.
        Prevents evaluating structurally equivalent candidates repeatedly.
        """
        canonical_str = (
            f"rep={self.representation}|"
            f"dec={self.decomposition}|"
            f"ord={self.ordering}|"
            f"reu={self.reuse}|"
            f"prd={self.prediction}|"
            f"app={self.approximation}|"
            f"cor={self.correction}|"
            f"com={self.communication}|"
            f"mem={self.memory}|"
            f"exe={self.execution}|"
            f"ver={self.verification}|"
            f"par={json.dumps(self.parameters, sort_keys=True)}"
        )
        return hashlib.sha256(canonical_str.encode()).hexdigest()

    def to_canonical_expression(self) -> str:
        """Converts genome into a readable compositional pipeline expression."""
        stages = [self.representation]
        if self.decomposition != "NONE":
            stages.append(self.decomposition)
        if self.ordering != "ROW_MAJOR":
            stages.append(self.ordering)
        if self.reuse != "NONE":
            stages.append(self.reuse)
        if self.approximation != "NONE":
            stages.append(self.approximation)
        if self.prediction != "NONE":
            stages.append(self.prediction)
        if self.correction != "NONE":
            stages.append(self.correction)
        stages.append(self.execution)
        return " >> ".join(stages)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["structural_hash"] = self.compute_structural_hash()
        d["expression"] = self.to_canonical_expression()
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlgorithmGenome":
        clean_data = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**clean_data)
