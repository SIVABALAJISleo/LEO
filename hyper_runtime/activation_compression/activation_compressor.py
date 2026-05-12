import numpy as np

class ActivationCompressionSystem:
    """
    Module 8 — Activation Compression System
    Reduces activation memory explosion via entropy-aware compression and lazy reconstruction.
    """
    def __init__(self, compression_ratio=0.25):
        self.compression_ratio = compression_ratio
        
    def compress_activation(self, activation_tensor):
        """
        Simulates lossy compression of activations.
        Drops the lowest variance dimensions.
        """
        variance = np.var(activation_tensor, axis=0)
        
        num_features = activation_tensor.shape[-1]
        keep_k = int(num_features * self.compression_ratio)
        
        indices_to_keep = np.argsort(variance)[-keep_k:]
        compressed_tensor = activation_tensor[:, indices_to_keep]
        
        return compressed_tensor, indices_to_keep
        
    def reconstruct_activation(self, compressed_tensor, indices, original_shape):
        """
        Lazy reconstruction (padding zeros for dropped dimensions).
        """
        reconstructed = np.zeros(original_shape, dtype=compressed_tensor.dtype)
        reconstructed[:, indices] = compressed_tensor
        return reconstructed
