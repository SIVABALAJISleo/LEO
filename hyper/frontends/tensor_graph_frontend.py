"""
hyper/frontends/tensor_graph_frontend.py
========================================
Generic Tensor Computational Graph Frontend.
Parses ONNX-like and JSON tensor graphs into Universal IR.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import numpy as np

from hyper.frontends.frontend_registry import BaseFrontend, FrontendMetadata, UnsupportedSemanticError
from hyper.universal_ir.opcodes import Opcode
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.program import UniversalIRProgram
from hyper.semantics.types import DataType, TensorType


TENSOR_OP_MAP = {
    "Add": Opcode.ADD,
    "Sub": Opcode.SUB,
    "Mul": Opcode.MUL,
    "Div": Opcode.DIV,
    "MatMul": Opcode.MATMUL,
    "Gemm": Opcode.GEMM,
    "Relu": Opcode.RELU,
    "Gelu": Opcode.GELU,
    "Sigmoid": Opcode.SIGMOID,
    "Tanh": Opcode.TANH,
    "Exp": Opcode.EXP,
    "Log": Opcode.LOG,
    "Sqrt": Opcode.SQRT,
    "Conv": Opcode.CONV2D,
    "ReduceSum": Opcode.REDUCE_SUM,
    "ReduceMean": Opcode.REDUCE_MEAN,
    "Transpose": Opcode.TRANSPOSE,
    "Reshape": Opcode.RESHAPE,
    "Concat": Opcode.CONCAT,
    "Split": Opcode.SPLIT,
    "Softmax": Opcode.SOFTMAX,
}


class TensorGraphFrontend(BaseFrontend):
    """Imports JSON-serialized tensor graphs (ONNX format subset) into Universal IR."""

    @classmethod
    def metadata(cls) -> FrontendMetadata:
        return FrontendMetadata(
            name="TensorGraph",
            version="1.0",
            supported_constructs=list(TENSOR_OP_MAP.keys()),
            semantic_guarantees="EXACT_SEMANTIC_ONNX_SUBSET",
            description="Imports standard ONNX/Tensor JSON computational graphs.",
        )

    def import_to_ir(self, source: Dict[str, Any]) -> UniversalIRProgram:
        name = source.get("name", "tensor_graph")
        program = UniversalIRProgram(name=name)

        # Inputs
        for inp in source.get("inputs", []):
            inp_name = inp["name"]
            shape = tuple(inp.get("shape", [1]))
            dt_str = inp.get("dtype", "FP32")
            dt = DataType[dt_str] if dt_str in DataType.__members__ else DataType.FP32
            program.add_input(inp_name, TensorType(shape=shape, dtype=dt))

        # Nodes
        for node in source.get("nodes", []):
            op_type = node.get("op_type")
            if op_type not in TENSOR_OP_MAP:
                raise UnsupportedSemanticError(
                    str(op_type),
                    f"TensorGraph operator '{op_type}' is not supported in the standard tensor subset.",
                )
            mapped_opcode = TENSOR_OP_MAP[op_type]
            out_name = node.get("output", f"node_{len(program.instructions)}")
            shape = tuple(node.get("output_shape", [1]))
            dt_str = node.get("output_dtype", "FP32")
            dt = DataType[dt_str] if dt_str in DataType.__members__ else DataType.FP32

            op = UniversalOp(
                opcode=mapped_opcode,
                operands=node.get("inputs", []),
                result_id=out_name,
                result_type=TensorType(shape=shape, dtype=dt),
                attributes=node.get("attributes", {}),
            )
            program.add_instruction(op)

        # Outputs
        for out in source.get("outputs", []):
            out_name = out["name"] if isinstance(out, dict) else str(out)
            program.add_output(out_name)

        return program
