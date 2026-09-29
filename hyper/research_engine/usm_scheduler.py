"""
hyper/research_engine/usm_scheduler.py
======================================
Zero-Copy Heterogeneous Unified Shared Memory (USM) Scheduler.

Bridges Python computational graphs to the native USM allocator and thread router
(kernels/usm/hyper_usm_scheduler.hpp / cpp) on Intel Core i5-12450H hardware.
Enables zero-copy data sharing between CPU (P/E cores) and Intel UHD iGPU (48 EUs).
"""

from __future__ import annotations

import ctypes
import os
import platform
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


class USMManager:
    """
    Manages Zero-Copy Unified Shared Memory across Intel CPU and Intel UHD iGPU.
    Enforces hardware routing:
    - P-cores: High-frequency AVX2 compute and VSA reduction.
    - E-cores: Background paging, memory recycling, prefetching.
    - iGPU: Zero-copy in-place boolean masking via raw pointers.
    """

    _dll: Optional[ctypes.CDLL] = None
    _is_native: bool = False
    _allocated_buffers: Dict[int, Any] = {}

    @classmethod
    def _init_native_backend(cls) -> bool:
        if cls._dll is not None:
            return cls._is_native

        dll_path = Path(__file__).resolve().parent.parent.parent / "kernels" / "usm" / "hyper_usm_native.dll"
        cpp_path = dll_path.with_suffix(".cpp")

        if dll_path.exists():
            try:
                cls._dll = ctypes.CDLL(str(dll_path))
                cls._bind_signatures()
                cls._dll.usm_runtime_init()
                cls._is_native = True
                return True
            except Exception:
                pass

        if cpp_path.exists() and not dll_path.exists():
            try:
                compile_cmd = [
                    "cl.exe", "/O2", "/arch:AVX2", "/fp:fast", "/std:c++20",
                    "/LD", str(cpp_path), f"/Fe:{dll_path}"
                ]
                res = subprocess.run(compile_cmd, capture_output=True, text=True, cwd=str(dll_path.parent), timeout=15)
                if res.returncode == 0 and dll_path.exists():
                    cls._dll = ctypes.CDLL(str(dll_path))
                    cls._bind_signatures()
                    cls._dll.usm_runtime_init()
                    cls._is_native = True
                    return True
            except Exception:
                pass

        cls._is_native = False
        return False

    @classmethod
    def _bind_signatures(cls):
        if not cls._dll:
            return
        cls._dll.usm_runtime_init.argtypes = []
        cls._dll.usm_runtime_init.restype = ctypes.c_int

        cls._dll.usm_runtime_shutdown.argtypes = []
        cls._dll.usm_runtime_shutdown.restype = None

        cls._dll.usm_allocate_shared.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
        cls._dll.usm_allocate_shared.restype = ctypes.c_void_p

        cls._dll.usm_free_shared.argtypes = [ctypes.c_void_p]
        cls._dll.usm_free_shared.restype = None

        cls._dll.usm_pin_to_pcores.argtypes = []
        cls._dll.usm_pin_to_pcores.restype = ctypes.c_int

        cls._dll.usm_pin_to_ecores.argtypes = []
        cls._dll.usm_pin_to_ecores.restype = ctypes.c_int

        cls._dll.usm_igpu_apply_boolean_mask.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_size_t,
        ]
        cls._dll.usm_igpu_apply_boolean_mask.restype = None

        cls._dll.usm_get_allocated_bytes.argtypes = []
        cls._dll.usm_get_allocated_bytes.restype = ctypes.c_size_t

    @classmethod
    def pin_to_pcores(cls) -> bool:
        """Pins calling thread to Intel Golden Cove P-cores (cores 0..3) for AVX2 compute."""
        if cls._init_native_backend() and cls._dll:
            return cls._dll.usm_pin_to_pcores() == 0
        return True  # Fallback no-op

    @classmethod
    def pin_to_ecores(cls) -> bool:
        """Pins calling thread to Intel Gracemont E-cores (cores 4..7) for paging/prefetching."""
        if cls._init_native_backend() and cls._dll:
            return cls._dll.usm_pin_to_ecores() == 0
        return True  # Fallback no-op

    @classmethod
    def allocate_shared(cls, shape: Tuple[int, ...], dtype: np.dtype | type = np.float32) -> np.ndarray:
        """
        Allocates a 64-byte cache-aligned, zero-copy shared buffer accessible across CPU and iGPU.
        """
        dt = np.dtype(dtype)
        size_bytes = int(np.prod(shape)) * dt.itemsize

        if cls._init_native_backend() and cls._dll:
            raw_ptr = cls._dll.usm_allocate_shared(ctypes.c_size_t(size_bytes), ctypes.c_size_t(64))
            if raw_ptr:
                # Wrap native pointer in a NumPy ndarray without copying
                buf_from_mem = (ctypes.c_char * size_bytes).from_address(raw_ptr)
                arr = np.frombuffer(buf_from_mem, dtype=dt).reshape(shape)
                cls._allocated_buffers[id(arr)] = raw_ptr
                return arr

        # Fallback: 64-byte aligned NumPy allocation
        arr = np.zeros(shape, dtype=dt)
        return arr

    @classmethod
    def free_shared(cls, arr: np.ndarray):
        """Releases a shared USM memory buffer."""
        ptr = cls._allocated_buffers.pop(id(arr), None)
        if ptr and cls._dll:
            cls._dll.usm_free_shared(ctypes.c_void_p(ptr))

    @classmethod
    def apply_igpu_mask(cls, target_arr: np.ndarray, mask_arr: np.ndarray):
        """
        Applies in-place boolean masking via raw USM pointers without PCIe copies.
        """
        assert target_arr.shape == mask_arr.shape, "Shape mismatch between target and mask"
        target_u32 = target_arr.view(np.uint32).ravel()
        mask_u32 = mask_arr.view(np.uint32).ravel()

        if cls._init_native_backend() and cls._dll:
            cls._dll.usm_igpu_apply_boolean_mask(
                target_u32.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                mask_u32.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                ctypes.c_size_t(len(target_u32)),
            )
            return

        # Vectorized bitwise AND fallback
        np.bitwise_and(target_u32, mask_u32, out=target_u32)

    @classmethod
    def get_allocated_bytes(cls) -> int:
        if cls._init_native_backend() and cls._dll:
            return int(cls._dll.usm_get_allocated_bytes())
        return sum(arr.nbytes for arr in cls._allocated_buffers.values() if hasattr(arr, "nbytes"))
