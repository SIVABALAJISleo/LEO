"""
hyper_v3/workloads/workload_registry.py
Central registry mapping workload identifiers to runnable execution runners.
"""

from typing import Dict, Any, Callable
from hyper_v3.workloads.suite_15 import BenchmarkSuite15


WORKLOAD_REGISTRY: Dict[str, Callable] = {
    "dense_gemm_fp32": BenchmarkSuite15.run_w01_dense_gemm_fp32,
    "dense_gemm_fp16": BenchmarkSuite15.run_w02_dense_gemm_fp16,
    "fft_1d": BenchmarkSuite15.run_w03_fft_1d,
    "vector_reduction": BenchmarkSuite15.run_w04_vector_reduction,
    "batch1_ai": BenchmarkSuite15.run_w05_batch1_ai,
    "batched_ai": BenchmarkSuite15.run_w06_batched_ai,
    "semantic_query": BenchmarkSuite15.run_w07_semantic_query,
    "rasterization": BenchmarkSuite15.run_w08_rasterization,
    "particle_physics": BenchmarkSuite15.run_w09_particle_physics,
    "bvh_hierarchy": BenchmarkSuite15.run_w10_bvh_hierarchy,
    "path_tracing": BenchmarkSuite15.run_w11_path_tracing,
    "video_pipeline": BenchmarkSuite15.run_w12_video_pipeline,
    "nbody_simulation": BenchmarkSuite15.run_w13_nbody_simulation,
    "monte_carlo": BenchmarkSuite15.run_w14_monte_carlo,
    "viewport_transform": BenchmarkSuite15.run_w15_viewport_transform,
}
