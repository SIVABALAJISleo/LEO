"""
hyper/upe/__init__.py
=====================
HYPER UPE — Computational Escape and Verified Algorithm Discovery System.

A scientific system that discovers when a required computational result
can be obtained through a different, cheaper, verifiably correct pathway.
"""

from hyper.upe.contract import WorkloadContract, ValidationMode, ExactnessRequirement
from hyper.upe.necessity import ComputationalNecessityAnalyzer, NecessityReport
from hyper.upe.algebra import PathAlgebra, TransformationRule
from hyper.upe.generator import AlternativePathwayGenerator, CandidatePathway
from hyper.upe.compiler import SearchSpaceCompiler, SearchBudget, SearchResult
from hyper.upe.cegis import CounterexampleHunter, CounterexampleRecord
from hyper.upe.validation import ValidationStack, ValidationLevel, ValidationOutcome, VerificationResult
from hyper.upe.memory import PathMemory, SQLitePathwayStore, ContractAwareCache
from hyper.upe.execution import ResourceAwareExecutionPlanner, ExecutionTarget
from hyper.upe.benchmark import BenchmarkTruthSystem, BenchmarkRunRecord
from hyper.upe.learning import AdaptivePathwayLearner
from hyper.upe.engine import UnseenPathwayEngine, PipelineReport

__all__ = [
    "WorkloadContract",
    "ValidationMode",
    "ExactnessRequirement",
    "ComputationalNecessityAnalyzer",
    "NecessityReport",
    "PathAlgebra",
    "TransformationRule",
    "AlternativePathwayGenerator",
    "CandidatePathway",
    "SearchSpaceCompiler",
    "SearchBudget",
    "SearchResult",
    "CounterexampleHunter",
    "CounterexampleRecord",
    "ValidationStack",
    "ValidationLevel",
    "ValidationOutcome",
    "VerificationResult",
    "PathMemory",
    "SQLitePathwayStore",
    "ContractAwareCache",
    "ResourceAwareExecutionPlanner",
    "ExecutionTarget",
    "BenchmarkTruthSystem",
    "BenchmarkRunRecord",
    "AdaptivePathwayLearner",
    "UnseenPathwayEngine",
    "PipelineReport",
]
