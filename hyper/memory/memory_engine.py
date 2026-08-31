"""
hyper/memory/memory_engine.py
=============================
Memory Engine & Lifetime Profiler (Section 33):
Optimizes allocation counts, data layout (row-major vs column-major vs tiled),
buffer lifetime, peak memory, and average memory usage.
"""

from typing import Dict, Any, Tuple
import numpy as np


class MemoryEngine:
    """
    Profiles and optimizes memory allocations and cache-line strides.
    """
    def __init__(self):
        self.peak_memory_bytes: int = 0
        self.total_allocations: int = 0

    def optimize_layout_for_gemm(self, A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Ensures A is C-contiguous (row-major) and B is Fortran-contiguous (column-major)
        so inner loop accesses cache lines contiguously without stride misses.
        """
        A_contig = np.ascontiguousarray(A)
        B_transposed = np.asfortranarray(B)
        
        mem_A = A_contig.nbytes
        mem_B = B_transposed.nbytes
        self.peak_memory_bytes = max(self.peak_memory_bytes, mem_A + mem_B)
        self.total_allocations += 2

        return A_contig, B_transposed, {
            "A_contiguous": A_contig.flags['C_CONTIGUOUS'],
            "B_contiguous": B_transposed.flags['F_CONTIGUOUS'],
            "memory_footprint_bytes": mem_A + mem_B,
            "peak_memory_bytes": self.peak_memory_bytes
        }
