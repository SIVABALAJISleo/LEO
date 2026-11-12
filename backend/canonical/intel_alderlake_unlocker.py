"""
backend/canonical/intel_alderlake_unlocker.py
=============================================
Runtime pre-execution unlocker for Intel Core i5-12450H + Intel UHD iGPU on Windows 11:
  1. Disables Windows 11 EcoQoS / Execution Speed Power Throttling via SetProcessInformation.
  2. Elevates process priority to HIGH_PRIORITY_CLASS for ThreadDirector P-core preference.
  3. Unlocks 1.0 ms NT Kernel timer resolution via winmm.timeBeginPeriod(1).
  4. Allocates 4096-byte page-aligned Zero-Copy Unified Shared Memory host buffers for Intel UHD.
  5. Dispatches AVX-VNNI INT8 GEMV on Alder Lake CPU P-cores.
"""

from __future__ import annotations

import ctypes
import os
import sys
import time
from typing import Dict, Any, Tuple, Optional
import numpy as np


class PROCESS_POWER_THROTTLING_STATE(ctypes.Structure):
    _fields_ = [
        ("Version", ctypes.c_ulong),
        ("ControlMask", ctypes.c_ulong),
        ("StateMask", ctypes.c_ulong),
    ]


def unlock_windows11_alderlake_throttles() -> Dict[str, Any]:
    """
    Disables Windows 11 EcoQoS execution throttling, elevates process priority
    to HIGH_PRIORITY_CLASS for ThreadDirector P-core affinity, and unlocks 1.0 ms
    NT kernel timer resolution.
    """
    status: Dict[str, Any] = {
        "platform": sys.platform,
        "ecoqos_throttle_disabled": False,
        "high_priority_enabled": False,
        "timer_1ms_unlocked": False,
    }

    if sys.platform != "win32":
        return status

    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        h_process = kernel32.GetCurrentProcess()

        # Disable PROCESS_POWER_THROTTLING_EXECUTION_SPEED (0x1) & IGNORE_TIMER_RESOLUTION (0x4)
        process_power_throttling = 4
        throttling_state = PROCESS_POWER_THROTTLING_STATE(
            Version=1,
            ControlMask=0x1 | 0x4,
            StateMask=0x0,  # Turn OFF throttling
        )
        kernel32.SetProcessInformation.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_ulong,
        ]
        kernel32.SetProcessInformation.restype = ctypes.c_int
        res = kernel32.SetProcessInformation(
            h_process,
            process_power_throttling,
            ctypes.byref(throttling_state),
            ctypes.sizeof(throttling_state),
        )
        status["ecoqos_throttle_disabled"] = bool(res != 0)

        # Elevate to HIGH_PRIORITY_CLASS (0x80)
        high_priority_class = 0x00000080
        kernel32.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        kernel32.SetPriorityClass.restype = ctypes.c_int
        prio_res = kernel32.SetPriorityClass(h_process, high_priority_class)
        status["high_priority_enabled"] = bool(prio_res != 0)

        # Unlock 1.0 ms NT Kernel timer resolution
        winmm = ctypes.windll.winmm
        winmm.timeBeginPeriod.argtypes = [ctypes.c_uint]
        winmm.timeBeginPeriod.restype = ctypes.c_uint
        timer_res = winmm.timeBeginPeriod(1)
        status["timer_1ms_unlocked"] = bool(timer_res == 0)

    except Exception as exc:
        status["error"] = str(exc)

    return status


def allocate_zero_copy_page_aligned_buffer(
    shape: Tuple[int, ...], dtype: np.dtype = np.float32
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Allocates a 4096-byte page-aligned NumPy array for Intel UHD OpenCL Zero-Copy USM.
    Guarantees both 4096-byte page boundary alignment and 64-byte cacheline alignment.
    """
    dt = np.dtype(dtype)
    num_elements = int(np.prod(shape))
    nbytes = num_elements * dt.itemsize

    raw = np.empty(nbytes + 4096, dtype=np.uint8)
    base_addr = int(raw.ctypes.data)
    offset = (4096 - (base_addr % 4096)) % 4096

    aligned = raw[offset : offset + nbytes].view(dtype=dt).reshape(shape)
    aligned_addr = int(aligned.ctypes.data)

    return aligned, {
        "virtual_address_hex": hex(aligned_addr),
        "page_aligned_4096": bool((aligned_addr % 4096) == 0),
        "cacheline_aligned_64": bool((aligned_addr % 64) == 0),
        "allocated_bytes": nbytes,
    }


_KEYSTONE_DLL: Optional[ctypes.CDLL] = None
_VNNI_FN = None


def _get_keystone_library() -> Optional[ctypes.CDLL]:
    global _KEYSTONE_DLL, _VNNI_FN
    if _KEYSTONE_DLL is not None:
        return _KEYSTONE_DLL

    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hardware", "keystone_engine.dll"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hardware", "keystone_engine.so"),
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                lib = ctypes.CDLL(p)
                if hasattr(lib, "leo_avx_vnni_int8_gemv"):
                    lib.leo_avx_vnni_int8_gemv.argtypes = [
                        ctypes.POINTER(ctypes.c_uint8),
                        ctypes.POINTER(ctypes.c_int8),
                        ctypes.POINTER(ctypes.c_int32),
                        ctypes.c_int,
                        ctypes.c_int,
                    ]
                    lib.leo_avx_vnni_int8_gemv.restype = None
                    _VNNI_FN = lib.leo_avx_vnni_int8_gemv
                _KEYSTONE_DLL = lib
                return _KEYSTONE_DLL
            except Exception:
                pass
    return None


def execute_avx_vnni_gemv(A_u8: np.ndarray, B_s8: np.ndarray) -> np.ndarray:
    """
    Executes INT8 GEMV using Intel Alder Lake AVX-VNNI hardware instructions
    (_mm256_dpbusd_epi32) if compiled native library is available, or exact
    vectorized NumPy fallback.
    
    A_u8: Unsigned INT8 vector of length K (or shape (1, K)).
    B_s8: Signed INT8 matrix of shape (M, K).
    Returns: Signed INT32 accumulator vector of shape (M,).
    """
    _get_keystone_library()

    A_flat = np.ascontiguousarray(A_u8.reshape(-1), dtype=np.uint8)
    B_cont = np.ascontiguousarray(B_s8, dtype=np.int8)

    if B_cont.ndim != 2:
        raise ValueError(f"B_s8 must be a 2D matrix, got shape {B_cont.shape}")

    m_dim, k_dim = B_cont.shape
    if A_flat.shape[0] != k_dim:
        raise ValueError(f"Dimension mismatch: A_u8 length {A_flat.shape[0]} != B_s8 cols {k_dim}")

    C_i32 = np.zeros(m_dim, dtype=np.int32)

    if _VNNI_FN is not None:
        _VNNI_FN(
            A_flat.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            B_cont.ctypes.data_as(ctypes.POINTER(ctypes.c_int8)),
            C_i32.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            ctypes.c_int(m_dim),
            ctypes.c_int(k_dim),
        )
    else:
        # Fallback to exact algebraic integer matmul
        C_i32 = (B_cont.astype(np.int32) @ A_flat.astype(np.int32)).astype(np.int32)

    return C_i32


def benchmark_intel_alderlake_acceleration() -> Dict[str, Any]:
    """
    Executes end-to-end hardware acceleration benchmark on Intel Alder Lake:
      1. Windows 11 EcoQoS throttle bypass and 1.0 ms timer lock.
      2. 4096-byte page-aligned Zero-Copy USM buffer allocation.
      3. Alder Lake AVX-VNNI INT8 GEMV throughput and exact numerical validation.
    """
    unlock_meta = unlock_windows11_alderlake_throttles()

    # Zero-Copy buffer allocation test
    buf, buf_meta = allocate_zero_copy_page_aligned_buffer((1024, 1024), dtype=np.float32)

    # AVX-VNNI INT8 GEMV test
    rng = np.random.default_rng(2026)
    m_size = 256
    k_size = 512
    a_u8 = rng.integers(0, 256, size=k_size, dtype=np.uint8)
    b_s8 = rng.integers(-128, 127, size=(m_size, k_size), dtype=np.int8)

    # Warmup
    for _ in range(5):
        _ = execute_avx_vnni_gemv(a_u8, b_s8)

    # Timed execution
    iters = 20
    t_start = time.perf_counter()
    for _ in range(iters):
        c_res = execute_avx_vnni_gemv(a_u8, b_s8)
    t_total = time.perf_counter() - t_start
    avg_latency_ms = float((t_total / iters) * 1000.0)

    # Numerical verification against exact reference
    ref_res = (b_s8.astype(np.int32) @ a_u8.astype(np.int32)).astype(np.int32)
    exact_match = bool(np.array_equal(c_res, ref_res))

    c_norm = float(np.linalg.norm(c_res))
    ref_norm = float(np.linalg.norm(ref_res))
    if c_norm > 0 and ref_norm > 0:
        cos_similarity = float(np.dot(c_res.astype(np.float64), ref_res.astype(np.float64)) / (c_norm * ref_norm))
    else:
        cos_similarity = 1.0 if exact_match else 0.0

    ops_total = 2 * m_size * k_size
    gops_val = float(ops_total / (max(avg_latency_ms, 1e-6) * 1e6))

    all_passed = bool(
        buf_meta["page_aligned_4096"]
        and buf_meta["cacheline_aligned_64"]
        and exact_match
        and (cos_similarity >= 0.999)
    )

    return {
        "unlock_meta": unlock_meta,
        "page_aligned_4096": buf_meta["page_aligned_4096"],
        "cacheline_aligned_64": buf_meta["cacheline_aligned_64"],
        "virtual_address_hex": buf_meta["virtual_address_hex"],
        "exact_integer_match": exact_match,
        "cosine_similarity": cos_similarity,
        "latency_ms": avg_latency_ms,
        "throughput_gops": gops_val,
        "native_kernel_active": bool(_VNNI_FN is not None),
        "passed": all_passed,
    }
