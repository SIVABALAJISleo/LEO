import numpy as np

class QuantizedKVCache:
    """
    Implements a low-bit (INT8/INT4) Key-Value cache.
    Drastically reduces memory footprint for long-context generation.
    """
    def __init__(self, max_seq_len: int, num_heads: int, head_dim: int, bits: int = 8):
        self.max_seq_len = max_seq_len
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.bits = bits
        
        self.dtype = np.int8 if bits >= 8 else np.uint8 # Use uint8 for packed int4
        
        # Pre-allocate cache memory
        self.k_cache = np.zeros((max_seq_len, num_heads, head_dim), dtype=self.dtype)
        self.v_cache = np.zeros((max_seq_len, num_heads, head_dim), dtype=self.dtype)
        
        # Scaling factors per token (need float16/float32)
        self.k_scales = np.zeros((max_seq_len, num_heads), dtype=np.float32)
        self.v_scales = np.zeros((max_seq_len, num_heads), dtype=np.float32)
        
        self.current_seq_len = 0
        
    def _quantize(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Quantizes fp32 tensor to int8 with per-token scaling."""
        max_abs = np.max(np.abs(x), axis=-1, keepdims=True)
        scale = max_abs / 127.0
        scale[scale == 0] = 1.0 # Prevent division by zero
        
        x_q = np.clip(np.round(x / scale), -128, 127).astype(np.int8)
        return x_q, np.squeeze(scale, axis=-1)

    def append(self, k: np.ndarray, v: np.ndarray):
        """
        Appends new K, V states to the cache.
        Shapes: [seq_len, num_heads, head_dim]
        """
        seq_len = k.shape[0]
        if self.current_seq_len + seq_len > self.max_seq_len:
            raise ValueError("KV Cache Overflow")
            
        k_q, k_s = self._quantize(k)
        v_q, v_s = self._quantize(v)
        
        start = self.current_seq_len
        end = start + seq_len
        
        self.k_cache[start:end] = k_q
        self.v_cache[start:end] = v_q
        self.k_scales[start:end] = k_s
        self.v_scales[start:end] = v_s
        
        self.current_seq_len += seq_len
        
    def get_memory_footprint_mb(self) -> dict:
        """Returns the memory footprint of the active cache."""
        k_mb = self.k_cache.nbytes / (1024 * 1024)
        v_mb = self.v_cache.nbytes / (1024 * 1024)
        scales_mb = (self.k_scales.nbytes + self.v_scales.nbytes) / (1024 * 1024)
        
        return {
            "quantized_cache_mb": k_mb + v_mb + scales_mb,
            "fp32_equivalent_mb": (self.max_seq_len * self.num_heads * self.head_dim * 4 * 2) / (1024 * 1024),
            "compression_ratio": (self.max_seq_len * self.num_heads * self.head_dim * 4 * 2) / max(1, self.k_cache.nbytes + self.v_cache.nbytes)
        }
