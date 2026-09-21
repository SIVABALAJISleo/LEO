"""
hyper/discovery package
=======================
Universal Computational Transformation, Discovery & Equivalence Engine (UCTDE).
"""

from hyper.discovery.hypotheses import EpistemicState, UniversalityLevel, ResearchHypothesis, TargetStatus
from hyper.discovery.knowledge_graph import ComputationalKnowledgeGraph, NodeType, EdgeType
from hyper.discovery.proof_engine import ProofDiscoveryEngine, ProofCertificate, ProofStatus
from hyper.discovery.counterexample_engine import CounterexampleDiscoveryEngine, Counterexample, CounterexampleDatabase
from hyper.discovery.universality_ladder import UniversalityLadder, UniversalityBoundaryEngine, BoundaryReport
from hyper.discovery.meta_search import MetaSearchEngine, SearchStrategyType
from hyper.discovery.resource_transcendence import ResourceTranscendenceEngine, ResourceVector, TranscendenceVerdict
from hyper.discovery.self_critique import SelfCritiqueEngine, SelfCritiqueReport
from hyper.discovery.transformation_library import TransformationLibrary, TransformationRule
from hyper.discovery.loop import UniversalDiscoveryLoop, DiscoveryExperimentResult
from hyper.discovery.engine import UniversalComputationalDiscoveryEngine

__all__ = [
    "EpistemicState",
    "UniversalityLevel",
    "ResearchHypothesis",
    "TargetStatus",
    "ComputationalKnowledgeGraph",
    "NodeType",
    "EdgeType",
    "ProofDiscoveryEngine",
    "ProofCertificate",
    "ProofStatus",
    "CounterexampleDiscoveryEngine",
    "Counterexample",
    "CounterexampleDatabase",
    "UniversalityLadder",
    "UniversalityBoundaryEngine",
    "BoundaryReport",
    "MetaSearchEngine",
    "SearchStrategyType",
    "ResourceTranscendenceEngine",
    "ResourceVector",
    "TranscendenceVerdict",
    "SelfCritiqueEngine",
    "SelfCritiqueReport",
    "TransformationLibrary",
    "TransformationRule",
    "UniversalDiscoveryLoop",
    "DiscoveryExperimentResult",
    "UniversalComputationalDiscoveryEngine",
]
