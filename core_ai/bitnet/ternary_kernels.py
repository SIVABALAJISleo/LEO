import numpy as np

try:
    from numba import njit, prange
except ImportError:
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range

class TernaryCPUKernels:
    def __init__(self):
        # Precompute lookup table for 4-weight blocks (byte-level)
        self.lookup_table = self._build_lookup_table()
        
    def _build_lookup_table(self):
        # 256 possible bytes (0 to 255) representing 4 ternary values each
        # Ternary encoding: 00 = 0, 01 = 1, 10 = -1
        table = np.zeros((256, 4), dtype=np.int8)
        for i in range(256):
            val = i
            for j in range(4):
                bits = val & 0b11
                if bits == 1:
                    table[i, j] = 1
                elif bits == 2:
                    table[i, j] = -1
                else:
                    table[i, j] = 0
                val >>= 2
        return table
        
    def matmul_packed(self, packed_weights, scales, activations, block_size=128):
        return ternary_matmul_packed(packed_weights, scales, activations, block_size)

@njit(parallel=True, fastmath=True)
def ternary_matmul_packed(packed_weights: np.ndarray,
                          scales: np.ndarray,
                          activations: np.ndarray,
                          block_size: int = 128) -> np.ndarray:
    """
    Optimized ternary matrix multiplication via on-the-fly unpacking.
    packed_weights: (M, K // 16) uint32 arrays
    activations: (K, N) FP32 array
    output: (M, N) FP32 array
    """
    M = packed_weights.shape[0]
    N = activations.shape[1]
    K = activations.shape[0]
    
    output = np.zeros((M, N), dtype=np.float32)
    
    for m in prange(M):
        for k_blk in range(packed_weights.shape[1]):
            val = packed_weights[m, k_blk]
            scale = scales[m, k_blk // (block_size // 16)]
            
            # Unpack 16 weights
            for i in range(16):
                bits = val & 0b11
                w = 0
                if bits == 1: w = 1
                elif bits == 2: w = -1
                
                k = k_blk * 16 + i
                if w != 0 and k < K:
                    for n in range(N):
                        output[m, n] += (w * activations[k, n]) * scale
                val >>= 2
                
    return output

@njit(parallel=True, fastmath=True)  
def ternary_matmul_lookup(packed_weights: np.ndarray,
                          lookup_table: np.ndarray,
                          activations: np.ndarray) -> np.ndarray:
    """
    Lookup-table based fast execution using precomputed byte-states.
    packed_weights: (M, K // 4) uint8 arrays
    """
    M = packed_weights.shape[0]
    N = activations.shape[1]
    K = activations.shape[0]
    
    output = np.zeros((M, N), dtype=np.float32)
    
    for m in prange(M):
        for k_blk in range(packed_weights.shape[1]):
            byte_val = packed_weights[m, k_blk]
            w_vals = lookup_table[byte_val]
            
            for i in range(4):
                w = w_vals[i]
                k = k_blk * 4 + i
                if w != 0 and k < K:
                    for n in range(N):
                        output[m, n] += w * activations[k, n]
                        
    return output
