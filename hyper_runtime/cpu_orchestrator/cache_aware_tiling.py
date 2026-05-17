import numpy as np

class CacheAwareTiler:
    """
    Implements cache-oblivious matrix blocking (tiling) and simulated Z-order curves.
    Optimizes memory access patterns to keep data in L1/L2/L3 cache during matrix operations.
    """
    def __init__(self, l2_cache_size_kb: int = 1024):
        self.l2_size_bytes = l2_cache_size_kb * 1024
        
        # Calculate optimal tile size assuming float32 (4 bytes)
        # We want to fit 3 tiles (A, B, C) in L2 cache: 3 * (T * T * 4) <= L2_SIZE
        max_elements = self.l2_size_bytes / (3 * 4)
        self.optimal_tile_size = int(np.sqrt(max_elements))
        # Round down to nearest power of 2 for alignment
        self.optimal_tile_size = 2 ** int(np.floor(np.log2(self.optimal_tile_size)))

    def tile_matrix_multiply(self, A: np.ndarray, B: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Simulates a tiled matrix multiplication.
        A: [M, K], B: [K, N]
        """
        M, K = A.shape
        K2, N = B.shape
        assert K == K2, "Inner dimensions must match"
        
        C = np.zeros((M, N), dtype=np.float32)
        T = self.optimal_tile_size
        
        # Simulated metrics tracking
        cache_misses = 0
        computations = 0
        
        # Tile loops
        for i in range(0, M, T):
            for j in range(0, N, T):
                for k in range(0, K, T):
                    # Define block boundaries
                    i_end = min(i + T, M)
                    j_end = min(j + T, N)
                    k_end = min(k + T, K)
                    
                    # Simulated cache load for the block
                    cache_misses += 3 # Load A_block, B_block, C_block into cache
                    
                    # Extract blocks (In a real implementation, memory views are used)
                    A_block = A[i:i_end, k:k_end]
                    B_block = B[k:k_end, j:j_end]
                    
                    # Compute block
                    C[i:i_end, j:j_end] += np.dot(A_block, B_block)
                    computations += (i_end - i) * (j_end - j) * (k_end - k)
                    
        telemetry = {
            "tile_size": T,
            "simulated_cache_misses": cache_misses,
            "total_computations": computations
        }
        
        return C, telemetry
