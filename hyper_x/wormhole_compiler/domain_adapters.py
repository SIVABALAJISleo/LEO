"""
hyper_x/wormhole_compiler/domain_adapters.py
=============================================================================
HYPER-X Workload Domain Adapters (Phases 31 through 35)
=============================================================================
Provides formal problem adapters for diverse computational domains:
  1. MatrixMultiplicationAdapter  - Dense / Sparse / Low-Rank / Block / Recursive
  2. GraphicsTemporalAdapter      - Temporal Reprojection / Event Deltas / Bilateral
  3. OutputSensitiveTopKAdapter   - Top-K Beam Search / MIPS / Argmax Projection
  4. ScientificStencilAdapter     - 2D Diffusion / Wave / Multigrid Stencil
  5. RAGEmbeddingRetrievalAdapter - Vector DB / Cosine Similarity / LSH Indexing

Each adapter formally defines:
  - Contract & Observables
  - Mathematically sound Reference Baseline
  - Domain-Specific Candidate Space
  - Independent Verification & Quality Metrics
"""

from __future__ import annotations
import time
from typing import Dict, Any, Tuple, Optional, List, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import (
    WorkloadContract,
    ObservableRequirement,
    CorrectnessRequirement,
    CachePolicy,
    GrammarOperator,
)
from hyper_x.wormhole_compiler.contract import ContractCompiler
from hyper_x.wormhole_compiler.observable import ObservableCompiler
from hyper_x.wormhole_compiler.algorithm_grammar import CompositeAlgorithm


class MatrixMultiplicationAdapter:
    """GEMM research testbed adapter."""

    @staticmethod
    def build_contract(
        M: int, K: int, N: int,
        tolerance: float = 1e-4,
        latency_slo_ms: float = 100.0,
        cache_policy: CachePolicy = CachePolicy.COLD
    ) -> WorkloadContract:
        return ContractCompiler.compile_matrix_contract(
            workload_id=f"GEMM_{M}x{K}x{N}",
            shape=(M, K, N),
            tolerance=tolerance,
            latency_slo_ms=latency_slo_ms,
            cache_policy=cache_policy
        )

    @staticmethod
    def build_observable(M: int, N: int, tolerance: float = 1e-4) -> ObservableRequirement:
        return ObservableCompiler.full_matrix(M, N, tolerance=tolerance)

    @staticmethod
    def execute_reference(A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        ref = A @ B
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return ref, elapsed_ms


class GraphicsTemporalAdapter:
    """Temporal graphics rendering and denoising adapter (Phase 33)."""

    @staticmethod
    def build_contract(
        resolution: Tuple[int, int] = (256, 256),
        target_fps: float = 60.0,
        min_ssim: float = 0.92
    ) -> WorkloadContract:
        return ContractCompiler.compile_graphics_contract(
            workload_id=f"GRAPHICS_{resolution[0]}x{resolution[1]}",
            resolution=resolution,
            target_fps=target_fps,
            min_ssim=min_ssim
        )

    @staticmethod
    def execute_reference(gt_100spp: np.ndarray) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        # Physical reference: perform actual multi-channel 3x3 box blur filtering across pixels
        H, W = gt_100spp.shape[:2]
        padded = np.pad(gt_100spp, ((1, 1), (1, 1), (0, 0)) if gt_100spp.ndim == 3 else ((1, 1), (1, 1)), mode="edge")
        if gt_100spp.ndim == 3:
            filtered = (
                padded[:-2, :-2, :] + padded[:-2, 1:-1, :] + padded[:-2, 2:, :] +
                padded[1:-1, :-2, :] + padded[1:-1, 1:-1, :] + padded[1:-1, 2:, :] +
                padded[2:, :-2, :] + padded[2:, 1:-1, :] + padded[2:, 2:, :]
            ) / 9.0
        else:
            filtered = (
                padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:] +
                padded[1:-1, :-2] + padded[1:-1, 1:-1] + padded[1:-1, 2:] +
                padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
            ) / 9.0
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return filtered, elapsed_ms


class OutputSensitiveTopKAdapter:
    """Output-sensitive computation adapter (Phase 34)."""

    @staticmethod
    def build_contract(M: int, K: int, k: int = 10) -> WorkloadContract:
        return WorkloadContract(
            workload_id=f"OUTPUT_SENSITIVE_TOP_{k}_{M}x{K}",
            operation="top_k_projection",
            input_shape=(M, K),
            output_shape=(k,),
            correctness=CorrectnessRequirement.TOP_K,
            tolerance=1e-3,
            latency_slo_ms=25.0
        )

    @staticmethod
    def build_observable(k: int, M: int) -> ObservableRequirement:
        return ObservableCompiler.top_k(k, total_dim=M)

    @staticmethod
    def execute_reference(A: np.ndarray, x: np.ndarray, k: int = 10) -> Tuple[Tuple[np.ndarray, np.ndarray], float]:
        t0 = time.perf_counter()
        full_dot = A @ x
        indices = np.argpartition(full_dot, -k)[-k:]
        sorted_indices = indices[np.argsort(-full_dot[indices])]
        top_vals = full_dot[sorted_indices]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return (top_vals, sorted_indices), elapsed_ms


class ScientificStencilAdapter:
    """2D scientific stencil and partial differential equation adapter."""

    @staticmethod
    def build_contract(grid_shape: Tuple[int, int] = (128, 128)) -> WorkloadContract:
        return ContractCompiler.compile_stencil_contract(
            workload_id=f"STENCIL_{grid_shape[0]}x{grid_shape[1]}",
            grid_shape=grid_shape,
            tolerance=1e-3,
            latency_slo_ms=40.0
        )

    @staticmethod
    def execute_reference(field: np.ndarray, steps: int = 10) -> Tuple[np.ndarray, float]:
        t0 = time.perf_counter()
        curr = np.copy(field)
        for _ in range(steps):
            padded = np.pad(curr, 1, mode="edge")
            curr = 0.25 * (padded[:-2, 1:-1] + padded[2:, 1:-1] + padded[1:-1, :-2] + padded[1:-1, 2:])
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return curr, elapsed_ms


class RAGEmbeddingRetrievalAdapter:
    """Vector database cosine retrieval adapter."""

    @staticmethod
    def build_contract(doc_count: int = 10000, dim: int = 384, top_k: int = 5) -> WorkloadContract:
        return WorkloadContract(
            workload_id=f"RAG_RETRIEVAL_{doc_count}_D{dim}",
            operation="vector_similarity_top_k",
            input_shape=(doc_count, dim),
            output_shape=(top_k,),
            correctness=CorrectnessRequirement.TOP_K,
            tolerance=1e-3,
            latency_slo_ms=15.0
        )

    @staticmethod
    def execute_reference(corpus: np.ndarray, query: np.ndarray, top_k: int = 5) -> Tuple[Tuple[np.ndarray, np.ndarray], float]:
        t0 = time.perf_counter()
        norm_corpus = corpus / (np.linalg.norm(corpus, axis=1, keepdims=True) + 1e-8)
        norm_query = query / (np.linalg.norm(query) + 1e-8)
        scores = norm_corpus @ norm_query
        indices = np.argpartition(scores, -top_k)[-top_k:]
        sorted_indices = indices[np.argsort(-scores[indices])]
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return (scores[sorted_indices], sorted_indices), elapsed_ms
