#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/decp/engine.py
======================
Phase 7: HYPER-DECP Master Engine.

Orchestrates frozen execution and outputs definitive deterministic parity comparison.
"""

from typing import Dict, Any, Tuple
import numpy as np
from .manifest import FrozenExecutionManifest
from .comparator import CrossHardwareComparator


class DECPEngine:
    """Master engine for Deterministic Exact-Compute & Parity."""

    def __init__(self):
        self.comparator = CrossHardwareComparator()

    def run_deterministic_comparison(
        self,
        candidate_result: np.ndarray,
        reference_result: np.ndarray,
        manifest: FrozenExecutionManifest,
        rel_tolerance: float = 1e-4
    ) -> Dict[str, Any]:
        comp = self.comparator.compare(candidate_result, reference_result, rel_tolerance)
        comp["manifest_hash"] = manifest.compute_manifest_hash()
        comp["workload_id"] = manifest.workload_id
        comp["runtime_environment"] = manifest.runtime_environment
        return comp
