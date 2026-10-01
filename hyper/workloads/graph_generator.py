"""
hyper/workloads/graph_generator.py
==================================
Procedural Composed Workload Graph Generator for LEO/HYPER.
Implements Sections 46, 47, 48:
- Procedurally generates composed computational DAGs
- Explicit patterns: ADD->MUL->FMA, LOAD->ADD->STORE, MATMUL->REDUCE, CONV->ACTIVATION->REDUCE, BRANCH->PHI->STORE
- Arbitrary composed randomized graphs with recorded seeds
- Generates 2,000+ composed execution test cases
"""

from __future__ import annotations
import random
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from hyper.universal_ir.opcodes import Opcode
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.program import UniversalIRProgram
from hyper.semantics.types import DataType, TensorType


class ProceduralGraphGenerator:
    """Generates deterministic composed Universal IR graphs for differential testing."""

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)
        self.np_rng = np.random.RandomState(seed)

    def generate_add_mul_fma(self, M: int = 8, N: int = 8) -> Tuple[UniversalIRProgram, Dict[str, np.ndarray]]:
        """Pattern 1: ADD -> MUL -> FMA"""
        p = UniversalIRProgram(name="pattern_add_mul_fma")
        t_type = TensorType(shape=(M, N), dtype=DataType.FP32)
        p.add_input("A", t_type)
        p.add_input("B", t_type)
        p.add_input("C", t_type)
        p.add_input("D", t_type)

        p.add_instruction(UniversalOp(opcode=Opcode.ADD, result_id="add1", result_type=t_type, operands=("A", "B")))
        p.add_instruction(UniversalOp(opcode=Opcode.MUL, result_id="mul1", result_type=t_type, operands=("add1", "C")))
        p.add_instruction(UniversalOp(opcode=Opcode.FMA, result_id="out", result_type=t_type, operands=("mul1", "D", "A")))
        p.add_output("out")

        inputs = {
            "A": self.np_rng.randn(M, N).astype(np.float32),
            "B": self.np_rng.randn(M, N).astype(np.float32),
            "C": self.np_rng.randn(M, N).astype(np.float32),
            "D": self.np_rng.randn(M, N).astype(np.float32),
        }
        return p, inputs

    def generate_load_add_store(self, M: int = 16) -> Tuple[UniversalIRProgram, Dict[str, np.ndarray]]:
        """Pattern 2: LOAD -> ADD -> STORE"""
        p = UniversalIRProgram(name="pattern_load_add_store")
        t_type = TensorType(shape=(M,), dtype=DataType.FP32)
        p.add_input("SrcA", t_type)
        p.add_input("SrcB", t_type)

        p.add_instruction(UniversalOp(opcode=Opcode.LOAD, result_id="regA", result_type=t_type, operands=("SrcA",)))
        p.add_instruction(UniversalOp(opcode=Opcode.LOAD, result_id="regB", result_type=t_type, operands=("SrcB",)))
        p.add_instruction(UniversalOp(opcode=Opcode.ADD, result_id="sum_val", result_type=t_type, operands=("regA", "regB")))
        p.add_instruction(UniversalOp(opcode=Opcode.STORE, result_id="out", result_type=t_type, operands=("sum_val",)))
        p.add_output("out")

        inputs = {
            "SrcA": self.np_rng.randn(M).astype(np.float32),
            "SrcB": self.np_rng.randn(M).astype(np.float32),
        }
        return p, inputs

    def generate_matmul_reduce(self, M: int = 8, K: int = 8, N: int = 8) -> Tuple[UniversalIRProgram, Dict[str, np.ndarray]]:
        """Pattern 3: MATMUL -> REDUCE"""
        p = UniversalIRProgram(name="pattern_matmul_reduce")
        p.add_input("A", TensorType(shape=(M, K), dtype=DataType.FP32))
        p.add_input("B", TensorType(shape=(K, N), dtype=DataType.FP32))

        p.add_instruction(UniversalOp(opcode=Opcode.MATMUL, result_id="mm", result_type=TensorType(shape=(M, N), dtype=DataType.FP32), operands=("A", "B")))
        p.add_instruction(
            UniversalOp(
                opcode=Opcode.REDUCE_SUM,
                result_id="out",
                result_type=TensorType(shape=(M,), dtype=DataType.FP32),
                operands=("mm",),
                attributes={"axis": 1, "keepdims": False},
            )
        )
        p.add_output("out")

        inputs = {
            "A": self.np_rng.randn(M, K).astype(np.float32),
            "B": self.np_rng.randn(K, N).astype(np.float32),
        }
        return p, inputs

    def generate_conv_activation_reduce(self) -> Tuple[UniversalIRProgram, Dict[str, np.ndarray]]:
        """Pattern 4: CONV -> ACTIVATION -> REDUCE"""
        p = UniversalIRProgram(name="pattern_conv_act_reduce")
        p.add_input("X", TensorType(shape=(1, 1, 6, 6), dtype=DataType.FP32))
        p.add_input("W", TensorType(shape=(1, 1, 3, 3), dtype=DataType.FP32))

        p.add_instruction(
            UniversalOp(
                opcode=Opcode.CONV2D,
                result_id="conv",
                result_type=TensorType(shape=(1, 1, 4, 4), dtype=DataType.FP32),
                operands=("X", "W"),
                attributes={"stride": 1, "padding": 0},
            )
        )
        p.add_instruction(
            UniversalOp(
                opcode=Opcode.RELU,
                result_id="act",
                result_type=TensorType(shape=(1, 1, 4, 4), dtype=DataType.FP32),
                operands=("conv",),
            )
        )
        p.add_instruction(
            UniversalOp(
                opcode=Opcode.REDUCE_MEAN,
                result_id="out",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("act",),
            )
        )
        p.add_output("out")

        inputs = {
            "X": self.np_rng.randn(1, 1, 6, 6).astype(np.float32),
            "W": self.np_rng.randn(1, 1, 3, 3).astype(np.float32),
        }
        return p, inputs

    def generate_branch_phi_store(self, N: int = 8) -> Tuple[UniversalIRProgram, Dict[str, np.ndarray]]:
        """Pattern 5: BRANCH -> PHI -> STORE"""
        p = UniversalIRProgram(name="pattern_branch_phi_store")
        t_type = TensorType(shape=(N,), dtype=DataType.FP32)
        b_type = TensorType(shape=(N,), dtype=DataType.BOOL)

        p.add_input("Cond", b_type)
        p.add_input("ValTrue", t_type)
        p.add_input("ValFalse", t_type)

        p.add_instruction(UniversalOp(opcode=Opcode.PHI, result_id="phi_out", result_type=t_type, operands=("Cond", "ValTrue", "ValFalse")))
        p.add_instruction(UniversalOp(opcode=Opcode.STORE, result_id="out", result_type=t_type, operands=("phi_out",)))
        p.add_output("out")

        inputs = {
            "Cond": self.np_rng.rand(N) > 0.5,
            "ValTrue": self.np_rng.randn(N).astype(np.float32),
            "ValFalse": self.np_rng.randn(N).astype(np.float32),
        }
        return p, inputs

    def generate_random_composed_dag(self, case_id: int) -> Tuple[UniversalIRProgram, Dict[str, np.ndarray]]:
        """Generates an arbitrary valid mathematical composed DAG."""
        local_rng = random.Random(case_id * 10007 + 42)
        local_np = np.random.RandomState(case_id * 10007 + 42)

        p = UniversalIRProgram(name=f"random_composed_{case_id}")
        shape = (4, 4)
        t_type = TensorType(shape=shape, dtype=DataType.FP32)

        # 2 to 4 inputs
        num_inputs = local_rng.randint(2, 4)
        input_names = [f"In_{i}" for i in range(num_inputs)]
        inputs = {}
        for in_name in input_names:
            p.add_input(in_name, t_type)
            inputs[in_name] = local_np.randn(*shape).astype(np.float32)

        available_vars = list(input_names)
        num_ops = local_rng.randint(3, 7)

        binary_ops = [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.MIN, Opcode.MAX]
        unary_ops = [Opcode.RELU, Opcode.GELU, Opcode.NEG, Opcode.ABS, Opcode.TANH]

        for op_idx in range(num_ops):
            res_id = f"t_{op_idx}"
            if local_rng.random() < 0.65:
                # Binary op
                op_code = local_rng.choice(binary_ops)
                op1 = local_rng.choice(available_vars)
                op2 = local_rng.choice(available_vars)
                p.add_instruction(UniversalOp(opcode=op_code, result_id=res_id, result_type=t_type, operands=(op1, op2)))
            else:
                # Unary op
                op_code = local_rng.choice(unary_ops)
                op1 = local_rng.choice(available_vars)
                p.add_instruction(UniversalOp(opcode=op_code, result_id=res_id, result_type=t_type, operands=(op1,)))

            available_vars.append(res_id)

        # Designate final result as output
        p.add_output(available_vars[-1])
        return p, inputs
