"""
hyper_x/leaf/discovery/mutation.py
==================================
Mutation operators for algorithmic escape search.
"""

from typing import Any, Dict, List
from .candidate import EscapeCandidate


class CandidateMutator:
    """Mutates candidate parameters (e.g. rank, block size, tolerance)."""

    def mutate_rank(self, candidate: EscapeCandidate, new_rank: int) -> EscapeCandidate:
        cand_copy = EscapeCandidate(**candidate.__dict__)
        cand_copy.candidate_id = f"{candidate.candidate_id}_r{new_rank}"
        cand_copy.assumptions = list(candidate.assumptions) + [f"Rank adjusted to {new_rank}"]
        return cand_copy
