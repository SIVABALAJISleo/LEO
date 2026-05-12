import numpy as np

def quantize_kv(kv_tensor, bits=8):
    """
    Quantizes floating point KV cache to INT8/INT4 for disk storage/RAM savings.
    """
    if bits == 8:
        # Min-max quantization per channel/head
        min_val = np.min(kv_tensor, axis=-1, keepdims=True)
        max_val = np.max(kv_tensor, axis=-1, keepdims=True)
        scale = (max_val - min_val) / 255.0
        scale = np.where(scale == 0, 1e-9, scale) # Avoid div zero
        
        q_tensor = np.round((kv_tensor - min_val) / scale).astype(np.uint8)
        return q_tensor, min_val, scale
    else:
        raise NotImplementedError("Only 8-bit KV quantization currently implemented.")

def dequantize_kv(q_tensor, min_val, scale):
    """Restores quantized KV cache to float32."""
    return q_tensor.astype(np.float32) * scale + min_val
