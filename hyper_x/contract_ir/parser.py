#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/contract_ir/parser.py
=============================
Parses raw inputs, hints, observables, and constraints into formal ContractIR.
"""

from typing import Any, Dict, Optional
import numpy as np
from .contract import ContractIR, CorrectnessMode
from .workload_classifier import classify_workload


class ContractParser:
    """Parses user requests and inputs into formal machine-readable execution contracts."""

    @staticmethod
    def parse(
        workload_id: str,
        input_data: Any,
        hints: Optional[Dict[str, Any]] = None
    ) -> ContractIR:
        h = hints or {}
        family = classify_workload(workload_id, input_data)

        # Derive input schema
        input_schema = {}
        if isinstance(input_data, np.ndarray):
            input_schema = {
                "type": "ndarray",
                "shape": list(input_data.shape),
                "dtype": str(input_data.dtype)
            }
        elif isinstance(input_data, str):
            input_schema = {
                "type": "string",
                "length": len(input_data)
            }
        elif isinstance(input_data, (dict, list)):
            input_schema = {
                "type": type(input_data).__name__,
                "length": len(input_data)
            }
        else:
            input_schema = {"type": type(input_data).__name__}

        # Exactness mapping
        if h.get("exact", False) or h.get("exact_bitwise", False):
            mode = CorrectnessMode.EXACT_BITWISE
            tol = 0.0
            atol = 0.0
            rtol = 0.0
            allowed_approx = []
        elif h.get("perceptual", False) or family == "GRAPHICS_TEMPORAL":
            mode = CorrectnessMode.PERCEPTUAL
            tol = h.get("numerical_tolerance", 1e-2)
            atol = h.get("absolute_tolerance", 1e-2)
            rtol = h.get("relative_tolerance", 1e-2)
            allowed_approx = ["temporal_reprojection", "bilateral_reconstruct", "low_rank"]
        elif h.get("predictive", False):
            mode = CorrectnessMode.PREDICTIVE
            tol = h.get("numerical_tolerance", 0.05)
            atol = h.get("absolute_tolerance", 0.05)
            rtol = h.get("relative_tolerance", 0.05)
            allowed_approx = ["speculative_draft", "low_rank"]
        elif h.get("bounded_approximation", False):
            mode = CorrectnessMode.BOUNDED_APPROXIMATION
            tol = h.get("numerical_tolerance", 1e-2)
            atol = h.get("absolute_tolerance", 1e-3)
            rtol = h.get("relative_tolerance", 1e-2)
            allowed_approx = ["low_rank", "sparsity", "quantization"]
        else:
            mode = CorrectnessMode.NUMERICALLY_EQUIVALENT
            tol = h.get("numerical_tolerance", 1e-4)
            atol = h.get("absolute_tolerance", 1e-5)
            rtol = h.get("relative_tolerance", 1e-3)
            allowed_approx = ["low_rank", "sparsity"]

        observable = h.get("observable", "OUTPUT_TENSOR")
        application = h.get("application", family)

        return ContractIR(
            workload_id=workload_id,
            application=application,
            observable=observable,
            input_schema=input_schema,
            output_schema=h.get("output_schema", {"type": "inferred"}),
            exactness_mode=mode,
            numerical_tolerance=tol,
            absolute_tolerance=atol,
            relative_tolerance=rtol,
            perceptual_tolerance=h.get("perceptual_tolerance", 0.95),
            latency_slo=h.get("latency_slo_ms", h.get("latency_slo", 100.0)),
            throughput_slo=h.get("throughput_slo", 10.0),
            memory_limit=h.get("memory_budget_mb", h.get("memory_limit", 2048.0)),
            determinism_requirement=h.get("deterministic", True),
            reproducibility_requirement=h.get("reproducible", True),
            allowed_approximations=h.get("allowed_approximations", allowed_approx),
            forbidden_transformations=h.get("forbidden_transformations", []),
            cache_policy=h.get("cache_policy", "EXACT_ONLY"),
            prediction_policy=h.get("prediction_policy", "VERIFIED_TARGET_ONLY"),
            reconstruction_policy=h.get("reconstruction_policy", "PERCEPTUAL_BOUNDED"),
            fallback_policy=h.get("fallback_policy", "DETERMINISTIC_LADDER"),
            verification_policy=h.get("verification_policy", "FAIL_CLOSED"),
            provenance_policy=h.get("provenance_policy", "CRYPTOGRAPHIC_MEASURED"),
            metadata=h.get("metadata", {})
        )
