"""
hyper_x/cpce/backend_registry.py
================================
Truthful Device and Backend Registry for CPCE.
Discovers and manages physical host execution backends at runtime:
- CPU AVX2 (OpenBLAS / NumPy baseline)
- Intel UHD Graphics iGPU via OpenVINO GPU Device Runtime
- Local quantized GGUF language model via llama-cpp-python
Strictly prevents claiming unverified or unavailable accelerators.
"""

from __future__ import annotations

import dataclasses
import os
import platform
from typing import Any, Dict, List, Optional

try:
    import openvino as ov
    _HAS_OPENVINO = True
except ImportError:
    _HAS_OPENVINO = False

try:
    import llama_cpp
    _HAS_LLAMA_CPP = True
except ImportError:
    _HAS_LLAMA_CPP = False


@dataclasses.dataclass
class BackendDescriptor:
    backend_id: str
    device_name: str
    is_available: bool
    is_accelerator: bool
    supported_ops: List[str]
    supported_dtypes: List[str]
    max_memory_mb: float
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class CPCEBackendRegistry:
    """Discovers and manages hardware backends truthfully."""

    def __init__(self):
        self._backends: Dict[str, BackendDescriptor] = {}
        self._discover_backends()

    def _discover_backends(self):
        proc = platform.processor() or "Host CPU (x86_64)"

        # 1. Host CPU Baseline (Always Available)
        self._backends["CPU"] = BackendDescriptor(
            backend_id="CPU",
            device_name=f"Host CPU ({proc})",
            is_available=True,
            is_accelerator=False,
            supported_ops=["MATMUL", "ADD", "SUB", "MUL", "DIV", "DOT", "SCALE", "HORNER_EVAL", "SPARSE_MATMUL"],
            supported_dtypes=["float32", "float64", "int32", "int64"],
            max_memory_mb=14000.0,
            notes="AVX2 OpenBLAS multi-threaded execution.",
        )

        # 2. Genuine Intel UHD Graphics iGPU via OpenVINO
        igpu_available = False
        igpu_device_name = "Intel UHD Graphics (Not Detected)"
        if _HAS_OPENVINO:
            try:
                core = ov.Core()
                if "GPU" in core.available_devices:
                    igpu_available = True
                    igpu_device_name = core.get_property("GPU", "FULL_DEVICE_NAME")
            except Exception as e:
                igpu_available = False
                igpu_device_name = f"OpenVINO GPU Init Failed: {e}"

        self._backends["INTEL_UHD_IGPU"] = BackendDescriptor(
            backend_id="INTEL_UHD_IGPU",
            device_name=igpu_device_name,
            is_available=igpu_available,
            is_accelerator=True,
            supported_ops=["MATMUL", "CONV2D"],
            supported_dtypes=["float32", "float16"],
            max_memory_mb=4096.0,
            notes="Intel Gen12.2 Xe-LP (48 EUs) via OpenVINO GPU runtime.",
        )

        # 3. Local GGUF LLM Engine via llama_cpp
        model_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "models", "qwen2.5-0.5b-instruct-q4_k_m.gguf")
        )
        model_on_disk = os.path.exists(model_path)
        llm_ready = _HAS_LLAMA_CPP and model_on_disk

        self._backends["LOCAL_GGUF_CPU"] = BackendDescriptor(
            backend_id="LOCAL_GGUF_CPU",
            device_name=f"Host CPU ({proc}) Local GGUF",
            is_available=llm_ready,
            is_accelerator=False,
            supported_ops=["LLM_GENERATE"],
            supported_dtypes=["q4_k_m"],
            max_memory_mb=1024.0,
            notes="100% local Qwen2.5-0.5B GGUF inference (zero cloud/paid API).",
        )

    def get_backend(self, backend_id: str) -> Optional[BackendDescriptor]:
        return self._backends.get(backend_id)

    def is_available(self, backend_id: str) -> bool:
        b = self.get_backend(backend_id)
        return b is not None and b.is_available

    def list_backends(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self._backends.values()]
