"""
DirectML Backend Wrapper for Intel iGPU without CUDA.
"""
import numpy as np

class DirectMLBackend:
    def __init__(self):
        self.device = "dml"
        self.available = False
        try:
            # Placeholder for actual DML bindings
            import onnxruntime as ort
            if 'DmlExecutionProvider' in ort.get_available_providers():
                self.available = True
        except ImportError:
            pass

    def is_available(self):
        return self.available

    def execute_dense_matmul(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        # Fallback to numpy if true DML bindings aren't loaded in this shim
        return np.dot(a, b)
