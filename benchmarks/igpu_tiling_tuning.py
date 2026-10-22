"""
OpenVINO Dynamic iGPU Matrix Tiling & Crossover Tuning Benchmark
================================================================
Empirically profiles Intel UHD Graphics (iGPU) vs CPU AVX2 OpenBLAS across:
- Matrix dimensions N in [256, 512, 768, 1024, 1536, 2048]
- Tiling split ratios alpha in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]

Establishes:
1. Exact crossover point N* where iGPU compute throughput beats CPU BLAS dispatch.
2. Optimal hybrid split ratio alpha* where concurrent CPU + iGPU execution minimizes total latency.
3. Strict numerical accuracy verification against IEEE 754 CPU reference.
"""

from concurrent.futures import ThreadPoolExecutor
import gc
import json
import os
import platform
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

try:
    import openvino as ov
    _HAS_OPENVINO = True
except ImportError:
    _HAS_OPENVINO = False

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class OpenVINOMatmulTuner:
    """Manages empirical execution and dynamic tiling across CPU and Intel UHD iGPU."""

    def __init__(self):
        if not _HAS_OPENVINO:
            raise RuntimeError("OpenVINO is required for iGPU tiling tuning.")
        self.core = ov.Core()
        self.has_igpu = "GPU" in self.core.available_devices
        self.gpu_name = self.core.get_property("GPU", "FULL_DEVICE_NAME") if self.has_igpu else "None"
        self._compiled_gpu_models: Dict[Tuple[int, int, int], Any] = {}

    def get_gpu_model(self, M: int, K: int, N: int):
        """Compiles or retrieves cached OpenVINO model for shape [M, K] x [K, N]."""
        key = (M, K, N)
        if key not in self._compiled_gpu_models:
            pa = ov.opset10.parameter([M, K], ov.Type.f32, name=f"A_{M}_{K}")
            pb = ov.opset10.parameter([K, N], ov.Type.f32, name=f"B_{K}_{N}")
            mm = ov.opset10.matmul(pa, pb, False, False)
            model = ov.Model([mm], [pa, pb], f"tiled_matmul_{M}_{K}_{N}")
            # Enforce f32 precision hint to prevent driver truncation
            self._compiled_gpu_models[key] = self.core.compile_model(
                model, "GPU", {"INFERENCE_PRECISION_HINT": "f32"}
            )
        return self._compiled_gpu_models[key]

    def execute_pure_cpu(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        return np.matmul(A, B)

    def execute_pure_gpu(self, A: np.ndarray, B: np.ndarray) -> np.ndarray:
        M, K = A.shape
        _, N = B.shape
        compiled = self.get_gpu_model(M, K, N)
        return compiled([A, B])[0]

    def execute_hybrid_tiled(
        self, A: np.ndarray, B: np.ndarray, alpha: float, executor: ThreadPoolExecutor
    ) -> np.ndarray:
        """
        Executes hybrid tiled multiplication:
        alpha * M rows computed on iGPU via OpenVINO.
        (1 - alpha) * M rows computed on CPU AVX2 via OpenBLAS concurrently.
        """
        M, K = A.shape
        _, N = B.shape
        M_gpu = int(round(M * alpha))
        M_cpu = M - M_gpu

        if M_gpu == 0:
            return self.execute_pure_cpu(A, B)
        if M_cpu == 0:
            return self.execute_pure_gpu(A, B)

        A_gpu = np.ascontiguousarray(A[:M_gpu, :])
        A_cpu = np.ascontiguousarray(A[M_gpu:, :])

        # Submit concurrent tasks
        fut_gpu = executor.submit(self.execute_pure_gpu, A_gpu, B)
        fut_cpu = executor.submit(self.execute_pure_cpu, A_cpu, B)

        out_gpu = fut_gpu.result()
        out_cpu = fut_cpu.result()

        return np.vstack([out_gpu, out_cpu])


def run_tuning_sweep():
    print("=" * 80)
    print("OPENVINO DYNAMIC iGPU MATRIX TILING & CROSSOVER TUNING BENCHMARK")
    print(f"Platform: {platform.processor()} | OS: {platform.system()} {platform.release()}")
    tuner = OpenVINOMatmulTuner()
    print(f"Detected iGPU: {tuner.gpu_name}")
    print("=" * 80)

    if not tuner.has_igpu:
        print("ERROR: Intel UHD Graphics (OpenVINO GPU) not detected. Exiting.")
        return

    dimensions = [256, 512, 768, 1024, 1536, 2048]
    split_ratios = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]
    results_by_dim: Dict[str, Any] = {}
    executor = ThreadPoolExecutor(max_workers=2)

    print("\nStarting Empirical Sweep across Dimensions and Split Ratios...")
    print(f"{'N':>6} | {'Split':>6} | {'CPU (ms)':>9} | {'iGPU (ms)':>9} | {'Hybrid (ms)':>11} | {'Speedup':>8} | {'Max Rel Err':>12}")
    print("-" * 75)

    for N in dimensions:
        rng = np.random.RandomState(42)
        A = rng.randn(N, N).astype(np.float32)
        B = rng.randn(N, N).astype(np.float32)

        # Baseline CPU measurement
        for _ in range(2):
            _ = tuner.execute_pure_cpu(A, B)
        cpu_times = []
        for _ in range(5):
            t0 = time.perf_counter()
            ref_c = tuner.execute_pure_cpu(A, B)
            cpu_times.append((time.perf_counter() - t0) * 1000.0)
        cpu_median = float(np.median(cpu_times))

        # Pure iGPU measurement
        for _ in range(2):
            _ = tuner.execute_pure_gpu(A, B)
        gpu_times = []
        for _ in range(5):
            t0 = time.perf_counter()
            gpu_c = tuner.execute_pure_gpu(A, B)
            gpu_times.append((time.perf_counter() - t0) * 1000.0)
        gpu_median = float(np.median(gpu_times))

        dim_records: List[Dict[str, Any]] = []
        best_time = min(cpu_median, gpu_median)
        best_config = "CPU" if cpu_median <= gpu_median else "iGPU"

        for alpha in split_ratios:
            # Warmup
            _ = tuner.execute_hybrid_tiled(A, B, alpha, executor)

            times = []
            for _ in range(5):
                t0 = time.perf_counter()
                out = tuner.execute_hybrid_tiled(A, B, alpha, executor)
                times.append((time.perf_counter() - t0) * 1000.0)
            med_time = float(np.median(times))

            # Numerical Verification
            diff = np.max(np.abs(out - ref_c))
            ref_norm = np.max(np.abs(ref_c))
            rel_err = float(diff / max(1e-12, ref_norm))
            speedup_vs_cpu = round(cpu_median / med_time, 2)

            if med_time < best_time:
                best_time = med_time
                best_config = f"Hybrid(alpha={alpha})"

            rec = {
                "alpha": alpha,
                "median_ms": round(med_time, 3),
                "speedup_vs_cpu": speedup_vs_cpu,
                "max_rel_error": f"{rel_err:.2e}",
                "verified": rel_err <= 1e-4,
            }
            dim_records.append(rec)

            alpha_str = f"{alpha:.1f}"
            print(f"{N:>6} | {alpha_str:>6} | {cpu_median:>9.2f} | {gpu_median:>9.2f} | {med_time:>11.2f} | {speedup_vs_cpu:>7.2f}x | {rel_err:>12.2e}")

        results_by_dim[str(N)] = {
            "dimension": N,
            "cpu_median_ms": round(cpu_median, 3),
            "pure_gpu_median_ms": round(gpu_median, 3),
            "pure_gpu_speedup": round(cpu_median / gpu_median, 2),
            "best_config": best_config,
            "best_time_ms": round(best_time, 3),
            "max_speedup_vs_cpu": round(cpu_median / best_time, 2),
            "split_sweeps": dim_records,
        }

    executor.shutdown(wait=True)

    # Calculate exact crossover dimension
    crossover_dim = None
    for N in sorted(dimensions):
        data = results_by_dim[str(N)]
        if data["pure_gpu_median_ms"] < data["cpu_median_ms"]:
            crossover_dim = N
            break

    summary = {
        "device_info": {
            "cpu": platform.processor(),
            "igpu": tuner.gpu_name,
            "openvino_version": ov.__version__,
        },
        "exact_crossover_dimension": crossover_dim,
        "crossover_finding": f"Intel UHD Graphics beats CPU AVX2 OpenBLAS for N >= {crossover_dim}." if crossover_dim else "CPU faster across all tested sizes.",
        "dimensions_evaluated": dimensions,
        "results": results_by_dim,
    }

    out_file = os.path.join(WORKSPACE_ROOT, "docs", "cpce", "IGPU_TUNING_RESULTS.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print("TUNING SUMMARY")
    print(f"Crossover Dimension N*: {crossover_dim} (Pure iGPU faster than CPU BLAS)")
    print(f"Results written to: {out_file}")
    print("=" * 80)
    return summary


if __name__ == "__main__":
    run_tuning_sweep()
