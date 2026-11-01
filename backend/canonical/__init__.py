"""
backend/canonical
=================
Verified Canonical Functional Replacement Engine and Native Runtimes for Project LEO.
Platform: Intel Core i5-12450H (4P+4E, 12T) + Intel UHD Graphics 48-EU.
"""

from .functional_replacement_engine import (
    FunctionalReplacementEngine,
    CurSkeletonFactoringResult,
    OfflineTruncatedSVDResult,
    QuantizedBitPackingResult,
    OutOfCoreTileResult,
)
from .native_runtime_bridge import NativeRuntimeBridge
from .unseen_subsumption_extensions import (
    HodlrCurResult,
    hodlr_banded_cur_gemm,
    ContextualHotColdResult,
    ContextualHotColdFFN,
    contextual_hot_cold_ffn_step,
    RadixPrefixNode,
    RadixPrefixCache,
    L3CoalescedConcurrencyResult,
    benchmark_l3_coalesced_concurrency,
    MeZOInPlaceTrainer,
    RadianceCascadeResult,
    deterministic_radiance_cascade_2d,
)
from .universal_100_contract_closure import (
    HadamardIncoherentResult,
    fwht_inplace,
    hadamard_incoherent_2bit_gemv,
    ChebyshevActionResult,
    chebyshev_matrix_exp_action,
    LookaheadAsyncResult,
    benchmark_lookahead_async_nvme_pipeline,
    RaggedBatchKVResult,
    RaggedContinuousBatcher,
    benchmark_ragged_continuous_batch_and_kv_compression,
    SubspaceMeZOResult,
    OjaSubspaceMeZOTrainer,
    benchmark_subspace_mezo_galore_training,
    QMCControlVariateResult,
    halton_sequence,
    benchmark_qmc_control_variate_subsumption,
)

__all__ = [
    "FunctionalReplacementEngine",
    "CurSkeletonFactoringResult",
    "OfflineTruncatedSVDResult",
    "QuantizedBitPackingResult",
    "OutOfCoreTileResult",
    "NativeRuntimeBridge",
    "HodlrCurResult",
    "hodlr_banded_cur_gemm",
    "ContextualHotColdResult",
    "ContextualHotColdFFN",
    "contextual_hot_cold_ffn_step",
    "RadixPrefixNode",
    "RadixPrefixCache",
    "L3CoalescedConcurrencyResult",
    "benchmark_l3_coalesced_concurrency",
    "MeZOInPlaceTrainer",
    "RadianceCascadeResult",
    "deterministic_radiance_cascade_2d",
    "HadamardIncoherentResult",
    "fwht_inplace",
    "hadamard_incoherent_2bit_gemv",
    "ChebyshevActionResult",
    "chebyshev_matrix_exp_action",
    "LookaheadAsyncResult",
    "benchmark_lookahead_async_nvme_pipeline",
    "RaggedBatchKVResult",
    "RaggedContinuousBatcher",
    "benchmark_ragged_continuous_batch_and_kv_compression",
    "SubspaceMeZOResult",
    "OjaSubspaceMeZOTrainer",
    "benchmark_subspace_mezo_galore_training",
    "QMCControlVariateResult",
    "halton_sequence",
    "benchmark_qmc_control_variate_subsumption",
]
