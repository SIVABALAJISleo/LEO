"""
hyper_v3/runtime/pipeline.py
Asynchronous pipeline manager overlapping preprocessing, compute, and postprocessing.
"""

from typing import Callable, Any, Tuple
import time


class PipelineCoordinator:
    """Coordinates multi-stage asynchronous data pipelines."""

    @staticmethod
    def execute_pipelined_stage(preprocess_fn: Callable, compute_fn: Callable, postprocess_fn: Callable, data: Any) -> Tuple[Any, float]:
        t0 = time.perf_counter()
        pre = preprocess_fn(data)
        res = compute_fn(pre)
        out = postprocess_fn(res)
        elapsed_us = (time.perf_counter() - t0) * 1e6
        return out, elapsed_us
