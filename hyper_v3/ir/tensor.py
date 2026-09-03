"""
hyper_v3/ir/tensor.py
Tensor descriptors representing shapes, dtypes, memory layouts, and sparsity.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np


@dataclass
class TensorDescriptor:
    """Describes a tensor operand or intermediate in the computation graph."""
    name: str
    shape: List[int]
    dtype: str = "float32"
    is_sparse: bool = False
    sparsity_ratio: float = 0.0
    memory_layout: str = "row_major"  # row_major, col_major, blocked, tiled
    memory_bytes: int = 0
    device_residency: str = "CPU"  # CPU, iGPU, SHARED
    is_constant: bool = False

    def __post_init__(self):
        if self.memory_bytes == 0 and self.shape:
            element_count = int(np.prod(self.shape))
            bytes_per_elem = 4 if "32" in self.dtype else (2 if "16" in self.dtype else 8)
            self.memory_bytes = element_count * bytes_per_elem
