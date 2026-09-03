"""
hyper_v3/intelligence/necessity.py
Autonomous 15-dimensional necessity analysis engine for HYPER 3.0.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np

from hyper_v3.frontend.contract_parser import ExecutionContract, ExecutionTrack
from hyper_v3.ir.operation import NecessityStatus


@dataclass
class NecessityReport:
    workload_name: str
    track: ExecutionTrack
    overall_status: NecessityStatus
    dimension_scores: Dict[str, float]
    details: Dict[str, Any]
    work_avoidance_potential: float
    recommended_strategy: str


class NecessityAnalyzer:
    """Evaluates 15 dimensions of computational necessity."""

    @staticmethod
    def analyze(
        workload_name: str,
        contract: ExecutionContract,
        tensor_inputs: Optional[Dict[str, np.ndarray]] = None,
        runtime_context: Optional[Dict[str, Any]] = None
    ) -> NecessityReport:
        scores: Dict[str, float] = {}
        details: Dict[str, Any] = {}
        ctx = runtime_context or {}
        inputs = tensor_inputs or {}

        # 1. Output Consumption Necessity
        scores["output_consumption"] = 1.0

        # 2. Mathematical Irreducibility
        scores["irreducibility"] = 0.85 if contract.track == ExecutionTrack.EXACT else 0.40

        # 3. Precision Sensitivity
        scores["precision_sensitivity"] = 1.0 if contract.precision_target.value in ["FP64", "FP32"] else 0.5

        # 4. Temporal Redundancy
        temporal_coherence = ctx.get("temporal_coherence", 0.0)
        scores["temporal_redundancy"] = float(temporal_coherence)

        # 5. Spatial Redundancy
        spatial_smoothness = ctx.get("spatial_smoothness", 0.0)
        scores["spatial_redundancy"] = float(spatial_smoothness)

        # 6. Algebraic Simplifiability
        scores["algebraic_simplifiability"] = 0.3 if "conv" in workload_name or "gemm" in workload_name else 0.1

        # 7. Low-Rank Compressibility
        has_matrices = any(isinstance(v, np.ndarray) and v.ndim == 2 for v in inputs.values())
        scores["low_rank_compressibility"] = 0.65 if has_matrices and contract.allow_low_rank else 0.0

        # 8. Sparsity / Zero Concentration
        sparsity = 0.0
        if inputs:
            sparsities = [float(np.count_nonzero(v == 0) / v.size) for v in inputs.values() if isinstance(v, np.ndarray) and v.size > 0]
            if sparsities:
                sparsity = max(sparsities)
        scores["sparsity_concentration"] = sparsity

        # 9. Invariant / Memoization Opportunity
        scores["memoization_potential"] = 1.0 if ctx.get("is_repeat_query", False) else 0.2

        # 10. Hardware-Algorithm Match
        scores["hardware_affinity"] = 0.85

        # 11. Statistical Sufficiency
        scores["statistical_sufficiency"] = 0.7 if "monte_carlo" in workload_name or "sampling" in workload_name else 0.1

        # 12. Information Density
        scores["information_density"] = 0.8 if contract.track == ExecutionTrack.EXACT else 0.5

        # 13. Dynamic Dependency Necessity
        scores["dependency_necessity"] = 0.9

        # 14. Speculative / Early Termination Potential
        scores["early_termination_potential"] = 0.8 if contract.allow_early_termination else 0.0

        # 15. Contract Bound Laxity
        scores["contract_laxity"] = 0.0 if contract.track == ExecutionTrack.EXACT else min(1.0, contract.max_relative_error * 10)

        # Work Avoidance Potential Calculation
        if contract.track == ExecutionTrack.EXACT:
            avoidance = scores["algebraic_simplifiability"] * 0.2 + (0.8 if ctx.get("cache_hit", False) else 0.0)
            overall = NecessityStatus.MANDATORY if not ctx.get("cache_hit", False) else NecessityStatus.REUSABLE
            rec_strat = "vectorized_blas" if not ctx.get("cache_hit", False) else "cache_bypass"
        else:
            avoidance = (
                scores["temporal_redundancy"] * 0.3 +
                scores["spatial_redundancy"] * 0.2 +
                scores["low_rank_compressibility"] * 0.25 +
                scores["sparsity_concentration"] * 0.25 +
                scores["early_termination_potential"] * 0.2
            )
            avoidance = min(0.95, max(0.0, avoidance))
            overall = NecessityStatus.TRANSFORMABLE if avoidance > 0.3 else NecessityStatus.MANDATORY
            rec_strat = "contract_aware_reformulation"

        return NecessityReport(
            workload_name=workload_name,
            track=contract.track,
            overall_status=overall,
            dimension_scores=scores,
            details=details,
            work_avoidance_potential=avoidance,
            recommended_strategy=rec_strat
        )
