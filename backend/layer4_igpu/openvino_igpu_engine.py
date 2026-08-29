"""
backend/layer4_igpu/openvino_igpu_engine.py
===========================================
LEO Pillar 4: OpenVINO Intel iGPU Execution Engine
Discovers Intel UHD Graphics (48EU Xe architecture) and compiles computational graphs
for hardware execution on the GPU.0 device or optimized multi-threaded AVX2 CPU.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger("OpenVINOiGPU")

try:
    import openvino as ov
    from openvino.runtime import opset10 as ops
    HAS_OPENVINO = True
except Exception as e:
    HAS_OPENVINO = False
    logger.debug(f"OpenVINO import skipped: {e}")


class OpenVINOiGPUEngine:
    """
    Genuine OpenVINO execution dispatcher targeting Intel UHD Graphics (GPU.0) and CPU.
    """

    def __init__(self):
        self.device = "CPU"
        self.core: Optional[Any] = None
        self.available_devices = []
        self.is_gpu_available = False

        self._init_openvino()

    def _init_openvino(self):
        """Initializes OpenVINO Core and queries available physical execution targets."""
        if HAS_OPENVINO:
            try:
                self.core = ov.Core()
                self.available_devices = self.core.available_devices
                logger.info(f"[OpenVINO iGPU] Detected hardware devices: {self.available_devices}")

                if "GPU" in self.available_devices:
                    self.device = "GPU"
                    self.is_gpu_available = True
                    logger.info("[OpenVINO iGPU] Targeted Intel UHD Graphics Xe iGPU (GPU.0).")
                else:
                    self.device = "CPU"
                    logger.info("[OpenVINO iGPU] GPU not in device list, using multi-threaded CPU.")
            except Exception as e:
                logger.warning(f"[OpenVINO iGPU] Initialization notice: {e}")
                self.device = "CPU"

    def execute_matmul_on_target(self, A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes matrix multiplication on Intel UHD iGPU via OpenVINO compiled model,
        or optimized NumPy CPU fallback.
        """
        t0 = time.perf_counter()
        A_f32 = np.ascontiguousarray(A, dtype=np.float32)
        B_f32 = np.ascontiguousarray(B, dtype=np.float32)

        if HAS_OPENVINO and self.core is not None:
            try:
                # Build an OpenVINO computation graph
                param_a = ops.parameter(A_f32.shape, dtype=np.float32, name="A")
                param_b = ops.parameter(B_f32.shape, dtype=np.float32, name="B")
                matmul_node = ops.matmul(param_a, param_b, transpose_a=False, transpose_b=False)
                model = ov.Model([matmul_node], [param_a, param_b], "MatMul_Graph")

                compiled_model = self.core.compile_model(model, self.device)
                infer_request = compiled_model.create_infer_request()
                res = infer_request.infer({param_a: A_f32, param_b: B_f32})
                out = list(res.values())[0]

                lat_ms = (time.perf_counter() - t0) * 1000.0
                telemetry = {
                    "device": self.device,
                    "status": "success",
                    "compute_offloaded": self.is_gpu_available,
                    "execution_time_ms": round(lat_ms, 3),
                    "openvino_compiled": True
                }
                return out, telemetry
            except Exception as e:
                logger.warning(f"[OpenVINO iGPU] Graph execution fallback: {e}")

        # Native CPU SIMD execution
        out = A_f32 @ B_f32
        lat_ms = (time.perf_counter() - t0) * 1000.0
        telemetry = {
            "device": "CPU_AVX2",
            "status": "success",
            "compute_offloaded": False,
            "execution_time_ms": round(lat_ms, 3),
            "openvino_compiled": False
        }
        return out, telemetry

    def get_hardware_info(self) -> Dict[str, Any]:
        return {
            "openvino_installed": HAS_OPENVINO,
            "active_device": self.device,
            "gpu_detected": self.is_gpu_available,
            "available_devices": self.available_devices
        }
