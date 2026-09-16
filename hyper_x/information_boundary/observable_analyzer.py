#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/observable_analyzer.py
===================================================
Phase 3: Observable Analyzer.
Extracts and analyzes application observables, determining whether the contract requires
full tensor reconstruction or whether an observable-directed reduction applies.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple, Optional, List
import numpy as np
from ..contract import WorkloadContract


class ObservableAnalyzer:
    """
    Inspects workload contract and execution request to identify:
    - Exact observable type and requested spatial/temporal/semantic bounds
    - Required precision and tolerance bounds
    - Observed vs unobserved volume fraction
    """

    @staticmethod
    def analyze_observable(
        contract: WorkloadContract,
        nominal_shape: Tuple[int, ...],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        meta = metadata or {}
        obs_type = contract.observable_type
        total_elements = int(np.prod(nominal_shape)) if nominal_shape else 1

        if obs_type in ("ARGMAX", "TOP_K"):
            k = meta.get("k", 1 if obs_type == "ARGMAX" else 5)
            observed_elements = min(k, total_elements)
            fraction = observed_elements / max(total_elements, 1)
            reduction_type = "INDEX_AND_LOGIT_PRUNING"
        elif obs_type in ("SUBREGION", "VIEWPORT_CULL"):
            sub_shape = meta.get("subregion_shape", tuple(max(1, s // 2) for s in nominal_shape))
            observed_elements = int(np.prod(sub_shape))
            fraction = min(1.0, observed_elements / max(total_elements, 1))
            reduction_type = "SPATIAL_CULLING"
        elif obs_type == "SCALAR_STATISTIC":
            observed_elements = 1
            fraction = 1.0 / max(total_elements, 1)
            reduction_type = "AGGREGATE_REDUCTION"
        elif obs_type == "FULL_TENSOR":
            observed_elements = total_elements
            fraction = 1.0
            reduction_type = "FULL_PRESERVATION"
        else:
            observed_elements = total_elements
            fraction = 1.0
            reduction_type = "DEFAULT_PRESERVATION"

        is_reduced = fraction < 0.999

        return {
            "workload_id": contract.workload_id,
            "observable_type": obs_type,
            "correctness_class": contract.correctness_class,
            "nominal_shape": list(nominal_shape),
            "nominal_elements": total_elements,
            "observed_elements": observed_elements,
            "observed_fraction": float(fraction),
            "unobserved_fraction": float(1.0 - fraction),
            "reduction_type": reduction_type,
            "allows_observable_escape": is_reduced and (contract.correctness_class != "EXACT_BIT_EQUAL" or obs_type in ("ARGMAX", "TOP_K", "SUBREGION")),
            "requires_full_state": not is_reduced or obs_type == "FULL_TENSOR",
        }
