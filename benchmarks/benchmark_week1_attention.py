"""
benchmarks/benchmark_week1_attention.py
Comprehensive Benchmark: Dense vs Local vs Vectorized Block Attention
Intel Core i5-12450H Optimized Benchmark Suite
"""

import os
import sys
import time
import json
import numpy as np
from typing import Dict, Any, Tuple

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core_ai.attention import VectorizedBlockAttention, LocalAttention


class ComprehensiveAttentionBenchmark:
    """Benchmark harness for Dense vs Block vs Local Attention."""

    @staticmethod
    def baseline_attention_vectorized(Q: np.ndarray, K: np.ndarray, V: np.ndarray, causal: bool = True) -> Tuple[np.ndarray, float]:
        """Dense O(n^2) attention with vectorized softmax."""
        t0 = time.perf_counter()
        seq_len, d = Q.shape
        scale = 1.0 / np.sqrt(d)

        scores = (Q @ K.T) * scale
        if causal:
            causal_mask = np.triu(np.ones((seq_len, seq_len), dtype=bool), k=1)
            scores = np.where(causal_mask, -1e9, scores)

        attn = VectorizedBlockAttention.softmax_stable(scores, axis=-1)
        output = attn @ V
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return output, elapsed_ms

    @staticmethod
    def block_attention_test(Q: np.ndarray, K: np.ndarray, V: np.ndarray, block_size: int = 64, summary_size: int = 20, causal: bool = True) -> Tuple[np.ndarray, float]:
        """Vectorized Block Attention test."""
        attn_engine = VectorizedBlockAttention(block_size=block_size, summary_size=summary_size, causal=causal)
        t0 = time.perf_counter()
        output = attn_engine.forward(Q, K, V)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return output, elapsed_ms

    @staticmethod
    def local_attention_test(Q: np.ndarray, K: np.ndarray, V: np.ndarray, window_size: int = 64, causal: bool = True) -> Tuple[np.ndarray, float]:
        """Local Window Attention test."""
        attn_engine = LocalAttention(window_size=window_size, causal=causal)
        t0 = time.perf_counter()
        output = attn_engine.forward(Q, K, V)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return output, elapsed_ms

    @classmethod
    def run_suite(
        cls,
        seq_lengths=(256, 512, 1024, 2048),
        d: int = 64,
        block_size: int = 64,
        summary_size: int = 20,
        window_size: int = 64,
        output_file: str = "benchmark_attention_week1.json"
    ) -> Dict[str, Any]:
        print("=" * 80)
        print("LEO RADICAL PATHWAY REDESIGN: ATTENTION BENCHMARK SUITE")
        print("Target: Intel Core i5-12450H + Intel UHD (CPU & Memory Efficient)")
        print("=" * 80)

        results = {}

        for seq_len in seq_lengths:
            print(f"\nEvaluating Sequence Length: {seq_len} (d={d})")
            print("-" * 80)

            np.random.seed(42)
            Q = np.random.randn(seq_len, d).astype(np.float32)
            K = np.random.randn(seq_len, d).astype(np.float32)
            V = np.random.randn(seq_len, d).astype(np.float32)

            # Warmup
            _, _ = cls.baseline_attention_vectorized(Q[:64], K[:64], V[:64])
            _, _ = cls.block_attention_test(Q[:64], K[:64], V[:64], block_size, summary_size)
            _, _ = cls.local_attention_test(Q[:64], K[:64], V[:64], window_size)

            # Benchmark 3 runs and average
            dense_runs = []
            for _ in range(3):
                out_dense, t_dense = cls.baseline_attention_vectorized(Q, K, V)
                dense_runs.append(t_dense)
            t_dense_avg = float(np.mean(dense_runs))

            block_runs = []
            for _ in range(3):
                out_block, t_block = cls.block_attention_test(Q, K, V, block_size, summary_size)
                block_runs.append(t_block)
            t_block_avg = float(np.mean(block_runs))

            local_runs = []
            for _ in range(3):
                out_local, t_local = cls.local_attention_test(Q, K, V, window_size)
                local_runs.append(t_local)
            t_local_avg = float(np.mean(local_runs))

            # Relative Frobenius errors
            norm_dense = np.linalg.norm(out_dense) + 1e-8
            err_block = float(np.linalg.norm(out_dense - out_block) / norm_dense)
            err_local = float(np.linalg.norm(out_dense - out_local) / norm_dense)

            speedup_block = t_dense_avg / max(1e-4, t_block_avg)
            speedup_local = t_dense_avg / max(1e-4, t_local_avg)

            # FLOP calculations
            block_engine = VectorizedBlockAttention(block_size, summary_size)
            full_flops, block_flops = block_engine.compute_flops(seq_len, d)
            local_engine = LocalAttention(window_size)
            _, local_flops = local_engine.compute_flops(seq_len, d)

            results[str(seq_len)] = {
                "seq_len": seq_len,
                "d": d,
                "dense_ms": round(t_dense_avg, 2),
                "block_ms": round(t_block_avg, 2),
                "block_speedup": round(speedup_block, 2),
                "block_error": float(f"{err_block:.4e}"),
                "block_flops": block_flops,
                "local_ms": round(t_local_avg, 2),
                "local_speedup": round(speedup_local, 2),
                "local_error": float(f"{err_local:.4e}"),
                "local_flops": local_flops,
                "full_flops": full_flops,
                "theoretical_block_speedup": round(full_flops / max(1, block_flops), 2),
                "theoretical_local_speedup": round(full_flops / max(1, local_flops), 2)
            }

            print(f"  Dense Baseline:        {t_dense_avg:8.2f} ms | FLOPs: {full_flops:,}")
            print(f"  Block Attention:       {t_block_avg:8.2f} ms | Speedup: {speedup_block:5.2f}x | Error: {err_block:.2e} | Theo: {full_flops/block_flops:.1f}x")
            print(f"  Local Window:          {t_local_avg:8.2f} ms | Speedup: {speedup_local:5.2f}x | Error: {err_local:.2e} | Theo: {full_flops/local_flops:.1f}x")

        # Save to JSON
        output_payload = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "hardware": "Intel Core i5-12450H + Intel UHD",
            "parameters": {
                "block_size": block_size,
                "summary_size": summary_size,
                "window_size": window_size,
                "d": d
            },
            "results": results
        }

        with open(output_file, "w") as f:
            json.dump(output_payload, f, indent=2)

        print("\n" + "=" * 80)
        print(f"Benchmark report saved to: {os.path.abspath(output_file)}")
        print("=" * 80)
        return output_payload


if __name__ == "__main__":
    ComprehensiveAttentionBenchmark.run_suite()
