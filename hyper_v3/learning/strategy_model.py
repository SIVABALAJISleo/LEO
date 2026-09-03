"""
hyper_v3/learning/strategy_model.py
Predicts optimal strategy classification based on tensor dimensions and contract rules.
"""

from typing import Dict, Any
from hyper_v3.frontend.contract_parser import ExecutionContract, ExecutionTrack


class StrategyModel:
    @staticmethod
    def predict_strategy_class(workload_name: str, contract: ExecutionContract) -> str:
        if contract.track == ExecutionTrack.EXACT:
            return "EXACT_AVX2_BLAS"
        elif "gemm" in workload_name and contract.allow_low_rank:
            return "LOW_RANK_SVD"
        elif "fft" in workload_name and contract.allow_sparsity:
            return "SUBLINEAR_SPARSE_FFT"
        elif contract.allow_temporal_reuse:
            return "SEMANTIC_LATTICE_CACHE"
        return "CONTRACT_AWARE_HYBRID"
