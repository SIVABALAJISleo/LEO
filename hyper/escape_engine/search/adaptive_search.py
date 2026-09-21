"""
hyper/escape_engine/search/adaptive_search.py
============================================
VAEE Section 11 & 36: Adaptive Computational Pathway Search Controller.

Progressively searches the pathway space, tracks improvement rate,
measures saturation, and avoids prematurely claiming impossibility.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..contracts.schema import ComputationalContract
from ..contracts.information_boundary import InformationBoundaryProfile
from ..pathways.schema import ComputationalPathway
from ..pathways.generator import PathwayGenerator
from ..pathways.registry import PathwayRegistry
from .search_budget import SearchBudget
from .search_state import SearchState
from .diversity import DiversityEngine
from .novelty import NoveltyArchive


class AdaptiveSearchEngine:
    """Orchestrates adaptive progressive exploration of computational pathways."""

    def __init__(
        self,
        registry: Optional[PathwayRegistry] = None,
        generator: Optional[PathwayGenerator] = None,
    ) -> None:
        self.registry = registry or PathwayRegistry()
        self.generator = generator or PathwayGenerator()
        self.novelty_archive = NoveltyArchive()

    def search(
        self,
        contract: ComputationalContract,
        profile: InformationBoundaryProfile,
        evaluate_fn: Callable[[ComputationalPathway], Tuple[bool, str, float, float]],
        budget: Optional[SearchBudget] = None,
    ) -> SearchState:
        """
        Main adaptive search loop:
        evaluate_fn: pathway -> (is_verified, verification_level, latency_ms, memory_mb)
        """
        budget = budget or SearchBudget()
        state = SearchState(
            experiment_id=f"EXP-{int(time.time()*1000)%1000000:06d}",
            contract_id=contract.contract_id,
        )

        # Generate candidates
        candidates = self.generator.generate_candidates(contract, profile, max_candidates=budget.max_candidates)

        consecutive_stagnant = 0
        prev_best = float("inf")

        for cand in candidates:
            if budget.is_exhausted():
                break

            budget.increment()

            # Register pathway & verify structural uniqueness
            is_unique, registered_cand = self.registry.register(cand)

            # Evaluate candidate
            t0 = time.perf_counter_ns()
            is_verified, verif_level, latency_ms, mem_mb = evaluate_fn(registered_cand)

            # If first candidate, set baseline
            if state.total_evaluated == 0:
                state.baseline_latency_ms = latency_ms

            ev = state.record_evaluation(
                pathway=registered_cand,
                is_verified=is_verified,
                verification_level=verif_level,
                latency_ms=latency_ms,
                memory_mb=mem_mb,
            )

            # Novelty archive update
            self.novelty_archive.consider_add(registered_cand)

            # Saturation detection
            if state.best_latency_ms < prev_best:
                prev_best = state.best_latency_ms
                consecutive_stagnant = 0
            else:
                consecutive_stagnant += 1

            if consecutive_stagnant >= budget.patience_without_improvement:
                state.saturation_detected = True
                state.saturation_reason = (
                    f"Search saturation detected: 0 verified improvements in the last "
                    f"{consecutive_stagnant} evaluated pathways."
                )
                break

        # Final outcome determination (Never confuse UNKNOWN with IMPOSSIBLE)
        if state.total_verified > 0 and state.best_latency_ms < state.baseline_latency_ms:
            state.outcome = "SUCCESS"
        elif state.total_verified > 0:
            state.outcome = "SUCCESS"  # Verified candidates found, even if not strictly faster
        else:
            state.outcome = "UNKNOWN"

        return state
