"""
Agent Discovery Duel: Breakthrough Agent proposes pathways,
and Falsification Agent actively attacks them.
Only surviving candidates are retained.
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple
from hyper_universal.contract_ir import ContractIR
from hyper_universal.types import ResultTaxonomy
from hyper_omega.agents.breakthrough_agent import BreakthroughAgent, BreakthroughProposal
from hyper_omega.agents.falsification_agent import FalsificationAgent, FalsificationAttackResult


@dataclass
class DuelResult:
    proposal_id: str
    breakthrough_class: str
    proposed_code: str
    survived_falsification: bool
    attack_results: List[FalsificationAttackResult]
    final_status: ResultTaxonomy


class AgentDiscoveryDuel:
    """
    Coordinates the adversarial interaction between BreakthroughAgent and FalsificationAgent.
    """

    def __init__(self):
        self.breakthrough_agent = BreakthroughAgent()
        self.falsification_agent = FalsificationAgent()
        self.duel_history: List[DuelResult] = []

    def execute_duel(
        self,
        workload_name: str,
        contract: ContractIR,
        nominal_inputs: List[Any],
        reference_fn: Callable[[Any], Any],
    ) -> List[DuelResult]:
        # 1. BreakthroughAgent generates candidate proposals
        proposals = self.breakthrough_agent.propose_breakthroughs(workload_name, contract)
        duel_results = []

        for p in proposals:
            # 2. FalsificationAgent ruthlessly attacks each candidate
            survived, attack_results = self.falsification_agent.attack_candidate(
                candidate_code=p.proposed_code,
                reference_fn=reference_fn,
                contract=contract,
                nominal_inputs=nominal_inputs,
            )

            status = ResultTaxonomy.VERIFIED if survived else ResultTaxonomy.COUNTEREXAMPLE_FOUND

            dr = DuelResult(
                proposal_id=p.proposal_id,
                breakthrough_class=p.breakthrough_class,
                proposed_code=p.proposed_code,
                survived_falsification=survived,
                attack_results=attack_results,
                final_status=status
            )
            duel_results.append(dr)
            self.duel_history.append(dr)

        return duel_results
