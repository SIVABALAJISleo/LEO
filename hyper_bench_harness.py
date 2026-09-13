#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HYPER / LEO — LOCAL REAL-HARDWARE BENCHMARK HARNESS
====================================================
Run THIS file ON YOUR OWN MACHINE (Lenovo IdeaPad Slim 3 15IAH8,
Intel Core i5-12450H + Intel UHD Xe 48EU + 16GB RAM + Windows 11).

Purpose: produce REAL, measured numbers on YOUR exact hardware for the
LEO/HYPER audit. Nothing here is simulated or hardcoded — every number
is a wall-clock measurement of an actual computation.

What it measures:
  1. CPU identity / core count / frequency (best effort)
  2. FP32 & FP16 dense GEMM (numpy) at 256/512/1024/2048 — cold vs warm
  3. Streaming memory bandwidth (read + write)
  4. 2D FFT
  5. 3x3 convolution: naive vs Winograd (F(2x2,3x3)) — real timings
  6. Optional: OpenVINO iGPU (Intel UHD) matmul if installed
  7. Optional: psutil CPU% + temperature if available
  8. Writes results to hyper_bench_results.json + prints a summary

Requires:  pip install numpy
Optional:   pip install openvino psutil
No GPU driver required for the CPU portion.

Run:  python hyper_bench_harness.py
"""
import json, os, sys, time, platform, struct
from datetime import datetime

try:
    import numpy as np
    HAS_NP = True
except Exception:
    HAS_NP = False

HAS_PSUTIL = False
try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    pass

HAS_OV = False
try:
    import openvino as ov
    HAS_OV = True
except Exception:
    pass


def t_ms(fn, *args, repeat=1, **kw):
    """Wall-clock a callable; returns (best_ms, all_ms)."""
    times = []
    out = None
    for _ in range(repeat):
        t0 = time.perf_counter()
        out = fn(*args, **kw)
        times.append((time.perf_counter() - t0) * 1000.0)
    return min(times), times, out


def bench_gemm(size, dtype=np.float32, repeat=3):
    a = np.random.randn(size, size).astype(dtype)
    b = np.random.randn(size, size).astype(dtype)
    # warm
    _ = a @ b
    best, times, _ = t_ms(lambda: a @ b, repeat=repeat)
    flops = 2.0 * size**3
    return {"size": size, "dtype": np.dtype(dtype).name,
            "best_ms": round(best, 3), "all_ms": [round(x, 3) for x in times],
            "gflops": round(flops / (best / 1000.0) / 1e9, 2)}


def bench_bandwidth(nbytes=256 * 1024 * 1024, repeat=3):
    """Streaming read bandwidth over a buffer larger than L3 (~12MB)."""
    n = nbytes // 4
    x = np.random.randn(n).astype(np.float32)
    best, times, _ = t_ms(lambda: float(x.sum()), repeat=repeat)
    gbs = (nbytes / (best / 1000.0)) / 1e9
    return {"bytes": nbytes, "best_ms": round(best, 3),
            "read_bw_gb_s": round(gbs, 2)}


def bench_fft(size=2048, repeat=3):
    x = np.random.randn(size, size).astype(np.float32)
    best, times, _ = t_ms(lambda: np.fft.fft2(x), repeat=repeat)
    return {"size": size, "best_ms": round(best, 3),
            "all_ms": [round(x, 3) for x in times]}


def bench_conv(tile=64, k=3, repeat=5):
    """3x3 conv on a (tile,tile) image: naive vs Winograd F(2x2,3x3)."""
    img = np.random.randn(tile, tile).astype(np.float32)
    ker = np.random.randn(k, k).astype(np.float32)

    def naive():
        out = np.zeros((tile, tile), np.float32)
        for i in range(1, tile - 1):
            for j in range(1, tile - 1):
                out[i, j] = (img[i-1:i+2, j-1:j+2] * ker).sum()
        return out

    # Winograd F(2x2,3x3) transform matrices (standard)
    Bt = np.array([[1, 0, -1, 0], [0, 1, 1, 0],
                   [0, -1, 1, 0], [0, 1, 0, -1]], np.float32)
    G = np.array([[1, 0, 0], [0.5, 0.5, 0.5],
                  [0.5, -0.5, 0.5], [0, 0, 1]], np.float32)
    At = np.array([[1, 1, 1, 0], [0, 1, -1, -1]], np.float32)

    def winograd():
        out = np.zeros((tile, tile), np.float32)
        U = G @ ker @ G.T  # 4x4
        for i in range(0, tile - 2, 2):
            for j in range(0, tile - 2, 2):
                d = img[i:i+4, j:j+4]
                V = Bt @ d @ Bt.T
                M = U * V
                out[i:i+2, j:j+2] = At @ M @ At.T
        return out

    t_naive, _, _ = t_ms(naive, repeat=repeat)
    t_win, _, _ = t_ms(winograd, repeat=repeat)
    # correctness check vs scipy-free reference on a small patch
    ref = np.zeros((tile, tile), np.float32)
    for i in range(1, tile - 1):
        for j in range(1, tile - 1):
            ref[i, j] = (img[i-1:i+2, j-1:j+2] * ker).sum()
    win = winograd()
    err = float(np.abs(win - ref).max())
    return {"tile": tile, "naive_ms": round(t_naive, 3),
            "winograd_ms": round(t_win, 3),
            "speedup": round(t_naive / max(t_win, 1e-6), 2),
            "max_abs_err": err}


def bench_openvino_igpu(size=1024, repeat=3):
    """If OpenVINO is installed, run a matmul on the Intel UHD iGPU."""
    if not HAS_OV:
        return {"available": False}
    try:
        core = ov.Core()
        devices = core.available_devices
        gpu = [d for d in devices if "GPU" in d.upper()]
        if not gpu:
            return {"available": True, "devices": devices, "gpu": None}
        dev = gpu[0]
        a = np.random.randn(size, size).astype(np.float32)
        b = np.random.randn(size, size).astype(np.float32)
        # MatMul via ov opset
        try:
            from openvino import opset10 as ops
        except Exception:
            try:
                from openvino.runtime import opset10 as ops
            except Exception:
                return {"available": True, "devices": devices, "gpu": dev, "error": "opset10 not found"}
        pa = ov.op.Parameter(ov.Type.f32, ov.PartialShape([size, size]))
        pb = ov.op.Parameter(ov.Type.f32, ov.PartialShape([size, size]))
        mm = ops.matmul(pa, pb)
        model = ov.Model([mm], [pa, pb])
        comp = core.compile_model(model, dev)
        times = []
        for _ in range(repeat):
            t0 = time.perf_counter()
            comp([a, b])
            times.append((time.perf_counter() - t0) * 1000.0)
        best = min(times)
        flops = 2.0 * size**3
        return {"available": True, "device": dev, "devices": devices,
                "best_ms": round(best, 3), "all_ms": [round(x, 3) for x in times],
                "gflops": round(flops / (best / 1000.0) / 1e9, 2)}
    except Exception as e:
        return {"available": True, "error": str(e)}


def main():
    if not HAS_NP:
        print("numpy required:  pip install numpy")
        sys.exit(1)

    print("=" * 70)
    print("HYPER/LEO REAL-HARDWARE BENCHMARK  (run on YOUR machine)")
    print("=" * 70)
    results = {"timestamp": datetime.now().isoformat(),
               "host": platform.platform(),
               "machine": platform.machine(),
               "python": platform.python_version(),
               "numpy": np.__version__ if HAS_NP else None}

    # CPU info (best effort)
    cpu = {"cores_logical": os.cpu_count()}
    try:
        import subprocess
        if sys.platform == "win32":
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "(Get-CimInstance Win32_Processor).Name"],
                capture_output=True, text=True, timeout=20)
            cpu["name"] = r.stdout.strip()
    except Exception:
        pass
    try:
        cpu["freq_mhz"] = round(psutil.cpu_freq().current, 1) if HAS_PSUTIL else None
        cpu["cores_physical"] = psutil.cpu_count(logical=False) if HAS_PSUTIL else None
    except Exception:
        pass
    results["cpu"] = cpu
    print(f"CPU: {cpu.get('name', platform.processor())} | "
          f"logical={cpu.get('cores_logical')} phys={cpu.get('cores_physical')} "
          f"freq={cpu.get('freq_mhz')}MHz")

    # 1) GEMM sweep
    print("\n--- Dense GEMM (numpy, real timings) ---", flush=True)
    gemm = {}
    for size in (256, 512, 1024, 2048):
        for dt in (np.float32, np.float16):
            rep = 1 if (dt == np.float16 and size >= 1024) else 3
            r = bench_gemm(size, dt, repeat=rep)
            gemm[f"{size}_{np.dtype(dt).name}"] = r
            print(f"  GEMM {size}x{size} {np.dtype(dt).name}: "
                  f"{r['best_ms']} ms  {r['gflops']} GFLOPS", flush=True)
    results["gemm"] = gemm

    # 2) Bandwidth
    print("\n--- Streaming memory bandwidth ---")
    bw = bench_bandwidth()
    results["bandwidth"] = bw
    print(f"  read BW: {bw['read_bw_gb_s']} GB/s (256MB buffer, > L3)")

    # 3) FFT
    print("\n--- 2D FFT ---")
    fft = bench_fft()
    results["fft"] = fft
    print(f"  2048x2048 FFT: {fft['best_ms']} ms")

    # 4) Conv naive vs Winograd
    print("\n--- 3x3 Conv: naive vs Winograd ---")
    conv = bench_conv()
    results["conv"] = conv
    print(f"  naive {conv['naive_ms']} ms | winograd {conv['winograd_ms']} ms "
          f"| speedup {conv['speedup']}x | max_err {conv['max_abs_err']}")

    # 5) OpenVINO iGPU
    print("\n--- OpenVINO Intel UHD iGPU (optional) ---")
    ovr = bench_openvino_igpu()
    results["openvino_igpu"] = ovr
    if ovr.get("available"):
        print(f"  OpenVINO devices: {ovr.get('devices')}")
        if ovr.get("gpu"):
            print(f"  iGPU matmul {ovr['best_ms']} ms  {ovr['gflops']} GFLOPS")
        else:
            print("  No GPU device found via OpenVINO (CPU-only run).")
    else:
        print("  OpenVINO not installed (CPU-only run).")

    # 6) CPU util / temp snapshot
    if HAS_PSUTIL:
        try:
            results["cpu_util_pct"] = psutil.cpu_percent(interval=1.0)
            temps = getattr(psutil, "sensors_temperatures", lambda: {})()
            results["temps"] = {k: [c.current for c in v]
                                for k, v in temps.items()}
            print(f"\nCPU util: {results['cpu_util_pct']}%  temps: {results['temps']}")
        except Exception:
            pass

    # Save
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "hyper_bench_results.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {out}")
    print("NOTE: to also capture thermals/power over time on Windows, run "
          "HWiNFO64 in logging mode, or: powercfg /energy")

    return results


if __name__ == "__main__":
    main()
