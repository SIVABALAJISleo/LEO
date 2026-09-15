"""
hyper_x/leaf/discovery/search.py
================================
Parallel and heuristic candidate search engine for LEAF.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import time

from .candidate import EscapeCandidate
from .generator import EscapeGenerator
from .ranking import CandidateRanker, CandidateMultiScore
from ..contract import LeafContract


class EscapeSearchEngine:
    """Explores candidate escape strategies and selects the cheapest valid pathway."""

    def __init__(self):
        self.generator = EscapeGenerator()
        self.ranker = CandidateRanker()

    def search_best_pathway(
        self,
        workload_name: str,
        contract: LeafContract,
        reference_flops: int,
        evaluators: Dict[str, Callable[[], Tuple[bool, float, float, float, int, int]]],
    ) -> Optional[CandidateMultiScore]:
        """
        Searches generated candidates by invoking evaluators and ranking results.
        Evaluator returns: (is_correct, ref_ms, cand_ms, verif_ms, ref_mem, cand_mem)
        """
        candidates = self.generator.generate_candidates_for_workload(
            workload_name, contract, reference_flops
        )
        scores: List[CandidateMultiScore] = []

        for cand in candidates:
            if cand.pathway_type in evaluators:
                eval_fn = evaluators[cand.pathway_type]
                is_corr, ref_ms, cand_ms, verif_ms, ref_mem, cand_mem = eval_fn()
                score = self.ranker.evaluate_candidate(
                    candidate=cand,
                    is_correct=is_corr,
                    measured_ref_ms=ref_ms,
                    measured_cand_ms=cand_ms,
                    verification_ms=verif_ms,
                    ref_mem_bytes=ref_mem,
                    cand_mem_bytes=cand_mem,
                )
                scores.append(score)

        ranked = self.ranker.rank_candidates(scores)
        return ranked[0] if ranked else None
