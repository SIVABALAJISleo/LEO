"""
leo_infinity_kernels standalone library v2.0
High-performance CPU/iGPU execution kernels — NVIDIA-irrelevant inference.
"""

__version__ = "2.0.0"

from .ternary_lut import TernaryLUTEngine
from .moe_spec import MoESpecEngine
from .predictive_prefetch import PredictivePrefetchEngine
from .dreamer import PredictiveDreamer
from .kernel_zoo_lite import KernelZooLite

__all__ = [
    "TernaryLUTEngine",
    "MoESpecEngine",
    "PredictivePrefetchEngine",
    "PredictiveDreamer",
    "KernelZooLite",
]
