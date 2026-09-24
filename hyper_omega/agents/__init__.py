"""
hyper_omega.agents package
"""
from hyper_omega.agents.counterfactual_engine import CounterfactualEngine, CounterfactualHypothesis
from hyper_omega.agents.breakthrough_agent import BreakthroughAgent, BreakthroughProposal
from hyper_omega.agents.falsification_agent import FalsificationAgent, FalsificationAttackResult
from hyper_omega.agents.duel import AgentDiscoveryDuel, DuelResult

__all__ = [
    "CounterfactualEngine",
    "CounterfactualHypothesis",
    "BreakthroughAgent",
    "BreakthroughProposal",
    "FalsificationAgent",
    "FalsificationAttackResult",
    "AgentDiscoveryDuel",
    "DuelResult",
]
