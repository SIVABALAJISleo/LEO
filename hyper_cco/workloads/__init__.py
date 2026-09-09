"""
hyper_cco/workloads/__init__.py
===============================
Manifest Workload Suite for HYPER-CCO Computation Elimination Benchmarks.

Provides the 6 canonical manifest workloads:
  1. GEMM_512x512
  2. SPMV_CSR_10K
  3. LLM_SPECULATIVE_32TOK
  4. CBE_RENDER_720P
  5. QSV_AV1_TRANSCODE_1080P
  6. PDE_POISSON_ITERATIVE
"""

from .gemm_512 import Gemm512Workload
from .spmv_csr_10k import SpmvCsr10kWorkload
from .llm_speculative import LlmSpeculativeWorkload
from .cbe_render_720p import CbeRender720pWorkload
from .qsv_media_transcode import QsvMediaTranscodeWorkload
from .pde_poisson import PdePoissonWorkload

__all__ = [
    "Gemm512Workload",
    "SpmvCsr10kWorkload",
    "LlmSpeculativeWorkload",
    "CbeRender720pWorkload",
    "QsvMediaTranscodeWorkload",
    "PdePoissonWorkload",
]
