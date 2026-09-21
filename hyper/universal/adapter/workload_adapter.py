"""
hyper/universal/adapter/workload_adapter.py
===========================================
Universal Workload Adapter for arbitrary computational intake.
Analyzes arbitrary Python functions, dataflow graphs, and tensors to extract:
- Workload ID & structural hash
- Input/output schemas
- Memory access patterns
- Parallelism & branching indicators
- Domain classification
"""

from __future__ import annotations

import hashlib
import inspect
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

from .workload_types import WorkloadDomain, InputOutputSchema, WorkloadNecessityClass


class UniversalWorkload:
    """Standardized descriptor for any computational workload."""

    def __init__(
        self,
        workload_id: str,
        target_fn: Callable[[Any], Any],
        sample_input: Any,
        domain: WorkloadDomain = WorkloadDomain.UNKNOWN_UNSEEN,
        reference_output: Optional[Any] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.workload_id = workload_id
        self.target_fn = target_fn
        self.sample_input = sample_input
        self.domain = domain
        self.reference_output = reference_output
        self.name = name or workload_id
        self.metadata = metadata or {}

        # Derived properties
        self.workload_hash = self._compute_hash()
        self.schema = self._extract_schema()
        self.execution_graph = self._infer_execution_graph()

    def _compute_hash(self) -> str:
        h = hashlib.sha256()
        h.update(self.workload_id.encode("utf-8"))
        try:
            src = inspect.getsource(self.target_fn)
            h.update(src.encode("utf-8"))
        except Exception:
            h.update(str(self.target_fn).encode("utf-8"))
        if isinstance(self.sample_input, np.ndarray):
            h.update(str(self.sample_input.shape).encode("utf-8"))
            h.update(str(self.sample_input.dtype).encode("utf-8"))
            # Sample sample hash
            h.update(self.sample_input.tobytes()[:256])
        else:
            h.update(str(type(self.sample_input)).encode("utf-8"))
        return h.hexdigest()

    def _extract_schema(self) -> InputOutputSchema:
        inp = self.sample_input
        if isinstance(inp, np.ndarray):
            in_type = "ndarray"
            in_shape = inp.shape
            in_dtype = str(inp.dtype)
            count = int(inp.size)
            bytes_est = int(inp.nbytes)
        elif isinstance(inp, (list, tuple)):
            in_type = "sequence"
            in_shape = (len(inp),)
            in_dtype = type(inp[0]).__name__ if len(inp) > 0 else "unknown"
            count = len(inp)
            bytes_est = count * 8
        elif isinstance(inp, (int, float, complex)):
            in_type = "scalar"
            in_shape = (1,)
            in_dtype = type(inp).__name__
            count = 1
            bytes_est = 8
        else:
            in_type = type(inp).__name__
            in_shape = None
            in_dtype = type(inp).__name__
            count = 1
            bytes_est = 64

        out_type = "unknown"
        out_shape = None
        out_dtype = None
        if self.reference_output is not None:
            out = self.reference_output
            if isinstance(out, np.ndarray):
                out_type = "ndarray"
                out_shape = out.shape
                out_dtype = str(out.dtype)
            elif isinstance(out, (list, tuple)):
                out_type = "sequence"
                out_shape = (len(out),)
                out_dtype = type(out[0]).__name__ if len(out) > 0 else "unknown"
            elif isinstance(out, (int, float, complex)):
                out_type = "scalar"
                out_shape = (1,)
                out_dtype = type(out).__name__

        return InputOutputSchema(
            input_type=in_type,
            input_shape=in_shape,
            input_dtype=in_dtype,
            output_type=out_type,
            output_shape=out_shape,
            output_dtype=out_dtype,
            element_count=count,
            estimated_bytes=bytes_est,
        )

    def _infer_execution_graph(self) -> Dict[str, Any]:
        """Infers basic data dependencies and operations from function attributes."""
        nodes = []
        edges = []
        is_parallelizable = True
        branching_factor = 1.0

        try:
            src = inspect.getsource(self.target_fn)
            if "for " in src or "while " in src:
                branching_factor = 2.0
            if "if " in src:
                branching_factor += 1.0
            if "yield " in src:
                is_parallelizable = False
        except Exception:
            pass

        return {
            "estimated_nodes": len(nodes) or 1,
            "estimated_edges": len(edges) or 0,
            "is_parallelizable": is_parallelizable,
            "branching_factor": branching_factor,
            "has_memory_locality": isinstance(self.sample_input, np.ndarray),
        }

    def execute_reference(self, inp: Optional[Any] = None) -> Any:
        x = self.sample_input if inp is None else inp
        return self.target_fn(x)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "name": self.name,
            "workload_hash": self.workload_hash,
            "domain": self.domain.value,
            "schema": self.schema.to_dict(),
            "execution_graph": self.execution_graph,
            "metadata": self.metadata,
        }


class UniversalWorkloadAdapter:
    """Adapts arbitrary user functions or workloads into UniversalWorkload instances."""

    @staticmethod
    def adapt(
        target: Union[Callable[[Any], Any], UniversalWorkload],
        sample_input: Any,
        workload_id: Optional[str] = None,
        domain: Optional[WorkloadDomain] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UniversalWorkload:
        if isinstance(target, UniversalWorkload):
            return target

        fn = target
        w_id = workload_id or f"WL-{int(time.time()*1000)%1000000:06d}"

        # Automatic domain inference if not provided
        inferred_domain = domain or UniversalWorkloadAdapter.infer_domain(fn, sample_input, name_hint=f"{w_id} {name or ''}")

        # Run reference trial to get output shape and verify execution
        ref_out = None
        try:
            ref_out = fn(sample_input)
        except Exception as e:
            # Function might require special handling
            pass

        meta = dict(metadata) if metadata else {}
        if "coeffs" not in meta and hasattr(fn, "__closure__") and fn.__closure__:
            for cell in fn.__closure__:
                try:
                    val = cell.cell_contents
                    if isinstance(val, np.ndarray) and val.ndim == 1:
                        meta["coeffs"] = val
                        break
                except Exception:
                    pass

        return UniversalWorkload(
            workload_id=w_id,
            target_fn=fn,
            sample_input=sample_input,
            domain=inferred_domain,
            reference_output=ref_out,
            name=name,
            metadata=meta,
        )

    @staticmethod
    def infer_domain(fn: Callable[[Any], Any], sample_input: Any, name_hint: Optional[str] = None) -> WorkloadDomain:
        name = f"{getattr(fn, '__name__', '')} {name_hint or ''}".lower()

        if any(k in name for k in ["poly", "horner", "taylor", "power_sum"]):
            return WorkloadDomain.NUMERICAL
        if any(k in name for k in ["gemm", "matmul", "matrix", "tensor", "dot"]):
            return WorkloadDomain.MATRIX_TENSOR
        if any(k in name for k in ["sort", "search", "binary_search", "partition"]):
            return WorkloadDomain.SEARCH_SORTING
        if any(k in name for k in ["conv", "filter", "image", "blur", "edge"]):
            return WorkloadDomain.IMAGE_VIDEO_PROCESSING
        if any(k in name for k in ["fft", "signal", "audio", "wave", "stft"]):
            return WorkloadDomain.SIGNAL_PROCESSING
        if any(k in name for k in ["knapsack", "dp", "lcs", "edit_distance", "fib"]):
            return WorkloadDomain.DYNAMIC_PROGRAMMING
        if any(k in name for k in ["graph", "dijkstra", "bfs", "dfs", "shortest_path"]):
            return WorkloadDomain.GRAPH_NETWORK
        if any(k in name for k in ["particle", "nbody", "physics", "diffusion", "heat"]):
            return WorkloadDomain.PHYSICS_PARTICLE
        if any(k in name for k in ["render", "raster", "ray", "shader", "pixel"]):
            return WorkloadDomain.GRAPHICS_RENDERING
        if any(k in name for k in ["compress", "decompress", "lz", "huffman", "entropy"]):
            return WorkloadDomain.COMPRESSION_DECOMPRESSION
        if any(k in name for k in ["encrypt", "decrypt", "hash", "sha", "aes"]):
            return WorkloadDomain.CRYPTOGRAPHIC
        if any(k in name for k in ["infer", "forward", "predict", "attention", "transformer"]):
            return WorkloadDomain.MACHINE_LEARNING_INFERENCE

        # Type-based heuristics
        if isinstance(sample_input, np.ndarray):
            if sample_input.ndim == 2:
                return WorkloadDomain.MATRIX_TENSOR
            elif sample_input.ndim >= 3:
                return WorkloadDomain.IMAGE_VIDEO_PROCESSING
            else:
                return WorkloadDomain.NUMERICAL

        return WorkloadDomain.CUSTOM_USER_CODE
