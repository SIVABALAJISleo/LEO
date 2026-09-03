"""
hyper_v3/search/candidate_generator.py
Generates composable strategy candidates for computation graphs.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from hyper_v3.frontend.contract_parser import ExecutionContract, ExecutionTrack
from hyper_v3.ir.operation import DeviceType


@dataclass
class StrategyCandidate:
    candidate_id: str
    strategy_name: str
    target_device: DeviceType
    use_low_rank: bool = False
    use_sparsity: bool = False
    use_memoization: bool = False
    use_fusion: bool = False
    tile_size: int = 32
    predicted_latency_us: float = 0.0
    predicted_vwa: float = 0.0  # Verified work avoidance potential
    transformations: List[str] = field(default_factory=list)


class CandidateGenerator:
    """Explores valid combinations of optimizations under contract rules."""

    @staticmethod
    def generate_candidates(workload_name: str, contract: ExecutionContract) -> List[StrategyCandidate]:
        candidates: List[StrategyCandidate] = []

        # Baseline Reference Candidate
        candidates.append(StrategyCandidate(
            candidate_id=f"{workload_name}_baseline_cpu",
            strategy_name="baseline_cpu_reference",
            target_device=DeviceType.CPU,
            predicted_vwa=0.0,
            transformations=["exact_reference"]
        ))

        # Vectorized / SIMD CPU Candidate
        candidates.append(StrategyCandidate(
            candidate_id=f"{workload_name}_vectorized_cpu",
            strategy_name="vectorized_simd_cpu",
            target_device=DeviceType.CPU,
            use_fusion=True,
            tile_size=64,
            predicted_vwa=0.05,
            transformations=["simd_avx2", "cache_blocking"]
        ))

        # Intel iGPU Candidate
        candidates.append(StrategyCandidate(
            candidate_id=f"{workload_name}_intel_igpu",
            strategy_name="openvino_igpu_pipeline",
            target_device=DeviceType.IGPU,
            tile_size=32,
            predicted_vwa=0.0,
            transformations=["igpu_subgroups_16", "usm_zero_copy"]
        ))

        # Contract-Aware Candidates
        if contract.track == ExecutionTrack.CONTRACT_AWARE:
            if contract.allow_low_rank:
                candidates.append(StrategyCandidate(
                    candidate_id=f"{workload_name}_low_rank_svd",
                    strategy_name="low_rank_svd_cpu_igpu",
                    target_device=DeviceType.HYBRID,
                    use_low_rank=True,
                    predicted_vwa=0.60,
                    transformations=["randomized_svd_rank_k", "hybrid_cpu_igpu_split"]
                ))
            if contract.allow_sparsity:
                candidates.append(StrategyCandidate(
                    candidate_id=f"{workload_name}_2to4_sparse_igpu",
                    strategy_name="structured_2to4_sparse_igpu",
                    target_device=DeviceType.IGPU,
                    use_sparsity=True,
                    predicted_vwa=0.50,
                    transformations=["2to4_sparsity_compression", "sparse_gemm_kernel"]
                ))
            if contract.allow_temporal_reuse or contract.allow_spatial_reuse:
                candidates.append(StrategyCandidate(
                    candidate_id=f"{workload_name}_semantic_reuse",
                    strategy_name="semantic_lattice_cache_reuse",
                    target_device=DeviceType.CPU,
                    use_memoization=True,
                    predicted_vwa=0.85,
                    transformations=["fingerprint_lookup", "temporal_delta_reconstruction"]
                ))

        return candidates
