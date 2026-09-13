#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/decp/engine.py
======================
Phase 11: HYPER-DECP Master Engine.

Orchestrates deterministic exact-compute comparison across Track A (Same Computation)
and Track B (Different Computation, Contract-Valid).
"""

from typing import Dict, Any, Tuple
import numpy as np
from .manifest import FrozenExecutionManifest
from .comparator import CrossHardwareComparator, DECPStatus


class DECPEngine:
    """Master engine for Deterministic Exact-Compute & Parity."""

    def __init__(self):
        self.comparator = CrossHardwareComparator()

    def run_deterministic_comparison(
        self,
        candidate_result: np.ndarray,
        reference_result: np.ndarray,
        manifest: FrozenExecutionManifest,
        rel_tolerance: float = 1e-4,
        abs_tolerance: float = 1e-5,
        track: str = "TRACK_B",
        contract_satisfied: bool = True
    ) -> Dict[str, Any]:
        comp = self.comparator.compare(
            cand_out=candidate_result,
            ref_out=reference_result,
            rel_tolerance=rel_tolerance,
            abs_tolerance=abs_tolerance,
            track=track,
            contract_satisfied=contract_satisfied
        )
        comp["manifest_hash"] = manifest.compute_manifest_hash()
        comp["workload_id"] = manifest.workload_id
        comp["runtime_environment"] = manifest.runtime_environment
        return comp
