"""
hyper/godmode/playbooks.py
==========================
Six Bottleneck Playbooks (Feature Module J).

Systematic optimization strategies tailored to each diagnosed bottleneck class:
J1. Compute Bottleneck
J2. Memory-Capacity Bottleneck
J3. Memory-Bandwidth Bottleneck
J4. Specialized-Unit Bottleneck
J5. Parallelism Bottleneck
J6. Thermal and Power Bottleneck
"""

from __future__ import annotations
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from .bottleneck_detector import BottleneckClass


class OptimizationPlaybook(BaseModel):
    bottleneck_class: BottleneckClass
    title: str
    primary_mechanisms: List[str]
    concrete_transformations: List[str]
    expected_work_reduction_pct: float
    correctness_contract: str


class BottleneckPlaybookRegistry:
    """
    Stores and activates targeted optimization playbooks for diagnosed bottlenecks.
    """

    PLAYBOOKS: Dict[BottleneckClass, OptimizationPlaybook] = {
        BottleneckClass.COMPUTE_BOUND: OptimizationPlaybook(
            bottleneck_class=BottleneckClass.COMPUTE_BOUND,
            title="J1. Compute Bottleneck Playbook",
            primary_mechanisms=[
                "Algorithmic complexity reduction",
                "Algebraic strength reduction",
                "Dead computation elimination",
                "Symmetric action-reaction halving",
            ],
            concrete_transformations=[
                "Dense matrix multiplication -> Strassen/Blocked sparse skipping",
                "O(N^2) N-body -> O(N^2/2) upper-triangular symmetric pair formulation",
                "2D full spatial convolution -> 1D horizontal + 1D vertical rank-1 separation",
                "Common subexpression elimination and constant folding",
            ],
            expected_work_reduction_pct=50.0,
            correctness_contract="EXACT or NUMERICALLY_EQUIVALENT",
        ),
        BottleneckClass.MEMORY_CAPACITY_BOUND: OptimizationPlaybook(
            bottleneck_class=BottleneckClass.MEMORY_CAPACITY_BOUND,
            title="J2. Memory Capacity Bottleneck Playbook",
            primary_mechanisms=[
                "Working-set limits and pre-execution safety headroom checks",
                "Chunked and tiled streaming (out-of-core execution)",
                "Bounded reusable buffer pools",
                "Quantized weights and activation reuse",
            ],
            concrete_transformations=[
                "Decompose large matrices into 1MB L2 cache-fitting blocks",
                "TinyStories-style memory streaming: retain bulk data on NVMe SSD, stream active working set",
                "INT8 dynamic quantization for neural projections",
                "Bounded buffer pool to eliminate malloc fragmentation",
            ],
            expected_work_reduction_pct=65.0,
            correctness_contract="EXACT (tiling) or NUMERICALLY_EQUIVALENT (quantization)",
        ),
        BottleneckClass.MEMORY_BANDWIDTH_BOUND: OptimizationPlaybook(
            bottleneck_class=BottleneckClass.MEMORY_BANDWIDTH_BOUND,
            title="J3. Memory Bandwidth Bottleneck Playbook",
            primary_mechanisms=[
                "Cache line alignment and loop tiling",
                "Kernel fusion (eliminating temporary intermediate arrays)",
                "Contiguous memory layout re-ordering",
                "Temporal dirty-region differential processing",
            ],
            concrete_transformations=[
                "Fuse activation + normalization into matrix output write",
                "Skip unmutated spatial pixels between adjacent video frames",
                "Vectorized contiguous striding across row-major arrays",
            ],
            expected_work_reduction_pct=40.0,
            correctness_contract="EXACT",
        ),
        BottleneckClass.LAUNCH_OVERHEAD_BOUND: OptimizationPlaybook(
            bottleneck_class=BottleneckClass.LAUNCH_OVERHEAD_BOUND,
            title="J4. Specialized-Unit & Dispatch Bottleneck Playbook",
            primary_mechanisms=[
                "Software alternative implementation for GPU specialized hardware",
                "Kernel fusion and batch aggregation",
                "In-process CPU dispatch bypassing driver launch",
            ],
            concrete_transformations=[
                "Software triangle AABB bounding box clamped rasterization",
                "Vectorized CPU ray-sphere intersection",
                "Immediate CPU execution avoiding asynchronous launch latency",
            ],
            expected_work_reduction_pct=35.0,
            correctness_contract="EXACT",
        ),
        BottleneckClass.SYNCHRONIZATION_BOUND: OptimizationPlaybook(
            bottleneck_class=BottleneckClass.SYNCHRONIZATION_BOUND,
            title="J5. Parallelism & Synchronization Bottleneck Playbook",
            primary_mechanisms=[
                "Alder Lake hybrid P/E-core affinity partitioning",
                "Lock-free single-producer single-consumer ring buffers",
                "Independent task partitioning",
            ],
            concrete_transformations=[
                "Bind compute kernels to 4 P-Cores (threads 0-7)",
                "Offload prefetching and verification to 4 E-Cores (threads 8-11)",
                "Eliminate inter-thread global synchronization barriers",
            ],
            expected_work_reduction_pct=30.0,
            correctness_contract="EXACT",
        ),
        BottleneckClass.THERMAL_POWER_CONSTRAINED: OptimizationPlaybook(
            bottleneck_class=BottleneckClass.THERMAL_POWER_CONSTRAINED,
            title="J6. Thermal & Power Bottleneck Playbook",
            primary_mechanisms=[
                "Elimination of redundant operations",
                "Concurrency tuning based on sustainable steady-state throughput",
                "Thermal deadline scheduling",
            ],
            concrete_transformations=[
                "Reduce thread oversubscription",
                "Shorten memory pipeline duration",
                "Prioritize work elimination over higher clock bursting",
            ],
            expected_work_reduction_pct=25.0,
            correctness_contract="EXACT",
        ),
    }

    @classmethod
    def get_playbook(cls, bottleneck: BottleneckClass) -> OptimizationPlaybook:
        return cls.PLAYBOOKS.get(
            bottleneck,
            cls.PLAYBOOKS[BottleneckClass.COMPUTE_BOUND],
        )
