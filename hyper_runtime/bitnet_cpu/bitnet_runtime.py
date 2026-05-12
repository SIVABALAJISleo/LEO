import ctypes
import numpy as np
import os

class BitNetRuntime:
    def __init__(self):
        self.lib_path = "./hyper_runtime/bitnet_cpu/ternary_kernels.so"
        self.has_avx = False
        try:
            if os.path.exists(self.lib_path):
                self.lib = ctypes.CDLL(self.lib_path)
                self.has_avx = True
        except Exception as e:
            print(f"Warning: Failed to load AVX kernels ({e}). Falling back to numpy.")
            
    def _numpy_ternary_gemm(self, W, A):
        return np.dot(A.astype(np.int32), W.T.astype(np.int32))

    def linear(self, A, W):
        M, K = A.shape
        N = W.shape[0]
        
        if self.has_avx:
            O = np.zeros((M, N), dtype=np.int32)
            self.lib.ternary_gemm_avx2(
                W.ctypes.data_as(ctypes.c_void_p),
                A.ctypes.data_as(ctypes.c_void_p),
                O.ctypes.data_as(ctypes.c_void_p),
                ctypes.c_int(M), ctypes.c_int(N), ctypes.c_int(K)
            )
            return O
        else:
            return self._numpy_ternary_gemm(W, A)
            
    def simulate_quantization(self, X):
        rms = np.sqrt(np.mean(X**2, axis=-1, keepdims=True) + 1e-5)
        X_norm = X / rms
        scale = 127.0 / np.max(np.abs(X_norm), axis=-1, keepdims=True)
        X_q = np.clip(np.round(X_norm * scale), -128, 127).astype(np.int8)
        return X_q, scale
