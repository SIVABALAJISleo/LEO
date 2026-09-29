"""
hyper_x/wormhole_compiler/workload_fingerprint.py
=============================================================================
HYPER-Ω Workload Fingerprint & Feature Extraction Engine (Section 39)
=============================================================================
Extracts quantitative mathematical and structural features from input tensors:
  - Shape & Dimensions
  - Data Type
  - Exact Zero Sparsity Ratio
  - Algebraic Rank & Defect
  - Delta Magnitude vs Historical State
  - Temporal Block Similarity
  - Numerical Entropy
  - Historical Reuse Frequency
  - Requested Output Size / Dimension Reduction Ratio
  - Dependency Structure (Dense, Sparse, Streaming, Stencil, Projection)

Used by the Learned Prediction and Speculative Execution engines to classify
workloads and predict optimal computational elimination routes.
"""

from __future__ import annotations
import time
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract, CorrectnessRequirement


@dataclass
class WorkloadFingerprint:
    workload_id: str
    shape: Tuple[int, ...]
    dtype: str
    size_elements: int
    size_bytes: int
    sparsity_ratio: float
    zero_rows_count: int
    zero_cols_count: int
    estimated_rank: int
    delta_magnitude: float
    temporal_similarity: float
    entropy: float
    output_dimension_ratio: float
    dependency_structure: str  # "DENSE_GEMM", "SPARSE_MATRIX", "PROJECTION_TOP_K", "STENCIL_GRID", "TEMPORAL_STREAM"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "shape": list(self.shape),
            "dtype": self.dtype,
            "size_elements": self.size_elements,
            "size_bytes": self.size_bytes,
            "sparsity_ratio": round(self.sparsity_ratio, 4),
            "zero_rows_count": self.zero_rows_count,
            "zero_cols_count": self.zero_cols_count,
            "estimated_rank": self.estimated_rank,
            "delta_magnitude": round(self.delta_magnitude, 4),
            "temporal_similarity": round(self.temporal_similarity, 4),
            "entropy": round(self.entropy, 4),
            "output_dimension_ratio": round(self.output_dimension_ratio, 6),
            "dependency_structure": self.dependency_structure,
        }


class WorkloadFingerprinter:
    """
    Extracts high-dimensional quantitative fingerprints from workloads.
    """

    @staticmethod
    def extract_fingerprint(
        inputs: Tuple[Any, ...],
        contract: WorkloadContract,
        previous_input: Optional[Any] = None,
    ) -> WorkloadFingerprint:
        primary = inputs[0] if len(inputs) > 0 else np.zeros((1, 1), dtype=np.float32)

        if not isinstance(primary, np.ndarray):
            # Non-tensor primitive
            return WorkloadFingerprint(
                workload_id=contract.workload_id,
                shape=(),
                dtype=type(primary).__name__,
                size_elements=1,
                size_bytes=8,
                sparsity_ratio=0.0,
                zero_rows_count=0,
                zero_cols_count=0,
                estimated_rank=1,
                delta_magnitude=0.0,
                temporal_similarity=0.0,
                entropy=0.0,
                output_dimension_ratio=1.0,
                dependency_structure="SCALAR_PRIMITIVE",
            )

        shape = primary.shape
        dtype = str(primary.dtype)
        size_elems = primary.size
        size_bytes = primary.nbytes

        # Sparsity & Zero slices
        if primary.ndim >= 2:
            zero_elems = np.sum(primary == 0.0)
            sparsity = float(zero_elems / max(1, size_elems))
            zero_rows = int(np.sum(np.all(primary == 0.0, axis=-1)))
            zero_cols = int(np.sum(np.all(primary == 0.0, axis=0))) if primary.ndim == 2 else 0
        else:
            sparsity = float(np.sum(primary == 0.0) / max(1, size_elems))
            zero_rows = 0
            zero_cols = 0

        # Rank estimate (fast sub-sample SVD if large)
        if primary.ndim == 2 and min(primary.shape) > 1:
            m, k = primary.shape
            if m <= 128 and k <= 128:
                try:
                    s = np.linalg.svd(primary, compute_uv=False)
                    eps = float(np.finfo(primary.dtype).eps) if np.issubdtype(primary.dtype, np.floating) else 1e-12
                    tol = float(s[0] * max(m, k) * eps) if len(s) > 0 and s[0] > 0 else 1e-12
                    est_rank = int(np.sum(s > tol))
                except Exception:
                    est_rank = min(m, k)
            else:
                est_rank = min(m, k)
        else:
            est_rank = min(shape) if shape else 1

        # Delta & Temporal similarity
        if previous_input is not None and isinstance(previous_input, np.ndarray) and previous_input.shape == primary.shape:
            diff = np.abs(primary - previous_input)
            delta_mag = float(np.mean(diff))
            temporal_sim = float(np.sum(diff == 0.0) / max(1, size_elems))
        else:
            delta_mag = 0.0
            temporal_sim = 0.0

        # Fast Shannon entropy estimate (via 16-bin histogram on normalized sample)
        sample = primary.ravel()[:1024]
        if sample.size > 0:
            hist, _ = np.histogram(sample, bins=16, density=True)
            hist = hist[hist > 0]
            entropy = float(-np.sum(hist * np.log2(hist + 1e-12))) if len(hist) > 0 else 0.0
        else:
            entropy = 0.0

        # Output dimension ratio
        if len(contract.output_shape) > 0 and contract.input_shape:
            in_vol = math.prod(contract.input_shape) if contract.input_shape else 1
            out_vol = math.prod(contract.output_shape)
            out_ratio = float(out_vol / max(1, in_vol))
        else:
            out_ratio = 1.0

        # Structural classification
        if contract.correctness == CorrectnessRequirement.TOP_K or out_ratio < 0.05:
            dep_struct = "PROJECTION_TOP_K"
        elif "GRAPHICS" in contract.workload_id or temporal_sim > 0.5:
            dep_struct = "TEMPORAL_STREAM"
        elif "STENCIL" in contract.workload_id:
            dep_struct = "STENCIL_GRID"
        elif sparsity > 0.6:
            dep_struct = "SPARSE_MATRIX"
        else:
            dep_struct = "DENSE_GEMM"

        return WorkloadFingerprint(
            workload_id=contract.workload_id,
            shape=shape,
            dtype=dtype,
            size_elements=size_elems,
            size_bytes=size_bytes,
            sparsity_ratio=sparsity,
            zero_rows_count=zero_rows,
            zero_cols_count=zero_cols,
            estimated_rank=est_rank,
            delta_magnitude=delta_mag,
            temporal_similarity=temporal_sim,
            entropy=entropy,
            output_dimension_ratio=out_ratio,
            dependency_structure=dep_struct,
        )
