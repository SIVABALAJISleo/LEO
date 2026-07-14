import ctypes
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

class IGpuOrchestrator:
    """
    Python Daemon to control the SYCL C++ Kernel.
    Manages the asynchronous staging of model weights into the CPU L3 cache.
    """
    def __init__(self, dll_path: str = "hyper_runtime/sycl_fetcher.so"):
        self.dll_path = dll_path
        self._lib = None
        self._load_lib()
        
    def _load_lib(self):
        if not os.path.exists(self.dll_path):
            logger.warning(f"SYCL library not found at {self.dll_path}. iGPU fetcher will run in simulation mode.")
            return
            
        try:
            self._lib = ctypes.CDLL(self.dll_path)
            self._lib.fetch_weights_to_l3.argtypes = [
                np.ctypeslib.ndpointer(dtype=np.int8, ndim=1, flags='C_CONTIGUOUS'),
                np.ctypeslib.ndpointer(dtype=np.int8, ndim=1, flags='C_CONTIGUOUS'),
                ctypes.c_size_t
            ]
            self._lib.fetch_weights_to_l3.restype = None
            logger.info("Intel UHD iGPU SYCL kernel loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SYCL kernel: {e}")
            
    def stage_layer_asynchronously(self, source_weights: np.ndarray, target_buffer: np.ndarray):
        """
        Dispatches the iGPU to copy weights into the target buffer (CPU L3 cache space).
        """
        if source_weights.size != target_buffer.size:
            raise ValueError("Source and target buffers must be the same size.")
            
        if self._lib:
            self._lib.fetch_weights_to_l3(source_weights, target_buffer, source_weights.nbytes)
        else:
            # Simulation mode: standard NumPy copy
            np.copyto(target_buffer, source_weights)
