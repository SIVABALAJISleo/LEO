"""
hyper/escape_engine/contracts/extractor.py
=========================================
Automated Computational Contract Extractor for VAEE.
Extracts explicit machine-readable contracts from input samples, problem specifications, and functions.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

from .schema import ComputationalContract


class ContractExtractor:
    """Extracts explicit, machine-readable computational contracts."""

    @staticmethod
    def extract_from_tensor_op(
        name: str,
        input_sample: Any,
        reference_fn: Callable[[Any], Any],
        tolerance: float = 0.0,
        relative_tolerance: float = 0.0,
        correctness: str = "EXACT",
        max_latency_ms: Optional[float] = None,
        max_memory_mb: Optional[float] = None,
        verification_method: Optional[str] = None,
    ) -> ComputationalContract:
        """Extract contract by probing a reference implementation with a sample input."""
        # Probe reference execution
        out = reference_fn(input_sample)

        # Detect input shape and dtype
        if isinstance(input_sample, np.ndarray):
            in_shape = input_sample.shape
            dtype = str(input_sample.dtype)
            in_type = "matrix" if input_sample.ndim == 2 else ("vector" if input_sample.ndim == 1 else "tensor")
        elif isinstance(input_sample, (list, tuple)):
            in_shape = (len(input_sample),)
            dtype = "int64" if all(isinstance(x, int) for x in input_sample) else "float32"
            in_type = "sequence"
        else:
            in_shape = (1,)
            dtype = type(input_sample).__name__
            in_type = "scalar"

        # Detect output shape and type
        if isinstance(out, np.ndarray):
            out_shape = out.shape
            out_type = "matrix" if out.ndim == 2 else ("vector" if out.ndim == 1 else "tensor")
        elif isinstance(out, (list, tuple)):
            out_shape = (len(out),)
            out_type = "sequence"
        else:
            out_shape = (1,)
            out_type = "scalar"

        verif_method = verification_method or ("EXACT" if tolerance == 0.0 and relative_tolerance == 0.0 else "EXACT_DIFFERENTIAL")

        return ComputationalContract(
            contract_id=f"contract_{name}_{in_shape}",
            input_type=in_type,
            output_type=out_type,
            input_shape=in_shape,
            output_shape=out_shape,
            dtype=dtype,
            correctness=correctness,
            numeric_tolerance=tolerance,
            relative_tolerance=relative_tolerance,
            deterministic=True,
            max_latency_ms=max_latency_ms,
            max_memory_mb=max_memory_mb,
            verification_method=verif_method,
        )

    @staticmethod
    def extract_from_spec(spec: Dict[str, Any]) -> ComputationalContract:
        """Create contract from dictionary specification."""
        return ComputationalContract.from_dict(spec)
