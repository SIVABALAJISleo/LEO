"""
run_leo_zerobit_proof.py

Standalone 60-Second Open-Source Proof for LEO-ZeroBit
Tests ONE 16.77M-parameter ternary layer (4096 x 4096) on your local hardware:
  - Baseline: Dense FP32 BLAS GEMV (64.0 MB read per token)
  - Mode 1 (Adversarial 0% Sparsity / Dense Ternary): 4.0 MB read, 0 multipliers, 0 error
  - Mode 2 (85% Sparse ReLU2/SwiGLU Activations): ~0.6 MB read, 0 multipliers, 0 error
  - Mode 3 (95% Persistent-Membrane Delta Stream): ~0.2 MB read, 0 multipliers, 0 error
  - Mode 4 (Live Simultaneous CPU AVX2 + Intel UHD OpenCL Heterogeneous Split): 0 error

Zero hardcoded RTX numbers. Zero fake iGPU timings. Hard exit(1) on any error != 0.
"""

from __future__ import annotations
import concurrent.futures
import ctypes
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

TILE_M = 512
ROOT = Path(__file__).resolve().parent
C_SRC = ROOT / "leo_zerobit_kernel.c"
LIB_EXT = ".dll" if platform.system() == "Windows" else ".so"
C_LIB = ROOT / f"leo_zerobit_kernel{LIB_EXT}"
REPORT_OUT = ROOT / "leo_zerobit_verified_proof.json"


def sha256_arr(arr: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest()


def compile_kernel() -> Dict[str, Any]:
    if not C_SRC.exists():
        raise FileNotFoundError(f"Missing {C_SRC}")

    # Auto-add embedded w64devkit MinGW toolchain to PATH if available
    embedded_bin = ROOT.parent / "backend" / "hardware" / ".compiler" / "w64devkit" / "bin"
    if embedded_bin.exists():
        bin_str = str(embedded_bin)
        if bin_str not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_str + os.pathsep + os.environ.get("PATH", "")

    cmds: List[Tuple[str, List[str]]] = []
    if shutil.which("gcc"):
        cmds.append(("gcc+avx2+omp", ["gcc", "-O3", "-mavx2", "-fopenmp", "-shared", "-fPIC", str(C_SRC), "-o", str(C_LIB)]))
        cmds.append(("gcc+avx2", ["gcc", "-O3", "-mavx2", "-shared", "-fPIC", str(C_SRC), "-o", str(C_LIB)]))
    if shutil.which("clang"):
        cmds.append(("clang+avx2+omp", ["clang", "-O3", "-mavx2", "-fopenmp", "-shared", "-fPIC", str(C_SRC), "-o", str(C_LIB)]))
        cmds.append(("clang+avx2", ["clang", "-O3", "-mavx2", "-shared", "-fPIC", str(C_SRC), "-o", str(C_LIB)]))
    if shutil.which("cl"):
        cmds.append(("msvc+avx2+omp", ["cl", "/nologo", "/O2", "/arch:AVX2", "/openmp", "/LD", str(C_SRC), f"/Fe:{C_LIB}"]))
        cmds.append(("msvc+avx2", ["cl", "/nologo", "/O2", "/arch:AVX2", "/LD", str(C_SRC), f"/Fe:{C_LIB}"]))

    last_err = ""
    used = None
    for name, cmd in cmds:
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 0 and C_LIB.exists():
            used = name
            break
        last_err = (p.stderr or p.stdout).strip()[:400]

    if used is None:
        raise RuntimeError(f"C compiler required (gcc/clang/cl). Last error: {last_err}")

    vpshufb_in_asm = False
    if shutil.which("objdump"):
        dis = subprocess.run(["objdump", "-d", str(C_LIB)], capture_output=True, text=True)
        vpshufb_in_asm = ("vpshufb" in dis.stdout.lower())

    return {
        "compiler": used,
        "binary": str(C_LIB),
        "vpshufb_verified_in_disassembly": vpshufb_in_asm,
    }


def pack_tile_group_major(w_tern: np.ndarray) -> np.ndarray:
    """Packs ternary weights {-1, 0, +1} (M, K) into [M/512, K/4, 512] uint8."""
    m, k = w_tern.shape
    assert m % TILE_M == 0 and k % 4 == 0
    u = (w_tern + 1).astype(np.uint8)
    u = u.reshape(m // TILE_M, TILE_M, k // 4, 4).transpose(0, 2, 1, 3)
    lo = u[..., 0] + np.uint8(3) * u[..., 1]
    hi = u[..., 2] + np.uint8(3) * u[..., 3]
    return np.ascontiguousarray((lo | (hi << np.uint8(4))).reshape(-1), dtype=np.uint8)


def build_chunks_for_opencl(x_i16: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Builds identical active chunks + 16-byte LUTs for the OpenCL iGPU kernel."""
    groups = x_i16.shape[0] // 4
    active_g: List[int] = []
    luts_lo: List[np.ndarray] = []
    luts_hi: List[np.ndarray] = []

    t0_grid = np.array([-1, 0, 1, -1, 0, 1, -1, 0, 1], dtype=np.int16)
    t1_grid = np.array([-1, -1, -1, 0, 0, 0, 1, 1, 1], dtype=np.int16)

    for g in range(groups):
        r = [int(x_i16[4 * g + i]) for i in range(4)]
        if r[0] == 0 and r[1] == 0 and r[2] == 0 and r[3] == 0:
            continue
        while r[0] != 0 or r[1] != 0 or r[2] != 0 or r[3] != 0:
            c = [max(-63, min(63, v)) for v in r]
            r = [r[i] - c[i] for i in range(4)]
            lo = np.zeros(16, dtype=np.int8)
            hi = np.zeros(16, dtype=np.int8)
            lo[:9] = (t0_grid * c[0] + t1_grid * c[1]).astype(np.int8)
            hi[:9] = (t0_grid * c[2] + t1_grid * c[3]).astype(np.int8)
            active_g.append(g)
            luts_lo.append(lo)
            luts_hi.append(hi)

    if not active_g:
        return (
            np.zeros((1,), dtype=np.int32),
            np.zeros((16,), dtype=np.int8),
            np.zeros((16,), dtype=np.int8),
        )
    return (
        np.ascontiguousarray(active_g, dtype=np.int32),
        np.ascontiguousarray(np.concatenate(luts_lo), dtype=np.int8),
        np.ascontiguousarray(np.concatenate(luts_hi), dtype=np.int8),
    )


def run_opencl_igpu_and_hybrid_split(
    lib: ctypes.CDLL,
    packed_w: np.ndarray,
    x_i16: np.ndarray,
    y_exact: np.ndarray,
    m: int,
    k: int,
    igpu_tiles: int = 3,
) -> Dict[str, Any]:
    """
    Runs the EXACT SAME Tile-Group-Major ternary buffer on:
      (A) Pure Intel UHD iGPU via OpenCL zero-copy CL_MEM_USE_HOST_PTR
      (B) Simultaneous CPU AVX2 (tiles 0..split-1) + Intel UHD iGPU (tiles split..end)
    """
    try:
        import pyopencl as cl  # type: ignore
    except ImportError:
        return {
            "igpu_dispatched": False,
            "status": "PYOPENCL_NOT_INSTALLED_RUN_PIP_INSTALL_PYOPENCL",
            "igpu_kernel_ms": 0.0,
            "hybrid_simultaneous_ms": 0.0,
            "verified_exact": False,
        }

    gpu_dev = None
    for plat in cl.get_platforms():
        for d in plat.get_devices(device_type=cl.device_type.GPU):
            if "intel" in d.vendor.lower() or "uhd" in d.name.lower() or gpu_dev is None:
                gpu_dev = d
                break
        if gpu_dev is not None:
            break

    if gpu_dev is None:
        return {
            "igpu_dispatched": False,
            "status": "NO_OPENCL_GPU_DRIVER_DETECTED",
            "igpu_kernel_ms": 0.0,
            "hybrid_simultaneous_ms": 0.0,
            "verified_exact": False,
        }

    total_tiles = m // TILE_M
    groups = k // 4
    active_g, luts_lo, luts_hi = build_chunks_for_opencl(x_i16)
    num_chunks = int(active_g.shape[0])

    ctx = cl.Context([gpu_dev])
    queue = cl.CommandQueue(ctx, properties=cl.command_queue_properties.PROFILING_ENABLE)
    mf = cl.mem_flags

    prg = cl.Program(
        ctx,
        """
        __kernel void leo_zerobit_ternary_lut(
            __global const uchar* packed_w,
            __global const int*   active_g,
            __global const char*  luts_lo,
            __global const char*  luts_hi,
            __global int*         out,
            const int             groups,
            const int             num_chunks,
            const int             tile_offset)
        {
            int lid = get_global_id(0);
            int tile = tile_offset + (lid >> 9);
            int tm   = lid & 511;
            int base = (tile * groups) * 512 + tm;

            int acc = 0;
            for (int c = 0; c < num_chunks; ++c) {
                int g = active_g[c];
                uchar p = packed_w[base + (g << 9)];
                int lut_base = c << 4;
                acc += (int)luts_lo[lut_base + (p & 0x0F)]
                     + (int)luts_hi[lut_base + ((p >> 4) & 0x0F)];
            }
            out[(tile << 9) + tm] = acc;
        }
        """,
    ).build()

    buf_w = cl.Buffer(ctx, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=packed_w)
    buf_g = cl.Buffer(ctx, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=active_g)
    buf_lo = cl.Buffer(ctx, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=luts_lo)
    buf_hi = cl.Buffer(ctx, mf.READ_ONLY | mf.USE_HOST_PTR, hostbuf=luts_hi)

    # (A) Full iGPU run
    out_igpu = np.zeros((m,), dtype=np.int32)
    buf_out = cl.Buffer(ctx, mf.WRITE_ONLY | mf.USE_HOST_PTR, hostbuf=out_igpu)
    # Warm JIT once
    prg.leo_zerobit_ternary_lut(
        queue, (m,), None, buf_w, buf_g, buf_lo, buf_hi, buf_out,
        np.int32(groups), np.int32(num_chunks), np.int32(0),
    ).wait()

    igpu_times = []
    for _ in range(5):
        evt = prg.leo_zerobit_ternary_lut(
            queue, (m,), None, buf_w, buf_g, buf_lo, buf_hi, buf_out,
            np.int32(groups), np.int32(num_chunks), np.int32(0),
        )
        evt.wait()
        igpu_times.append((evt.profile.end - evt.profile.start) / 1e6)
    cl.enqueue_copy(queue, out_igpu, buf_out).wait()
    igpu_err = int(np.max(np.abs(out_igpu - y_exact)))
    igpu_median_ms = float(np.median(igpu_times))

    # (B) Simultaneous CPU AVX2 (tiles 0..cpu_tiles-1) + Intel UHD iGPU (tiles cpu_tiles..total_tiles-1)
    cpu_tiles = max(1, total_tiles - igpu_tiles)
    gpu_rows = (total_tiles - cpu_tiles) * TILE_M
    out_hybrid = np.zeros((m,), dtype=np.int32)
    out_gpu_slice = np.zeros((m,), dtype=np.int32)
    buf_out_h = cl.Buffer(ctx, mf.WRITE_ONLY | mf.USE_HOST_PTR, hostbuf=out_gpu_slice)

    p_w = packed_w.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
    p_x = x_i16.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
    p_y = out_hybrid.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))

    hybrid_times = []
    for _ in range(5):
        t0 = time.perf_counter_ns()
        evt_h = prg.leo_zerobit_ternary_lut(
            queue, (gpu_rows,), None, buf_w, buf_g, buf_lo, buf_hi, buf_out_h,
            np.int32(groups), np.int32(num_chunks), np.int32(cpu_tiles),
        )
        queue.flush()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            fut = pool.submit(lib.leo_zerobit_gemv_tiles, p_w, p_x, p_y, m, k, 0, cpu_tiles, 0)
            evt_h.wait()
            cl.enqueue_copy(queue, out_gpu_slice, buf_out_h).wait()
            rc = fut.result()
            if rc < 0:
                raise RuntimeError(f"Hybrid CPU tile error: {rc}")
        out_hybrid[cpu_tiles * TILE_M :] = out_gpu_slice[cpu_tiles * TILE_M :]
        hybrid_times.append((time.perf_counter_ns() - t0) / 1e6)

    hybrid_err = int(np.max(np.abs(out_hybrid - y_exact)))
    hybrid_sha_match = (sha256_arr(out_hybrid) == sha256_arr(y_exact))

    return {
        "igpu_dispatched": True,
        "device_name": gpu_dev.name.strip(),
        "compute_units": int(gpu_dev.max_compute_units),
        "igpu_full_median_ms": round(igpu_median_ms, 3),
        "igpu_max_int_error": igpu_err,
        "hybrid_split_tiles": f"CPU={cpu_tiles}/{total_tiles}, iGPU={total_tiles - cpu_tiles}/{total_tiles}",
        "hybrid_simultaneous_median_ms": round(float(np.median(hybrid_times)), 3),
        "hybrid_max_int_error": hybrid_err,
        "hybrid_sha256_exact_match": hybrid_sha_match,
        "verified_exact": (igpu_err == 0 and hybrid_err == 0 and hybrid_sha_match and igpu_median_ms > 0.0),
    }


def main() -> int:
    m, k = 4096, 4096
    total_tiles = m // TILE_M
    groups = k // 4

    build_info = compile_kernel()
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
    avx2_active = bool(lib.leo_zerobit_is_avx2())

    rng = np.random.default_rng(20261128)
    # Realistic BitNet b1.58 ternary weight matrix {-1, 0, +1} (16.77M weights)
    w_tern = rng.choice(np.array([-1, 0, 1], dtype=np.int8), size=(m, k))
    w_fp32 = w_tern.astype(np.float32)
    packed_w = pack_tile_group_major(w_tern)

    # Dense FP32 BLAS baseline (reads 64.0 MB per token)
    x_dense = rng.integers(-60, 61, size=(k,), dtype=np.int16)
    x_fp32 = x_dense.astype(np.float32)
    _ = w_fp32 @ x_fp32  # warm allocator
    fp32_times = []
    for _ in range(10):
        t0 = time.perf_counter_ns()
        _ = w_fp32 @ x_fp32
        fp32_times.append((time.perf_counter_ns() - t0) / 1e6)
    fp32_ms = float(np.median(fp32_times))

    p_w = packed_w.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))

    def bench_cpu_mode(name: str, x_vec: np.ndarray, prev_y: Optional[np.ndarray] = None, x_full_ref: Optional[np.ndarray] = None) -> Dict[str, Any]:
        y_gt = (w_tern.astype(np.int32) @ (x_full_ref if x_full_ref is not None else x_vec).astype(np.int32)).astype(np.int32)
        ref_sha = sha256_arr(y_gt)

        y_out = np.zeros((m,), dtype=np.int32)
        p_x = x_vec.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
        p_y = y_out.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        acc_flag = 1 if prev_y is not None else 0

        times = []
        active_g = 0
        for _ in range(12):
            if prev_y is not None:
                np.copyto(y_out, prev_y)
            t0 = time.perf_counter_ns()
            active_g = lib.leo_zerobit_gemv_tiles(p_w, p_x, p_y, m, k, 0, total_tiles, acc_flag)
            times.append((time.perf_counter_ns() - t0) / 1e6)
            if active_g < 0:
                raise RuntimeError(f"Kernel error {active_g} in {name}")

        med_ms = float(np.median(times))
        max_err = int(np.max(np.abs(y_out - y_gt)))
        sha_ok = (sha256_arr(y_out) == ref_sha)
        mb_read = (active_g * m) / (1024.0 * 1024.0)
        return {
            "mode": name,
            "active_groups": f"{active_g}/{groups}",
            "weight_mb_read": round(mb_read, 3),
            "memory_traffic_reduction_vs_fp32": round(64.0 / max(1e-6, mb_read), 1),
            "leo_cpu_avx2_median_ms": round(med_ms, 3),
            "speedup_vs_dense_fp32_cpu": round(fp32_ms / max(1e-6, med_ms), 2),
            "max_abs_integer_error": max_err,
            "sha256_exact_match": sha_ok,
            "passed": (max_err == 0 and sha_ok),
        }

    # Mode 1: Adversarial 100% Dense Random (0% sparsity -> proves honest dense floor)
    m1 = bench_cpu_mode("M1_ADVERSARIAL_100PCT_DENSE_TERNARY", x_dense)

    # Mode 2: 85% Block-Sparse SwiGLU/ReLU2 Activation (realistic LLM FFN sparsity)
    x_sparse = np.zeros((k,), dtype=np.int16)
    active_g_idx = rng.choice(groups, size=int(groups * 0.15), replace=False)
    for g in active_g_idx:
        x_sparse[4 * g : 4 * g + 4] = rng.integers(-60, 61, size=(4,), dtype=np.int16)
    m2 = bench_cpu_mode("M2_85PCT_SPARSE_ACTIVATION_TERNARY", x_sparse)

    # Mode 3: 95% Persistent-Membrane Delta Stream (tests arbitrary int16 deltas > 63 too!)
    y_prev = (w_tern.astype(np.int32) @ x_dense.astype(np.int32)).astype(np.int32)
    x_next = x_dense.copy()
    changed_g = rng.choice(groups, size=int(groups * 0.05), replace=False)
    for g in changed_g:
        x_next[4 * g : 4 * g + 4] = rng.integers(-60, 61, size=(4,), dtype=np.int16)
    delta_x = (x_next - x_dense).astype(np.int16)  # Range [-120, +120] -> exercises exact chunk split!
    m3 = bench_cpu_mode("M3_95PCT_DELTA_PERSISTENT_MEMBRANE", delta_x, prev_y=y_prev, x_full_ref=x_next)

    # Mode 4: Live Intel UHD OpenCL + Simultaneous CPU+iGPU Split on Dense Ternary
    y_dense_exact = (w_tern.astype(np.int32) @ x_dense.astype(np.int32)).astype(np.int32)
    m4 = run_opencl_igpu_and_hybrid_split(lib, packed_w, x_dense, y_dense_exact, m, k)

    report = {
        "project": "LEO-ZeroBit (Standalone Open-Source Single-Device Engine)",
        "host": f"{platform.system()} {platform.release()} | {platform.processor()}",
        "layer_shape": [m, k],
        "fp32_weight_mb": 64.0,
        "zerobit_packed_mb": round(packed_w.nbytes / (1024.0 * 1024.0), 2),
        "baseline_dense_fp32_median_ms": round(fp32_ms, 3),
        "build_info": build_info,
        "avx2_intrinsics_active": avx2_active,
        "simulated_gpu_timings_present": False,
        "modes": {
            "mode_1_adversarial_dense": m1,
            "mode_2_sparse_activation": m2,
            "mode_3_delta_membrane": m3,
            "mode_4_live_igpu_and_hybrid_split": m4,
        },
        "all_cpu_modes_bit_exact": (m1["passed"] and m2["passed"] and m3["passed"]),
    }

    REPORT_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nVerified proof written to: {REPORT_OUT}")

    if not report["all_cpu_modes_bit_exact"]:
        print("FAIL: Exact integer parity check failed!", file=sys.stderr)
        return 1
    if m4["igpu_dispatched"] and not m4["verified_exact"]:
        print("FAIL: Intel UHD OpenCL / Hybrid split parity check failed!", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
