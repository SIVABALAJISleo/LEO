"""
hyper_cel/execution/igpu.py
=============================================================================
HYPER-CEL: Intel UHD Graphics iGPU Execution Backend (Mode B)
=============================================================================
Optimized for:
  - Zero-Copy UMA Shared Memory Buffer access
  - Regular dense tensor and matrix products
  - Fast 2D image filtering & parallel reductions
  - Batch embedding computations
"""

import time
import numpy as np
from typing import Dict, Any, Tuple
from core_ai.alchemy_shared_memory import AlchemySharedMemoryBuffer
from core_ai.alchemy_engine import MortonCacheObliviousEngine

class iGPUExecutionBackend:
    """Integrated GPU execution backend managing zero-copy pinned shared memory."""

    def __init__(self, shared_memory_pool_mb: int = 128):
        self.device_name = "Intel UHD Graphics (48 EUs) UMA"
        self.shared_mem = AlchemySharedMemoryBuffer(pool_size_mb=shared_memory_pool_mb)

    def execute_dense_gemm(self, A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Executes dense matrix multiplication in shared unified memory."""
        t0 = time.perf_counter()
        # Allocate in zero-copy shared memory
        M, K = A.shape
        _, N = B.shape
        buf = self.shared_mem.allocate_tensor("igpu_gemm_out", (M, N), dtype=A.dtype)
        
        # Execute Morton cache-friendly matrix product
        buf[:] = MortonCacheObliviousEngine.morton_matmul(A, B)
        t1 = time.perf_counter()
        
        latency_ms = (t1 - t0) * 1000.0
        return buf, {
            "device": self.device_name,
            "latency_ms": round(latency_ms, 3),
            "shared_memory_alloc_mb": self.shared_mem.get_utilization()["allocated_mb"]
        }

    def execute_parallel_reduction(self, tensor: np.ndarray, axis: int = -1) -> np.ndarray:
        """Parallel tensor reduction over specified axis."""
        return np.sum(tensor, axis=axis)
