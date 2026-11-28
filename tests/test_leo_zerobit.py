"""
tests/test_leo_zerobit.py

Verification suite for LEO-ZeroBit:
Tile-Group-Major Sparse Ternary {-1, 0, +1} VPSHUFB GEMV Engine.
Target Hardware: Intel Core i5-12450H (AVX2) + Intel UHD iGPU (OpenCL).
"""

import ctypes
import os
import sys
import numpy as np
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ZEROBIT_DIR = REPO_ROOT / "zerobit"
if str(ZEROBIT_DIR) not in sys.path:
    sys.path.insert(0, str(ZEROBIT_DIR))

from run_leo_zerobit_proof import (
    compile_kernel,
    pack_tile_group_major,
    sha256_arr,
    TILE_M,
    C_LIB,
)


@pytest.fixture(scope="module")
def zerobit_lib():
    compile_kernel()
    lib = ctypes.CDLL(str(C_LIB))
    lib.leo_zerobit_is_avx2.restype = ctypes.c_int
    lib.leo_zerobit_gemv_tiles.argtypes = [
        ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_int16),
        ctypes.POINTER(ctypes.c_int32),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]
    lib.leo_zerobit_gemv_tiles.restype = ctypes.c_int
    return lib


def test_zerobit_compilation_and_avx2(zerobit_lib):
    """Verify kernel compiles with AVX2 VPSHUFB support."""
    is_avx2 = zerobit_lib.leo_zerobit_is_avx2()
    assert is_avx2 == 1, "Expected AVX2 kernel support"


def test_zerobit_dense_exact_integer_parity(zerobit_lib):
    """Verify 0 integer error and SHA-256 bit-exact match on 100% dense random ternary matrix."""
    m, k = 1024, 1024
    total_tiles = m // TILE_M

    rng = np.random.default_rng(101)
    w_tern = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(m, k))
    packed_w = pack_tile_group_major(w_tern)
    x_dense = rng.integers(-60, 61, size=(k,), dtype=np.int16)

    y_gt = (w_tern.astype(np.int32) @ x_dense.astype(np.int32)).astype(np.int32)
    y_out = np.zeros((m,), dtype=np.int32)

    p_w = packed_w.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
    p_x = x_dense.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
    p_y = y_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

    rc = zerobit_lib.leo_zerobit_gemv_tiles(p_w, p_x, p_y, m, k, 0, total_tiles, 0)
    assert rc >= 0, f"Error in kernel: {rc}"

    assert np.array_equal(y_out, y_gt)
    assert float(np.max(np.abs(y_out - y_gt))) == 0.0
    assert sha256_arr(y_out) == sha256_arr(y_gt)


def test_zerobit_sparse_activation_skipping(zerobit_lib):
    """Verify 85% sparse activation skipping reads only active slabs with 0 error."""
    m, k = 1024, 1024
    total_tiles = m // TILE_M
    groups = k // 4

    rng = np.random.default_rng(202)
    w_tern = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(m, k))
    packed_w = pack_tile_group_major(w_tern)

    x_sparse = np.zeros((k,), dtype=np.int16)
    active_g_idx = rng.choice(groups, size=int(groups * 0.15), replace=False)
    for g in active_g_idx:
        x_sparse[4 * g : 4 * g + 4] = rng.integers(-60, 61, size=(4,), dtype=np.int16)

    y_gt = (w_tern.astype(np.int32) @ x_sparse.astype(np.int32)).astype(np.int32)
    y_out = np.zeros((m,), dtype=np.int32)

    p_w = packed_w.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
    p_x = x_sparse.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
    p_y = y_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

    active_g = zerobit_lib.leo_zerobit_gemv_tiles(p_w, p_x, p_y, m, k, 0, total_tiles, 0)
    assert active_g == len(active_g_idx)
    assert np.array_equal(y_out, y_gt)
    assert float(np.max(np.abs(y_out - y_gt))) == 0.0


def test_zerobit_persistent_membrane_delta_accumulation(zerobit_lib):
    """Verify persistent-membrane delta accumulation with large int16 split chunks."""
    m, k = 1024, 1024
    total_tiles = m // TILE_M
    groups = k // 4

    rng = np.random.default_rng(303)
    w_tern = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(m, k))
    packed_w = pack_tile_group_major(w_tern)
    x_dense = rng.integers(-60, 61, size=(k,), dtype=np.int16)

    y_prev = (w_tern.astype(np.int32) @ x_dense.astype(np.int32)).astype(np.int32)
    x_next = x_dense.copy()
    changed_g = rng.choice(groups, size=int(groups * 0.05), replace=False)
    for g in changed_g:
        x_next[4 * g : 4 * g + 4] = rng.integers(-60, 61, size=(4,), dtype=np.int16)

    delta_x = (x_next - x_dense).astype(np.int16)
    y_target = (w_tern.astype(np.int32) @ x_next.astype(np.int32)).astype(np.int32)

    y_out = y_prev.copy()
    p_w = packed_w.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
    p_dx = delta_x.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
    p_y = y_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

    # accumulate=1
    rc = zerobit_lib.leo_zerobit_gemv_tiles(p_w, p_dx, p_y, m, k, 0, total_tiles, 1)
    assert rc >= 0

    assert np.array_equal(y_out, y_target)
    assert float(np.max(np.abs(y_out - y_target))) == 0.0
    assert sha256_arr(y_out) == sha256_arr(y_target)
