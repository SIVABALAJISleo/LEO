"""
hyper_x/leaf/discovery/crossover.py
===================================
Crossover and strategy composition operators for LEAF escape discovery.
"""

from typing import Any, Dict, List
from .candidate import EscapeCandidate, BreakthroughLevel


class StrategyComposer:
    """Composes multiple escape strategies (e.g. Symbolic + Low-Rank)."""

    def compose(self, cand_a: EscapeCandidate, cand_b: EscapeCandidate) -> EscapeCandidate:
        new_id = f"{cand_a.candidate_id}_x_{cand_b.candidate_id}"
        combined_flops = int((cand_a.candidate_work_flops + cand_b.candidate_work_flops) / 2)
        return EscapeCandidate(
            candidate_id=new_id,
            workload_name=cand_a.workload_name,
            pathway_type="HYBRID",
            reference_algorithm=cand_a.reference_algorithm,
            candidate_algorithm=f"hybrid_{cand_a.candidate_algorithm}_{cand_b.candidate_algorithm}",
            contract=cand_a.contract,
            assumptions=list(set(cand_a.assumptions + cand_b.assumptions)),
            representation=f"hybrid({cand_a.representation}, {cand_b.representation})",
            reference_work_flops=cand_a.reference_work_flops,
            candidate_work_flops=combined_flops,
            breakthrough_level=BreakthroughLevel.LEVEL_3,
            failure_conditions=list(set(cand_a.failure_conditions + cand_b.failure_conditions)),
        )
