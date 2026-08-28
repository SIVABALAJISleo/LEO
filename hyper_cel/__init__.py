"""
hyper_cel: Contractual Elimination Layer Engine Package
"""

from hyper_cel.contract.contract import (
    ComputationalContract,
    ExactContract,
    NumericContract,
    PerceptualContract
)
from hyper_cel.contract.verifier import ContractVerifier
from hyper_cel.prediction.predictor import (
    LowRankPredictor,
    KANSplinePredictor,
    SpeculativeDraftPredictor
)
from hyper_cel.prediction.residual import ResidualEngine
from hyper_cel.reuse.exact_cache import ExactResultCache, ComputationalDNA
from hyper_cel.reuse.temporal_cache import ComputationReservoir, TemporalFrameBuffer
from hyper_cel.execution.cpu import CPUExecutionBackend
from hyper_cel.execution.igpu import iGPUExecutionBackend
from hyper_cel.execution.hybrid import HybridCPUiGPUPipeline
from hyper_cel.scheduler.cost_model import HyperCostModel, ExecutionCandidate
from hyper_cel.runtime import HyperCELRuntime

__all__ = [
    "ComputationalContract",
    "ExactContract",
    "NumericContract",
    "PerceptualContract",
    "ContractVerifier",
    "LowRankPredictor",
    "KANSplinePredictor",
    "SpeculativeDraftPredictor",
    "ResidualEngine",
    "ExactResultCache",
    "ComputationalDNA",
    "ComputationReservoir",
    "TemporalFrameBuffer",
    "CPUExecutionBackend",
    "iGPUExecutionBackend",
    "HybridCPUiGPUPipeline",
    "HyperCostModel",
    "ExecutionCandidate",
    "HyperCELRuntime"
]
