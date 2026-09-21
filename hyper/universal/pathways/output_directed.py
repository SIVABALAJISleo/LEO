"""
hyper/universal/pathways/output_directed.py
==========================================
Family 6: Output-Directed Transformations.
- Demand-driven computation (compute only what the contract demands)
- Top-K partial sorting via Quickselect / Argpartition: O(N) vs O(N log N)
- Spatial subregion rendering & bounding-box evaluation
- Lazy evaluation and stream slicing
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional
import numpy as np

from .schema import UniversalPathway, TransformationFamily


class OutputDirectedTransformations:
    """Generates demand-driven and output-directed pathways."""

    @staticmethod
    def create_topk_pathway(k: int = 10) -> UniversalPathway:
        pid = f"PATH-OUT-TOPK-{int(time.time()*1000)%1000000:06d}"
        chain = ["OUTPUT_DEMAND_ANALYSIS", "QUICKSELECT_ARGPARTITION", "FULL_SORT_ELIMINATION"]

        def topk_eval(arr: np.ndarray, k_val: int = k) -> np.ndarray:
            if len(arr) <= k_val:
                return np.sort(arr)[::-1]
            idx = np.argpartition(arr, -k_val)[-k_val:]
            top_part = arr[idx]
            return top_part[np.argsort(top_part)[::-1]]

        h = UniversalPathway.compute_structural_hash(
            family=TransformationFamily.OUTPUT_DIRECTED.value,
            transformations=chain,
            hardware="CPU_AVX2",
        )

        return UniversalPathway(
            pathway_id=pid,
            family=TransformationFamily.OUTPUT_DIRECTED,
            name=f"Top-K Demand-Driven Slicing (k={k})",
            transformation_chain=chain,
            structural_hash=h,
            target_hardware="CPU_AVX2",
            run_fn=topk_eval,
            estimated_speedup=4.5,
            metadata={"k": k, "complexity": "O(N + K log K)"},
        )

    @staticmethod
    def create_subregion_pathway(bounds: tuple = (0, 64, 0, 64)) -> UniversalPathway:
        pid = f"PATH-OUT-SUBREGION-{int(time.time()*1000)%1000000:06d}"
        chain = ["VIEWPORT_FRUSTUM_CULLING", "BOUNDING_BOX_RESTRICTION", "UNVIEWED_REGION_ELIMINATION"]
        h = UniversalPathway.compute_structural_hash(
            family=TransformationFamily.OUTPUT_DIRECTED.value,
            transformations=chain,
            hardware="CPU_AVX2",
        )
        return UniversalPathway(
            pathway_id=pid,
            family=TransformationFamily.OUTPUT_DIRECTED,
            name="Bounding-Box Subregion Pruning",
            transformation_chain=chain,
            structural_hash=h,
            target_hardware="CPU_AVX2",
            estimated_speedup=3.0,
            metadata={"bounds": bounds},
        )
