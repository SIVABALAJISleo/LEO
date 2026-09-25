"""
hyper/discovery/adversarial.py
==============================
Adversarial Workload Generator and Holdout Set System.

Generates workloads designed specifically to defeat shortcuts, expose numerical
instabilities, and test generalization across:
- DISCOVERY SET
- VALIDATION SET
- BLIND HOLDOUT SET

Adversarial profiles:
- Prime and pathological dimensions (e.g., 1009 x 1013)
- Catastrophic cancellation (x - y where x ≈ y)
- Extreme dynamic range (1e-15 to 1e15)
- Ultra-sparse vs dense
- Memory-bound streaming vs Compute-bound intensive
"""

from __future__ import annotations

import dataclasses
import enum
import uuid
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from hyper.discovery.cir import CIRGraph, CIRNode, CIRTensorMeta, DataType, OpType
from hyper.discovery.contract import VerificationMode, WorkloadContract


class WorkloadCategory(str, enum.Enum):
    DISCOVERY_SET = "DISCOVERY_SET"
    VALIDATION_SET = "VALIDATION_SET"
    BLIND_HOLDOUT_SET = "BLIND_HOLDOUT_SET"


class AdversarialType(str, enum.Enum):
    PRIME_DIMENSIONS = "PRIME_DIMENSIONS"
    CATASTROPHIC_CANCELLATION = "CATASTROPHIC_CANCELLATION"
    EXTREME_DYNAMIC_RANGE = "EXTREME_DYNAMIC_RANGE"
    ULTRA_SPARSE = "ULTRA_SPARSE"
    MEMORY_BOUND = "MEMORY_BOUND"
    COMPUTE_BOUND = "COMPUTE_BOUND"
    ILL_CONDITIONED = "ILL_CONDITIONED"


@dataclasses.dataclass
class AdversarialWorkload:
    workload_id: str
    name: str
    category: WorkloadCategory
    adversarial_type: AdversarialType
    graph: CIRGraph
    contract: WorkloadContract
    sample_inputs: Dict[str, Any]
    intended_challenge: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "name": self.name,
            "category": self.category.value,
            "adversarial_type": self.adversarial_type.value,
            "intended_challenge": self.intended_challenge,
            "contract": self.contract.to_dict(),
            "graph": self.graph.to_dict(),
        }


class AdversarialWorkloadGenerator:
    """
    Generator of rigorous adversarial and holdout workloads.
    """

    def __init__(self, seed: int = 1337):
        self.rng = np.random.RandomState(seed)

    def generate_prime_dimensions_gemm(self, category: WorkloadCategory = WorkloadCategory.BLIND_HOLDOUT_SET) -> AdversarialWorkload:
        """
        Matrix multiplication with prime dimensions (e.g. 71 x 113 @ 113 x 97)
        defeating power-of-two tiling assumptions.
        """
        M, K, N = 71, 113, 97
        g = CIRGraph(name=f"gemm_primes_{M}_{K}_{N}")
        in_a = g.add_input("A", shape=(M, K), dtype=DataType.FP32)
        in_b = g.add_input("B", shape=(K, N), dtype=DataType.FP32)
        op_mm = g.add_op(OpType.MATMUL, [in_a, in_b], name="result", output_meta=CIRTensorMeta(shape=(M, N), dtype=DataType.FP32))
        g.mark_output(op_mm)

        contract = WorkloadContract(
            contract_id=f"c_prime_{M}_{K}_{N}",
            workload_name=f"prime_gemm_{M}_{K}_{N}",
            required_outputs=["result"],
            exactness_mode=VerificationMode.MODE_2_NUMERIC_EXACT,
        )

        inputs = {
            "A": self.rng.randn(M, K).astype(np.float32),
            "B": self.rng.randn(K, N).astype(np.float32),
        }

        return AdversarialWorkload(
            workload_id=f"adv_prime_{uuid.uuid4().hex[:8]}",
            name=f"Prime_Dimensions_GEMM_{M}x{K}x{N}",
            category=category,
            adversarial_type=AdversarialType.PRIME_DIMENSIONS,
            graph=g,
            contract=contract,
            sample_inputs=inputs,
            intended_challenge=f"Defeat standard tile-size power-of-2 alignments using prime dimensions ({M}x{K}x{N}).",
        )

    def generate_catastrophic_cancellation(self, category: WorkloadCategory = WorkloadCategory.BLIND_HOLDOUT_SET) -> AdversarialWorkload:
        """
        Calculates (x + eps) - x where eps is near machine precision.
        Tests whether approximations, low-rank, or imprecise reassociation corrupt output.
        """
        N = 256
        g = CIRGraph(name="cancellation_test")
        in_x = g.add_input("X", shape=(N,), dtype=DataType.FP32)
        in_eps = g.add_input("EPS", shape=(N,), dtype=DataType.FP32)

        op_add = g.add_op(OpType.ADD, [in_x, in_eps], name="sum_val", output_meta=CIRTensorMeta(shape=(N,), dtype=DataType.FP32))
        op_sub = g.add_op(OpType.SUB, [op_add, in_x], name="result", output_meta=CIRTensorMeta(shape=(N,), dtype=DataType.FP32))
        g.mark_output(op_sub)

        contract = WorkloadContract(
            contract_id="c_cancellation",
            workload_name="cancellation_adversarial",
            required_outputs=["result"],
            exactness_mode=VerificationMode.MODE_2_NUMERIC_EXACT,
        )

        base = np.full(N, 1e4, dtype=np.float32)
        eps = np.full(N, 1e-2, dtype=np.float32)
        inputs = {"X": base, "EPS": eps}

        return AdversarialWorkload(
            workload_id=f"adv_cancel_{uuid.uuid4().hex[:8]}",
            name="Catastrophic_Cancellation_Stress",
            category=category,
            adversarial_type=AdversarialType.CATASTROPHIC_CANCELLATION,
            graph=g,
            contract=contract,
            sample_inputs=inputs,
            intended_challenge="Expose loss of precision in intermediate floating-point subtractive cancellation.",
        )

    def generate_ultra_sparse(self, category: WorkloadCategory = WorkloadCategory.BLIND_HOLDOUT_SET) -> AdversarialWorkload:
        """
        Workload with 95% zero elements.
        Tests whether sparse specialized kernels are selected over dense GEMMs.
        """
        M, K, N = 64, 64, 64
        g = CIRGraph(name="ultra_sparse_gemm")
        in_a = g.add_input("A", shape=(M, K), dtype=DataType.FP32)
        # Sparse constant weight matrix B
        dense_b = self.rng.randn(K, N).astype(np.float32)
        mask = self.rng.rand(K, N) > 0.95  # 95% zeros
        sparse_b = dense_b * mask

        const_b = g.add_constant("W_sparse", sparse_b)
        op_mm = g.add_op(OpType.MATMUL, [in_a, const_b], name="result", output_meta=CIRTensorMeta(shape=(M, N), dtype=DataType.FP32))
        g.mark_output(op_mm)

        contract = WorkloadContract(
            contract_id="c_ultra_sparse",
            workload_name="ultra_sparse_linear",
            required_outputs=["result"],
            exactness_mode=VerificationMode.MODE_2_NUMERIC_EXACT,
        )

        inputs = {"A": self.rng.randn(M, K).astype(np.float32)}

        return AdversarialWorkload(
            workload_id=f"adv_sparse_{uuid.uuid4().hex[:8]}",
            name="Ultra_Sparse_95_Percent_Linear",
            category=category,
            adversarial_type=AdversarialType.ULTRA_SPARSE,
            graph=g,
            contract=contract,
            sample_inputs=inputs,
            intended_challenge="Exploit 95% sparsity without precision loss.",
        )

    def generate_memory_bound_streaming(self, category: WorkloadCategory = WorkloadCategory.BLIND_HOLDOUT_SET) -> AdversarialWorkload:
        """
        Memory-bound streaming workload with large vectors (arithmetic intensity < 0.2 FLOP/byte).
        """
        N = 250000  # 1 MB vector
        g = CIRGraph(name="memory_bound_streaming")
        in_x = g.add_input("X", shape=(N,), dtype=DataType.FP32)
        in_y = g.add_input("Y", shape=(N,), dtype=DataType.FP32)
        in_z = g.add_input("Z", shape=(N,), dtype=DataType.FP32)

        op_mul = g.add_op(OpType.MUL, [in_x, in_y], name="xy", output_meta=CIRTensorMeta(shape=(N,), dtype=DataType.FP32))
        op_add = g.add_op(OpType.ADD, [op_mul, in_z], name="result", output_meta=CIRTensorMeta(shape=(N,), dtype=DataType.FP32))
        g.mark_output(op_add)

        contract = WorkloadContract(
            contract_id="c_mem_stream",
            workload_name="streaming_triad",
            required_outputs=["result"],
            exactness_mode=VerificationMode.MODE_1_BIT_EXACT,
        )

        inputs = {
            "X": self.rng.randn(N).astype(np.float32),
            "Y": self.rng.randn(N).astype(np.float32),
            "Z": self.rng.randn(N).astype(np.float32),
        }

        return AdversarialWorkload(
            workload_id=f"adv_mem_{uuid.uuid4().hex[:8]}",
            name="Memory_Bound_Triad_Stream",
            category=category,
            adversarial_type=AdversarialType.MEMORY_BOUND,
            graph=g,
            contract=contract,
            sample_inputs=inputs,
            intended_challenge="Memory bandwidth saturation with near-zero compute reuse.",
        )

    def generate_full_suite(self) -> Dict[WorkloadCategory, List[AdversarialWorkload]]:
        """Generate balanced suite partitioned into Discovery, Validation, and Blind Holdout sets."""
        return {
            WorkloadCategory.DISCOVERY_SET: [
                self.generate_prime_dimensions_gemm(WorkloadCategory.DISCOVERY_SET),
                self.generate_ultra_sparse(WorkloadCategory.DISCOVERY_SET),
            ],
            WorkloadCategory.VALIDATION_SET: [
                self.generate_catastrophic_cancellation(WorkloadCategory.VALIDATION_SET),
                self.generate_memory_bound_streaming(WorkloadCategory.VALIDATION_SET),
            ],
            WorkloadCategory.BLIND_HOLDOUT_SET: [
                self.generate_prime_dimensions_gemm(WorkloadCategory.BLIND_HOLDOUT_SET),
                self.generate_catastrophic_cancellation(WorkloadCategory.BLIND_HOLDOUT_SET),
                self.generate_ultra_sparse(WorkloadCategory.BLIND_HOLDOUT_SET),
                self.generate_memory_bound_streaming(WorkloadCategory.BLIND_HOLDOUT_SET),
            ],
        }
