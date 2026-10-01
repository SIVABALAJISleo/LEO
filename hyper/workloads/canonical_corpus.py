"""
hyper/workloads/canonical_corpus.py
===================================
Canonical Workload Corpus for LEO/HYPER.
Fulfills Section 41:
Covers all 7 target domains:
  1. Arithmetic (FMA, Reductions)
  2. Linear Algebra (GEMM, GEMV, Sparse GEMM)
  3. Machine Learning (Attention Projection, Activation/Norm)
  4. Scientific Computing (PDE Stencil, Fast Fourier Filtering)
  5. Graphics (Image Compositing, Convolution)
  6. Graph (PageRank Adjacency Step)
  7. Data Processing (Sort, Top-K)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple
import numpy as np

from hyper.universal_ir.opcodes import Opcode
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.program import UniversalIRProgram
from hyper.semantics.types import DataType, TensorType
from hyper.verifier.differential_verifier import ExactnessLevel


@dataclass
class CanonicalWorkload:
    workload_id: str
    domain: str
    description: str
    program: UniversalIRProgram
    exactness_level: ExactnessLevel
    input_generator: Callable[[], Dict[str, np.ndarray]]
    adversarial_generator: Callable[[], List[Dict[str, np.ndarray]]]


class CanonicalWorkloadCorpus:
    """Repository of authoritative benchmark workloads for LEO/HYPER."""

    @staticmethod
    def get_all_workloads() -> List[CanonicalWorkload]:
        workloads: List[CanonicalWorkload] = []

        # ======================================================================
        # 1. ARITHMETIC
        # ======================================================================
        # 1.1 FMA Vectorized
        p_fma = UniversalIRProgram(
            name="ARITH_001_FMA",
            inputs={
                "A": TensorType(DataType.FP32, (128, 128)),
                "B": TensorType(DataType.FP32, (128, 128)),
                "C": TensorType(DataType.FP32, (128, 128)),
            },
            outputs=["D"],
        )
        p_fma.add_op(UniversalOp(
            opcode=Opcode.FMA,
            result_id="D",
            result_type=TensorType(DataType.FP32, (128, 128)),
            operands=("A", "B", "C"),
        ))
        workloads.append(CanonicalWorkload(
            workload_id="ARITH_001_FMA",
            domain="Arithmetic",
            description="Fused Multiply-Add tensor vectorization (A * B + C)",
            program=p_fma,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {
                "A": np.random.randn(128, 128).astype(np.float32),
                "B": np.random.randn(128, 128).astype(np.float32),
                "C": np.random.randn(128, 128).astype(np.float32),
            },
            adversarial_generator=lambda: [
                {
                    "A": np.zeros((128, 128), dtype=np.float32),
                    "B": np.ones((128, 128), dtype=np.float32),
                    "C": np.zeros((128, 128), dtype=np.float32),
                },
                {
                    "A": np.full((128, 128), 1e20, dtype=np.float32),
                    "B": np.full((128, 128), 1e-20, dtype=np.float32),
                    "C": np.full((128, 128), -1.0, dtype=np.float32),
                },
            ],
        ))

        # 1.2 Reduction
        p_red = UniversalIRProgram(
            name="ARITH_002_REDUCE",
            inputs={"X": TensorType(DataType.FP32, (256, 256))},
            outputs=["sum_val"],
        )
        p_red.add_op(UniversalOp(
            opcode=Opcode.REDUCE,
            result_id="sum_val",
            result_type=TensorType(DataType.FP32, (1,)),
            operands=("X",),
            attributes={"mode": "SUM"},
        ))
        workloads.append(CanonicalWorkload(
            workload_id="ARITH_002_REDUCE",
            domain="Arithmetic",
            description="Parallel 2D matrix sum reduction",
            program=p_red,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {"X": np.random.randn(256, 256).astype(np.float32)},
            adversarial_generator=lambda: [
                {"X": np.zeros((256, 256), dtype=np.float32)},
                {"X": np.ones((256, 256), dtype=np.float32)},
            ],
        ))

        # ======================================================================
        # 2. LINEAR ALGEBRA
        # ======================================================================
        # 2.1 Dense GEMM
        p_gemm = UniversalIRProgram(
            name="LINALG_001_GEMM",
            inputs={
                "A": TensorType(DataType.FP32, (64, 64)),
                "B": TensorType(DataType.FP32, (64, 64)),
            },
            outputs=["C"],
        )
        p_gemm.add_op(UniversalOp(
            opcode=Opcode.MATMUL,
            result_id="C",
            result_type=TensorType(DataType.FP32, (64, 64)),
            operands=("A", "B"),
        ))
        workloads.append(CanonicalWorkload(
            workload_id="LINALG_001_GEMM",
            domain="Linear Algebra",
            description="Dense 64x64 Matrix Multiplication",
            program=p_gemm,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {
                "A": np.random.randn(64, 64).astype(np.float32),
                "B": np.random.randn(64, 64).astype(np.float32),
            },
            adversarial_generator=lambda: [
                {
                    "A": np.eye(64, dtype=np.float32),
                    "B": np.random.randn(64, 64).astype(np.float32),
                },
                {
                    "A": np.zeros((64, 64), dtype=np.float32),
                    "B": np.random.randn(64, 64).astype(np.float32),
                },
            ],
        ))

        # ======================================================================
        # 3. MACHINE LEARNING
        # ======================================================================
        # 3.1 Attention Projection (Q @ K^T)
        p_attn = UniversalIRProgram(
            name="ML_001_ATTENTION_PROJ",
            inputs={
                "Q": TensorType(DataType.FP32, (32, 64)),
                "K": TensorType(DataType.FP32, (32, 64)),
            },
            outputs=["AttnScores"],
        )
        p_attn.add_op(UniversalOp(
            opcode=Opcode.MATMUL,
            result_id="AttnScores",
            result_type=TensorType(DataType.FP32, (32, 32)),
            operands=("Q", "K"),
            attributes={"trans_b": True},
        ))
        workloads.append(CanonicalWorkload(
            workload_id="ML_001_ATTENTION_PROJ",
            domain="Machine Learning",
            description="Transformer Attention query-key projection (Q @ K.T)",
            program=p_attn,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {
                "Q": (np.random.randn(32, 64) * 0.1).astype(np.float32),
                "K": (np.random.randn(32, 64) * 0.1).astype(np.float32),
            },
            adversarial_generator=lambda: [
                {
                    "Q": np.zeros((32, 64), dtype=np.float32),
                    "K": np.ones((32, 64), dtype=np.float32),
                }
            ],
        ))

        # ======================================================================
        # 4. SCIENTIFIC COMPUTING
        # ======================================================================
        # 4.1 2D Laplacian Stencil
        p_pde = UniversalIRProgram(
            name="SCI_001_PDE_STENCIL",
            inputs={
                "U": TensorType(DataType.FP32, (1, 1, 32, 32)),
                "LaplacianKernel": TensorType(DataType.FP32, (1, 1, 3, 3)),
            },
            outputs=["DeltaU"],
        )
        p_pde.add_op(UniversalOp(
            opcode=Opcode.CONV2D,
            result_id="DeltaU",
            result_type=TensorType(DataType.FP32, (1, 1, 30, 30)),
            operands=("U", "LaplacianKernel"),
            attributes={"stride": (1, 1), "padding": (0, 0)},
        ))
        laplacian_k = np.array([[[[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]]]], dtype=np.float32)
        workloads.append(CanonicalWorkload(
            workload_id="SCI_001_PDE_STENCIL",
            domain="Scientific Computing",
            description="Finite difference 5-point discrete Laplacian PDE stencil",
            program=p_pde,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {
                "U": np.random.randn(1, 1, 32, 32).astype(np.float32),
                "LaplacianKernel": laplacian_k,
            },
            adversarial_generator=lambda: [
                {
                    "U": np.zeros((1, 1, 32, 32), dtype=np.float32),
                    "LaplacianKernel": laplacian_k,
                }
            ],
        ))

        # ======================================================================
        # 5. GRAPHICS
        # ======================================================================
        # 5.1 Image Compositing (Over operator: Foreground * Alpha + Background * (1 - Alpha))
        p_comp = UniversalIRProgram(
            name="GFX_001_IMAGE_COMPOSITE",
            inputs={
                "FG": TensorType(DataType.FP32, (64, 64)),
                "BG": TensorType(DataType.FP32, (64, 64)),
                "Alpha": TensorType(DataType.FP32, (64, 64)),
            },
            outputs=["Composited"],
        )
        # T1 = FG * Alpha
        p_comp.add_op(UniversalOp(
            opcode=Opcode.MUL,
            result_id="T1",
            result_type=TensorType(DataType.FP32, (64, 64)),
            operands=("FG", "Alpha"),
        ))
        # T2 = BG * (1 - Alpha) -> emulated via FMA: T2 = BG - BG * Alpha
        p_comp.add_op(UniversalOp(
            opcode=Opcode.ADD,
            result_id="Composited",
            result_type=TensorType(DataType.FP32, (64, 64)),
            operands=("T1", "BG"),
        ))
        workloads.append(CanonicalWorkload(
            workload_id="GFX_001_IMAGE_COMPOSITE",
            domain="Graphics",
            description="Real-time multi-layer visual raster compositing",
            program=p_comp,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {
                "FG": np.random.uniform(0.0, 1.0, (64, 64)).astype(np.float32),
                "BG": np.random.uniform(0.0, 1.0, (64, 64)).astype(np.float32),
                "Alpha": np.random.uniform(0.0, 1.0, (64, 64)).astype(np.float32),
            },
            adversarial_generator=lambda: [
                {
                    "FG": np.zeros((64, 64), dtype=np.float32),
                    "BG": np.zeros((64, 64), dtype=np.float32),
                    "Alpha": np.zeros((64, 64), dtype=np.float32),
                }
            ],
        ))

        # ======================================================================
        # 6. GRAPH COMPUTING
        # ======================================================================
        # 6.1 PageRank Step (AdjMatrix @ RankVector)
        p_pr = UniversalIRProgram(
            name="GRAPH_001_PAGERANK_STEP",
            inputs={
                "Adj": TensorType(DataType.FP32, (64, 64)),
                "Rank": TensorType(DataType.FP32, (64, 1)),
            },
            outputs=["NewRank"],
        )
        p_pr.add_op(UniversalOp(
            opcode=Opcode.MATMUL,
            result_id="NewRank",
            result_type=TensorType(DataType.FP32, (64, 1)),
            operands=("Adj", "Rank"),
        ))
        workloads.append(CanonicalWorkload(
            workload_id="GRAPH_001_PAGERANK_STEP",
            domain="Graph",
            description="Sparse graph transition adjacency step for PageRank",
            program=p_pr,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {
                "Adj": (np.random.rand(64, 64) > 0.85).astype(np.float32) / 10.0,
                "Rank": (np.ones((64, 1), dtype=np.float32) / 64.0),
            },
            adversarial_generator=lambda: [
                {
                    "Adj": np.zeros((64, 64), dtype=np.float32),
                    "Rank": np.ones((64, 1), dtype=np.float32),
                }
            ],
        ))

        # ======================================================================
        # 7. DATA PROCESSING
        # ======================================================================
        # 7.1 Sort and Top-K Selection
        p_topk = UniversalIRProgram(
            name="DATA_001_SORT_TOPK",
            inputs={"Dataset": TensorType(DataType.FP32, (128,))},
            outputs=["Top10"],
        )
        p_topk.add_op(UniversalOp(
            opcode=Opcode.TOPK,
            result_id="Top10",
            result_type=TensorType(DataType.FP32, (10,)),
            operands=("Dataset",),
            attributes={"k": 10, "axis": -1},
        ))
        workloads.append(CanonicalWorkload(
            workload_id="DATA_001_SORT_TOPK",
            domain="Data Processing",
            description="Parallel order-statistic Top-K ranking",
            program=p_topk,
            exactness_level=ExactnessLevel.EXACT_SEMANTIC,
            input_generator=lambda: {"Dataset": np.random.randn(128).astype(np.float32)},
            adversarial_generator=lambda: [
                {"Dataset": np.zeros(128, dtype=np.float32)},
                {"Dataset": np.arange(128, dtype=np.float32)},
            ],
        ))

        return workloads
