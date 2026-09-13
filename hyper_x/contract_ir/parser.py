#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/contract_ir/parser.py
=============================
Parses raw inputs, hints, and constraints into formal ContractIR.
"""

from typing import Any, Dict, Optional
import numpy as np
from .contract import ContractIR, ExactnessClass
from .workload_classifier import classify_workload


class ContractParser:
    """Parses user requests and inputs into formal execution contracts."""

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
        if h.get("exact", False):
            exactness = ExactnessClass.EXACT
            tol = 0.0
            atol = 0.0
            approx_allowed = False
        elif h.get("perceptual", False) or family == "GRAPHICS_TEMPORAL":
            exactness = ExactnessClass.PERCEPTUAL_APPROXIMATION
            tol = h.get("numerical_tolerance", 1e-2)
            atol = h.get("absolute_tolerance", 1e-2)
            approx_allowed = True
        elif h.get("predictive", False):
            exactness = ExactnessClass.PREDICTIVE
            tol = h.get("numerical_tolerance", 0.05)
            atol = h.get("absolute_tolerance", 0.05)
            approx_allowed = True
        else:
            exactness = ExactnessClass.NUMERICALLY_EQUIVALENT
            tol = h.get("numerical_tolerance", 1e-4)
            atol = h.get("absolute_tolerance", 1e-5)
            approx_allowed = False

        return ContractIR(
            workload_id=workload_id,
            workload_family=family,
            input_schema=input_schema,
            output_schema=h.get("output_schema", {"type": "inferred"}),
            exactness_class=exactness,
            numerical_tolerance=tol,
            absolute_tolerance=atol,
            perceptual_tolerance=h.get("perceptual_tolerance", 0.95),
            latency_slo_ms=h.get("latency_slo_ms", 100.0),
            throughput_slo=h.get("throughput_slo", 10.0),
            memory_budget_mb=h.get("memory_budget_mb", 2048.0),
            energy_budget_joules=h.get("energy_budget_joules", None),
            determinism_requirement=h.get("deterministic", True),
            reproducibility_requirement=h.get("reproducible", True),
            allowed_approximation=approx_allowed,
            allowed_prediction=h.get("allow_prediction", False),
            allowed_reconstruction=h.get("allow_reconstruction", False),
            cache_policy=h.get("cache_policy", "EXACT_ONLY"),
            fallback_policy=h.get("fallback_policy", "EXACT_REFERENCE"),
            metadata=h.get("metadata", {})
        )
