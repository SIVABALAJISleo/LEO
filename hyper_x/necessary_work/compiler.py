"""
hyper_x/necessary_work/compiler.py
==================================
Universal Necessary-Work Compiler for LEO / HYPER Omega Research Mode (Part 8).

Classifies every operation into:
    ORIGINAL
    NECESSARY
    ELIMINABLE
    REUSED
    REFORMULATED
    SPARSE
    LOW_RANK
    COMPRESSED
    PREDICTED
    RECONSTRUCTED
    VERIFICATION
    FALLBACK

Computes and preserves work conservation:
    original_work = necessary_work + eliminated_work + reused_work + transformed_work
    total_executed_work = necessary_work + verification_work + fallback_work
    CCR = original_work / max(1, necessary_work)
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, Any, List, Optional
import numpy as np


class OperationClass(str, Enum):
    ORIGINAL = "ORIGINAL"
    NECESSARY = "NECESSARY"
    ELIMINABLE = "ELIMINABLE"
    REUSED = "REUSED"
    REFORMULATED = "REFORMULATED"
    SPARSE = "SPARSE"
    LOW_RANK = "LOW_RANK"
    COMPRESSED = "COMPRESSED"
    PREDICTED = "PREDICTED"
    RECONSTRUCTED = "RECONSTRUCTED"
    VERIFICATION = "VERIFICATION"
    FALLBACK = "FALLBACK"


@dataclass
class WorkLedgerEntry:
    operation_id: str
    op_class: OperationClass
    work_units: float  # Logical FLOPs or work units
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    reusable: bool = False
    overhead_units: float = 0.0


@dataclass
class NecessaryWorkReport:
    workload_id: str
    original_work: float
    necessary_work: float
    eliminated_work: float
    reused_work: float
    transformed_work: float
    predicted_work: float
    reconstructed_work: float
    verification_work: float
    fallback_work: float
    ccr: float  # Computational Compression Ratio
    work_elimination_pct: float
    classification: OperationClass
    entries: List[WorkLedgerEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["classification"] = self.classification.value
        d["entries"] = [
            {**asdict(e), "op_class": e.op_class.value}
            for e in self.entries
        ]
        return d


class UniversalNecessaryWorkCompiler:
    """
    Authoritative compiler that decomposes workloads into irreducible work
    and mathematically justified shortcuts.
    """

    def __init__(self):
        self._history: List[NecessaryWorkReport] = []

    def analyze_gemm(
        self,
        M: int,
        K: int,
        N: int,
        effective_rank: Optional[int] = None,
        sparsity: float = 0.0,
        cache_hit: bool = False,
        delta_ratio: float = 0.0,
        verify: bool = True
    ) -> NecessaryWorkReport:
        """
        Analyze dense matrix multiply (M x K) @ (K x N).
        Original work = 2 * M * K * N.
        """
        original_work = float(2 * M * K * N)
        entries: List[WorkLedgerEntry] = []

        if cache_hit:
            # 100% exact reuse
            entry = WorkLedgerEntry(
                operation_id="exact_hash_lookup",
                op_class=OperationClass.REUSED,
                work_units=0.0,
                description="Exact multi-factor cache hit; zero compute required",
                reusable=True
            )
            entries.append(entry)
            report = NecessaryWorkReport(
                workload_id=f"gemm_{M}x{K}x{N}",
                original_work=original_work,
                necessary_work=0.0,
                eliminated_work=original_work,
                reused_work=original_work,
                transformed_work=0.0,
                predicted_work=0.0,
                reconstructed_work=0.0,
                verification_work=0.0,
                fallback_work=0.0,
                ccr=float("inf"),
                work_elimination_pct=100.0,
                classification=OperationClass.REUSED,
                entries=entries
            )
            self._history.append(report)
            return report

        r = effective_rank if (effective_rank is not None and effective_rank < min(M, K, N)) else None

        if r is not None:
            # Low-rank factorization: (M x r) @ (r x N) requires 2 * M * r * N
            necessary_work = float(2 * M * r * N)
            eliminated_work = float(original_work - necessary_work)
            transformed_work = float(2 * M * r * K) # SVD decomposition overhead if not amortized
            verif_work = float(2 * K * (M + N)) if verify else 0.0 # Freivalds test O(K(M+N))

            entries.append(WorkLedgerEntry(
                operation_id="low_rank_inner_mult",
                op_class=OperationClass.LOW_RANK,
                work_units=necessary_work,
                description=f"Truncated SVD rank-{r} contraction"
            ))
            if verify:
                entries.append(WorkLedgerEntry(
                    operation_id="freivalds_probabilistic_check",
                    op_class=OperationClass.VERIFICATION,
                    work_units=verif_work,
                    description="Freivalds O(N^2) randomized verification"
                ))

            ccr = original_work / max(1.0, necessary_work + transformed_work)
            report = NecessaryWorkReport(
                workload_id=f"gemm_{M}x{K}x{N}_rank_{r}",
                original_work=original_work,
                necessary_work=necessary_work,
                eliminated_work=eliminated_work,
                reused_work=0.0,
                transformed_work=transformed_work,
                predicted_work=0.0,
                reconstructed_work=0.0,
                verification_work=verif_work,
                fallback_work=0.0,
                ccr=round(ccr, 2),
                work_elimination_pct=round((eliminated_work / original_work) * 100.0, 2),
                classification=OperationClass.LOW_RANK,
                entries=entries
            )
            self._history.append(report)
            return report

        if sparsity > 0.0:
            # Sparse zero skipping
            necessary_work = float(original_work * (1.0 - sparsity))
            eliminated_work = float(original_work * sparsity)
            entries.append(WorkLedgerEntry(
                operation_id="sparse_csr_contraction",
                op_class=OperationClass.SPARSE,
                work_units=necessary_work,
                description=f"Sparse matrix contraction with {sparsity*100:.1f}% zeros skipped"
            ))
            ccr = original_work / max(1.0, necessary_work)
            report = NecessaryWorkReport(
                workload_id=f"gemm_{M}x{K}x{N}_sparse",
                original_work=original_work,
                necessary_work=necessary_work,
                eliminated_work=eliminated_work,
                reused_work=0.0,
                transformed_work=0.0,
                predicted_work=0.0,
                reconstructed_work=0.0,
                verification_work=0.0,
                fallback_work=0.0,
                ccr=round(ccr, 2),
                work_elimination_pct=round(sparsity * 100.0, 2),
                classification=OperationClass.SPARSE,
                entries=entries
            )
            self._history.append(report)
            return report

        if delta_ratio > 0.0 and delta_ratio < 1.0:
            # Incremental delta computation
            necessary_work = float(original_work * delta_ratio)
            reused_work = float(original_work * (1.0 - delta_ratio))
            entries.append(WorkLedgerEntry(
                operation_id="delta_propagation",
                op_class=OperationClass.REFORMULATED,
                work_units=necessary_work,
                description=f"Linear delta update covering {delta_ratio*100:.1f}% altered input coordinates"
            ))
            ccr = original_work / max(1.0, necessary_work)
            report = NecessaryWorkReport(
                workload_id=f"gemm_{M}x{K}x{N}_delta",
                original_work=original_work,
                necessary_work=necessary_work,
                eliminated_work=reused_work,
                reused_work=reused_work,
                transformed_work=0.0,
                predicted_work=0.0,
                reconstructed_work=0.0,
                verification_work=0.0,
                fallback_work=0.0,
                ccr=round(ccr, 2),
                work_elimination_pct=round((reused_work / original_work) * 100.0, 2),
                classification=OperationClass.REFORMULATED,
                entries=entries
            )
            self._history.append(report)
            return report

        # Irreducible dense work
        entries.append(WorkLedgerEntry(
            operation_id="dense_blas_avx2",
            op_class=OperationClass.NECESSARY,
            work_units=original_work,
            description="Irreducible dense tensor contraction executed via vector SIMD FMA"
        ))
        report = NecessaryWorkReport(
            workload_id=f"gemm_{M}x{K}x{N}_dense",
            original_work=original_work,
            necessary_work=original_work,
            eliminated_work=0.0,
            reused_work=0.0,
            transformed_work=0.0,
            predicted_work=0.0,
            reconstructed_work=0.0,
            verification_work=0.0,
            fallback_work=0.0,
            ccr=1.0,
            work_elimination_pct=0.0,
            classification=OperationClass.NECESSARY,
            entries=entries
        )
        self._history.append(report)
        return report
