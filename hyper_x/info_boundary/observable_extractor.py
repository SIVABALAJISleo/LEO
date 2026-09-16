"""
hyper_x/info_boundary/observable_extractor.py
=============================================
Phase 2: Observable-Directed Computation & Observable Extractor.
Identifies the minimum observable required by the application contract:
- Rendering: displayed pixels, viewport frustum, frame latency, perceptual threshold
- LLM: next token, top-k logits, requested sequence, argmax
- Scientific: target fields, spatial probe points, required precision
- Search / RAG: retrieved top-k document IDs, relevance ranking
Rule: Never compute entire reference intermediate state if contract only observes a subset.
If the contract requires full state, compute full state.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np


class ObservableType(str, enum.Enum):
    FULL_TENSOR = "FULL_TENSOR"
    SUBREGION = "SUBREGION"
    TOP_K = "TOP_K"
    ARGMAX = "ARGMAX"
    SCALAR_STATISTIC = "SCALAR_STATISTIC"  # e.g., trace, norm, mean
    SPARSE_SAMPLES = "SPARSE_SAMPLES"
    PERCEPTUAL_PIXELS = "PERCEPTUAL_PIXELS"


@dataclass
class ObservableSpecification:
    workload_id: str
    observable_type: ObservableType
    target_dimensions: Tuple[int, ...]
    observed_fraction: float  # [0.0, 1.0] of reference output actually consumed
    precision_required: str   # "FP32", "FP16", "INT8", "EXACT"
    quality_threshold: Optional[float] = None  # e.g., PSNR dB or Relative Tolerance
    slice_indices: Optional[List[slice]] = None
    target_k: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ObservableExtractor:
    """
    Extracts application-specific observable specifications and projects
    candidate computational requirements backwards.
    """

    @staticmethod
    def extract_from_contract(
        workload_id: str,
        contract: Dict[str, Any],
        nominal_output_shape: Tuple[int, ...],
    ) -> ObservableSpecification:
        mode = contract.get("mode", "FULL_TENSOR")

        if mode in ("TOP_K", "ARGMAX"):
            k = contract.get("k", 1 if mode == "ARGMAX" else 5)
            total_elements = int(np.prod(nominal_output_shape))
            fraction = min(1.0, k / max(1, total_elements))
            return ObservableSpecification(
                workload_id=workload_id,
                observable_type=ObservableType.TOP_K if mode == "TOP_K" else ObservableType.ARGMAX,
                target_dimensions=(k,) if mode == "TOP_K" else (1,),
                observed_fraction=round(fraction, 6),
                precision_required="ORDER_PRESERVING",
                target_k=k,
                metadata={"contract_mode": mode},
            )

        elif mode == "TRACE":
            # For square matrix (N, N), trace only observes N diagonal elements out of N^2
            N = nominal_output_shape[0] if len(nominal_output_shape) >= 2 else 1
            fraction = 1.0 / max(1, N)
            return ObservableSpecification(
                workload_id=workload_id,
                observable_type=ObservableType.SCALAR_STATISTIC,
                target_dimensions=(1,),
                observed_fraction=round(fraction, 6),
                precision_required=contract.get("precision", "FP32"),
                metadata={"statistic": "trace", "diagonal_elements_only": True},
            )

        elif mode == "PERCEPTUAL_PIXELS":
            psnr_target = contract.get("target_psnr_db", 40.0)
            return ObservableSpecification(
                workload_id=workload_id,
                observable_type=ObservableType.PERCEPTUAL_PIXELS,
                target_dimensions=nominal_output_shape,
                observed_fraction=1.0,
                precision_required="PERCEPTUAL",
                quality_threshold=psnr_target,
                metadata={"target_psnr_db": psnr_target},
            )

        # Default full tensor
        return ObservableSpecification(
            workload_id=workload_id,
            observable_type=ObservableType.FULL_TENSOR,
            target_dimensions=nominal_output_shape,
            observed_fraction=1.0,
            precision_required=contract.get("precision", "FP32"),
            metadata={"contract_mode": "FULL_TENSOR"},
        )
