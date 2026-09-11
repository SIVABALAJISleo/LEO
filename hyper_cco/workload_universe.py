"""
hyper_cco/workload_universe.py
=============================================================================
Workload Universe & Taxonomy Matrix (Sections 44, 45, 46)
=============================================================================
Defines an explicit multi-dimensional parameter universe covering:
  - Dense Numerical Computing
  - Sparse Linear Algebra
  - AI Model Blocks (Attention, FeedForward, Embedding)
  - Graphics & Video (720p/1080p, Temporal Stencils, Bilateral Filters)
  - Scientific Computing (PDE, Poisson, Heat Diffusion)
  - Search & Retrieval (MIPS, Top-K, Cosine Similarity)

Includes parameter sweeps across:
  - Input dimensions (N in [32, 64, 128, 256, 512, 1024])
  - Sparsity levels (0.0 to 0.99)
  - Rank ratios (r/N from 0.05 to 1.0)
  - Tolerances (1e-6 to 1e-2)
  - Distributions (Gaussian, Uniform, Power-Law, Cauchy, Checkerboard)
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from hyper_cco.contract import WorkloadContract, CorrectnessClass


class WorkloadCategory(str, enum.Enum):
    DENSE_NUMERICAL = "DENSE_NUMERICAL"
    SPARSE_ALGEBRA = "SPARSE_ALGEBRA"
    AI_INFERENCE = "AI_INFERENCE"
    GRAPHICS_RENDERING = "GRAPHICS_RENDERING"
    SCIENTIFIC_SIMULATION = "SCIENTIFIC_SIMULATION"
    SEARCH_RETRIEVAL = "SEARCH_RETRIEVAL"
    VIDEO_PROCESSING = "VIDEO_PROCESSING"


@dataclass
class WorkloadUniverseEntry:
    entry_id: str
    category: WorkloadCategory
    name: str
    dimension_range: Tuple[int, int]
    sparsity_range: Tuple[float, float]
    rank_ratio_range: Tuple[float, float]
    tolerance_default: float
    correctness_class_default: CorrectnessClass
    deterministic: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "category": self.category.value,
            "name": self.name,
            "dimension_range": list(self.dimension_range),
            "sparsity_range": list(self.sparsity_range),
            "rank_ratio_range": list(self.rank_ratio_range),
            "tolerance_default": self.tolerance_default,
            "correctness_class_default": self.correctness_class_default.value,
            "deterministic": self.deterministic,
        }


class WorkloadUniverse:
    """Manages the explicit universe of testable workloads."""

    def __init__(self):
        self.entries: Dict[str, WorkloadUniverseEntry] = {}
        self._register_default_universe()

    def _register_default_universe(self):
        default_items = [
            WorkloadUniverseEntry(
                entry_id="UNIV_DENSE_GEMM",
                category=WorkloadCategory.DENSE_NUMERICAL,
                name="Dense General Matrix Multiplication (GEMM)",
                dimension_range=(32, 1024),
                sparsity_range=(0.0, 0.20),
                rank_ratio_range=(0.05, 1.0),
                tolerance_default=1e-4,
                correctness_class_default=CorrectnessClass.NUMERICALLY_BOUNDED,
            ),
            WorkloadUniverseEntry(
                entry_id="UNIV_SPARSE_CSR",
                category=WorkloadCategory.SPARSE_ALGEBRA,
                name="Sparse Matrix-Vector Multiplication (SpMV)",
                dimension_range=(100, 10000),
                sparsity_range=(0.80, 0.999),
                rank_ratio_range=(0.50, 1.0),
                tolerance_default=1e-3,
                correctness_class_default=CorrectnessClass.APPLICATION_CONTRACT_EQUIVALENT,
            ),
            WorkloadUniverseEntry(
                entry_id="UNIV_AI_ATTENTION",
                category=WorkloadCategory.AI_INFERENCE,
                name="Multi-Head Attention Query-Key Product",
                dimension_range=(64, 512),
                sparsity_range=(0.10, 0.60),
                rank_ratio_range=(0.10, 0.50),
                tolerance_default=1e-3,
                correctness_class_default=CorrectnessClass.NUMERICALLY_BOUNDED,
            ),
            WorkloadUniverseEntry(
                entry_id="UNIV_GRAPHICS_FILTER",
                category=WorkloadCategory.GRAPHICS_RENDERING,
                name="Realtime 720p/1080p Temporal Image Filtering",
                dimension_range=(256, 1920),
                sparsity_range=(0.0, 0.99),
                rank_ratio_range=(0.01, 0.20),
                tolerance_default=1e-2,
                correctness_class_default=CorrectnessClass.PERCEPTUALLY_EQUIVALENT,
            ),
            WorkloadUniverseEntry(
                entry_id="UNIV_SCIENTIFIC_PDE",
                category=WorkloadCategory.SCIENTIFIC_SIMULATION,
                name="2D Poisson Equation Multigrid Stencil",
                dimension_range=(64, 512),
                sparsity_range=(0.85, 0.98),
                rank_ratio_range=(0.10, 0.40),
                tolerance_default=1e-2,
                correctness_class_default=CorrectnessClass.NUMERICALLY_BOUNDED,
            ),
            WorkloadUniverseEntry(
                entry_id="UNIV_SEARCH_TOPK",
                category=WorkloadCategory.SEARCH_RETRIEVAL,
                name="Maximal Inner Product Search (MIPS) Top-K",
                dimension_range=(1000, 50000),
                sparsity_range=(0.0, 0.50),
                rank_ratio_range=(0.01, 0.10),
                tolerance_default=1e-3,
                correctness_class_default=CorrectnessClass.APPLICATION_CONTRACT_EQUIVALENT,
            ),
        ]
        for item in default_items:
            self.entries[item.entry_id] = item

    def get_universe_size(self) -> int:
        return len(self.entries)

    def list_entries(self) -> List[WorkloadUniverseEntry]:
        return list(self.entries.values())
