import numpy as np
import math

class BitLinear:
    """
    Implements 1.58-bit (Ternary) Linear Layer.
    Weights are quantized to {-1, 0, 1}.
    Activations are quantized to INT8.
    Replaces dense floating-point matrix multiplication with integer addition/subtraction.
    """
    def __init__(self, in_features: int, out_features: int, eps: float = 1e-5):
        self.in_features = in_features
        self.out_features = out_features
        self.eps = eps
        
        # Initialize floating point weights (simulate pre-trained weights)
        np.random.seed(42)
        std = math.sqrt(2.0 / in_features)
        self.weight = np.random.normal(0, std, (out_features, in_features)).astype(np.float32)
        
        # Quantization states
        self.weight_quantized = None
        self.weight_scale = None

    def quantize_weights(self):
        """
        Quantizes weights to {-1, 0, 1} using mean absolute value scaling.
        Formula: W_q = round(clip(W / (scale + eps), -1, 1))
        scale = mean(abs(W))
        """
        self.weight_scale = np.mean(np.abs(self.weight))
        scaled_weight = self.weight / (self.weight_scale + self.eps)
        # Quantize to ternary
        self.weight_quantized = np.clip(np.round(scaled_weight), -1.0, 1.0).astype(np.int8)
        
    def quantize_activations(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Quantizes activations to INT8 using absolute maximum scaling per token.
        x shape: [batch_size, seq_len, in_features]
        Returns: (quantized_x, activation_scales)
        """
        # Calculate scale per token: scale = max(abs(x)) / 127
        max_abs = np.max(np.abs(x), axis=-1, keepdims=True)
        scale = max_abs / 127.0
        
        scaled_x = x / (scale + self.eps)
        quantized_x = np.clip(np.round(scaled_x), -128.0, 127.0).astype(np.int8)
        
        return quantized_x, scale

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Executes the BitLinear forward pass.
        Returns the output float tensor and a telemetry dict.
        """
        if self.weight_quantized is None:
            self.quantize_weights()
            
        # 1. Quantize Activations
        x_q, x_scale = self.quantize_activations(x)
        
        # 2. Integer Matrix Multiplication (Simulated ternary + INT8 dot product)
        # In hardware, this is purely ADD/SUB operations because weights are {-1, 0, 1}
        # We use standard dot product here for numpy simulation, but it represents integer MACs
        out_q = np.dot(x_q.astype(np.int32), self.weight_quantized.T.astype(np.int32))
        
        # 3. Dequantize
        # Output = out_q * (weight_scale * activation_scale)
        out_f = out_q.astype(np.float32) * (self.weight_scale * x_scale)
        
        telemetry = {
            "weight_memory_mb": self.weight_quantized.nbytes / (1024 * 1024),
            "original_memory_mb": self.weight.nbytes / (1024 * 1024),
            "compression_ratio": self.weight.nbytes / max(1, self.weight_quantized.nbytes),
            "operations_type": "INT8_ADD_SUB"
        }
        
        return out_f, telemetry
