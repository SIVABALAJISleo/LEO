"""
HYPER Ω: Autonomous Computational Discovery, Escape, Verification, and Proof Architecture.
Operates on the fundamental principle:
«Change the pathway, not the truth.»
"""

__version__ = "2.0.0-omega"

from hyper_universal.types import (
    ResultTaxonomy,
    MetricProvenance,
    CacheRegime,
    HardwareProvenance,
    ExecutionTarget,
)
from hyper_omega.escape_engine.engine import ComputationalEscapeEngine
from hyper_omega.escape_engine.types import EscapeClass, EscapeHypothesis, EscapeResult
from hyper_omega.search_space_compiler.compiler import SearchSpaceCompiler, CompiledSearchSpace
from hyper_omega.algorithm_discovery.engine import AlgorithmDiscoveryEngine
from hyper_omega.program_evolution.engine import ProgramEvolutionEngine
from hyper_omega.program_evolution.genome import ProgramGenome
from hyper_omega.meta_search.engine import MetaSearchEngine
from hyper_omega.meta_search.strategy_genome import SearchStrategyGenome
from hyper_omega.genealogy.graph import CandidateGenealogyGraph, CandidateNode
from hyper_omega.agents.breakthrough_agent import BreakthroughAgent
from hyper_omega.agents.falsification_agent import FalsificationAgent
from hyper_omega.agents.duel import AgentDiscoveryDuel
from hyper_omega.counterexamples.database import CounterexampleDatabase
from hyper_omega.theorem_engine.engine import TheoremDiscoveryEngine, TheoremStatus
from hyper_omega.instant_path.engine import InstantPathEngine, ExecutionMode
from hyper_omega.orchestrator import HyperOmegaOrchestrator, HyperOmegaExecutionSummary
from hyper_omega.hardware_bridge import (
    DormantSiliconHarvester,
    MicroHardwareCatalog,
    SoftwareDefinedVirtualSilicon,
    HardwareIrrelevanceReport,
    MicroHardwareOption,
)

__all__ = [
    "ResultTaxonomy",
    "MetricProvenance",
    "CacheRegime",
    "HardwareProvenance",
    "ExecutionTarget",
    "ComputationalEscapeEngine",
    "EscapeClass",
    "EscapeHypothesis",
    "EscapeResult",
    "SearchSpaceCompiler",
    "CompiledSearchSpace",
    "AlgorithmDiscoveryEngine",
    "ProgramEvolutionEngine",
    "ProgramGenome",
    "MetaSearchEngine",
    "SearchStrategyGenome",
    "CandidateGenealogyGraph",
    "CandidateNode",
    "BreakthroughAgent",
    "FalsificationAgent",
    "AgentDiscoveryDuel",
    "CounterexampleDatabase",
    "TheoremDiscoveryEngine",
    "TheoremStatus",
    "InstantPathEngine",
    "ExecutionMode",
    "HyperOmegaOrchestrator",
    "HyperOmegaExecutionSummary",
    "DormantSiliconHarvester",
    "MicroHardwareCatalog",
    "SoftwareDefinedVirtualSilicon",
    "HardwareIrrelevanceReport",
    "MicroHardwareOption",
]

