"""
hyper/core/ai_research/__init__.py
AI Multi-Agent research system and self-falsification loop.
"""
from hyper.core.ai_research.multi_agent import (
    AgentProposal,
    ProposalStatus,
    ResearchMultiAgentSystem,
)

__all__ = ["AgentProposal", "ProposalStatus", "ResearchMultiAgentSystem"]
