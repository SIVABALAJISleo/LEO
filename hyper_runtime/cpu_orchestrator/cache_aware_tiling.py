import numpy as np
from typing import Callable

class CacheAwareTiler:
    """
    Implements cache-oblivious matrix blocking (tiling) and simulated Z-order curves.
    Optimizes memory access patterns to keep data in L1/L2 cache during matrix operations.
    """
    def __init__(self, l2_cache_size_kb: int = 1280): # i5-12450H L2 cache per core is 1.25MB
        self.l2_size_bytes = l2_cache_size_kb * 1024

    def tile_matrix_multiply(self, A: np.ndarray, B: np.ndarray, compute_func: Callable = np.dot) -> tuple[np.ndarray, dict]:
        """
        Executes a tiled matrix multiplication using L1/L2 Spatial Tiling.
        A: [M, K], B: [K, N]
        """
        M, K = A.shape
        K2, N = B.shape
        assert K == K2, "Inner dimensions must match"
        
        dtype = A.dtype
        itemsize = A.itemsize
        
        # Calculate optimal tile size based on dtype
        # We want to fit 3 tiles (A, B, C) in L2 cache: 3 * (T * T * itemsize) <= L2_SIZE
        max_elements = self.l2_size_bytes / (3 * itemsize)
        T = int(np.sqrt(max_elements))
        
        # Micro-tiling: If it's int8, force small blocks (e.g., 16x16 = 256 bytes) to ensure 
        # it stays in the absolute fastest L1 cache while the Trie-lookup table (64KB) also resides there.
        if itemsize == 1:
            T = 16
        else:
            T = 2 ** int(np.floor(np.log2(T)))
            
        C_dtype = np.int32 if itemsize == 1 else np.float32
        C = np.zeros((M, N), dtype=C_dtype)
        
        cache_misses = 0
        computations = 0
        
        # Micro-Tile loops
        for i in range(0, M, T):
            for j in range(0, N, T):
                for k in range(0, K, T):
                    i_end = min(i + T, M)
                    j_end = min(j + T, N)
                    k_end = min(k + T, K)
                    
                    cache_misses += 3
                    
                    A_block = A[i:i_end, k:k_end]
                    B_block = B[k:k_end, j:j_end]
                    
                    C[i:i_end, j:j_end] += compute_func(A_block, B_block)
                    computations += (i_end - i) * (j_end - j) * (k_end - k)
                    
        telemetry = {
            "tile_size": T,
            "simulated_cache_misses": cache_misses,
            "total_computations": computations,
            "method": compute_func.__name__
        }
        
        return C, telemetry
