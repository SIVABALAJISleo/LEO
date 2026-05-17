import numpy as np

class EntropyActivationCompressor:
    """
    Compresses neural activations by aggressively truncating/quantizing
    low-variance (low-entropy) channels.
    """
    def __init__(self, variance_threshold: float = 0.05, quantization_bits: int = 8):
        self.variance_threshold = variance_threshold
        self.quantization_bits = quantization_bits
        
    def compress(self, activations: np.ndarray) -> dict:
        """
        Compresses fp32 activations.
        Returns a compressed payload dict and decompression metadata.
        """
        # Calculate variance across the feature dimension
        var = np.var(activations, axis=(0, 1)) if activations.ndim == 3 else np.var(activations, axis=0)
        
        # Identify high-variance (critical) vs low-variance (compressible) channels
        high_var_mask = var > self.variance_threshold
        low_var_mask = ~high_var_mask
        
        # Keep high-variance channels in fp16
        critical_features = activations[..., high_var_mask].astype(np.float16)
        
        # Quantize low-variance channels to INT8 or discard/average if extremely low
        # Here we quantize to int8
        low_var_features = activations[..., low_var_mask]
        max_abs = np.max(np.abs(low_var_features), axis=-1, keepdims=True)
        # Avoid div by zero
        max_abs[max_abs == 0] = 1.0
        
        scale = max_abs / ((2 ** (self.quantization_bits - 1)) - 1)
        quantized_low_var = np.clip(np.round(low_var_features / scale), -128, 127).astype(np.int8)
        
        compressed_payload = {
            "critical": critical_features,
            "quantized": quantized_low_var,
            "scale": scale.astype(np.float16),
            "high_var_mask": high_var_mask,
            "original_shape": activations.shape,
            "original_dtype": activations.dtype
        }
        
        original_bytes = activations.nbytes
        compressed_bytes = critical_features.nbytes + quantized_low_var.nbytes + scale.nbytes + high_var_mask.nbytes
        
        return compressed_payload, {
            "original_mb": original_bytes / (1024 * 1024),
            "compressed_mb": compressed_bytes / (1024 * 1024),
            "ratio": original_bytes / max(1, compressed_bytes)
        }
        
    def decompress(self, payload: dict) -> np.ndarray:
        """
        Reconstructs the original activations (with slight compression loss).
        """
        high_var_mask = payload["high_var_mask"]
        shape = payload["original_shape"]
        
        # Dequantize
        dequantized_low = payload["quantized"].astype(np.float32) * payload["scale"].astype(np.float32)
        critical_float = payload["critical"].astype(np.float32)
        
        # Reassemble
        reconstructed = np.zeros(shape, dtype=np.float32)
        reconstructed[..., high_var_mask] = critical_float
        reconstructed[..., ~high_var_mask] = dequantized_low
        
        return reconstructed
