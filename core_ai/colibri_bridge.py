"""
core_ai/colibri_bridge.py
Bridge module connecting LEO's Python HDC Engine to the Colibri C-Engine.
Forces binary quantization (XOR/Popcount) bypassing standard FP32 ops.
"""

import os
import ctypes
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ColibriBridge:
    def __init__(self):
        self.is_c_linked = False
        self._lib = None
        
        # Try to load the compiled Colibri shared library (if it was built)
        # We look for a .dll (Windows) or .so (Linux) in the colibri_engine/c/ directory
        lib_path = os.path.join(os.path.dirname(__file__), 'colibri_engine', 'c', 'libcolibri.so')
        if os.name == 'nt':
            lib_path = os.path.join(os.path.dirname(__file__), 'colibri_engine', 'c', 'colibri.dll')
            
        if os.path.exists(lib_path):
            try:
                self._lib = ctypes.CDLL(lib_path)
                self.is_c_linked = True
                logger.info("[Colibri] Successfully linked C execution engine.")
            except Exception as e:
                logger.warning(f"[Colibri] Failed to load C library: {e}. Falling back to AVX2 mock.")
        else:
            logger.warning("[Colibri] C library not found. Falling back to AVX2 NumPy bridge.")

    def bind_hypervectors(self, hv1: np.ndarray, hv2: np.ndarray) -> np.ndarray:
        """
        Forces Colibri's execution path to use pure bitwise XOR instead of FP32 mul.
        Takes packed uint8 arrays.
        """
        if self.is_c_linked and hasattr(self._lib, 'colibri_bitwise_xor'):
            # Example C-hook implementation
            res = np.empty_like(hv1)
            self._lib.colibri_bitwise_xor(
                hv1.ctypes.data_as(ctypes.c_void_p),
                hv2.ctypes.data_as(ctypes.c_void_p),
                res.ctypes.data_as(ctypes.c_void_p),
                ctypes.c_size_t(hv1.size)
            )
            return res
        
        # Highly optimized AVX2 NumPy fallback
        return np.bitwise_xor(hv1, hv2)
        
    def batch_hamming_distance(self, query: np.ndarray, memory_matrix: np.ndarray) -> np.ndarray:
        """
        Executes a batched XOR + Popcount using Colibri's internal matrix loops.
        """
        vec_len = query.shape[0]
        num_memories = memory_matrix.shape[0]
        
        if self.is_c_linked and hasattr(self._lib, 'colibri_batch_hamming'):
            res = np.empty(num_memories, dtype=np.float32)
            self._lib.colibri_batch_hamming(
                query.ctypes.data_as(ctypes.c_void_p),
                memory_matrix.ctypes.data_as(ctypes.c_void_p),
                res.ctypes.data_as(ctypes.c_void_p),
                ctypes.c_int(num_memories),
                ctypes.c_int(vec_len)
            )
            return res
            
        # AVX2 NumPy fallback
        xor_res = np.bitwise_xor(memory_matrix, query)
        unpacked = np.unpackbits(xor_res, axis=1)
        diff_counts = np.sum(unpacked, axis=1)
        return diff_counts / (vec_len * 8.0)
