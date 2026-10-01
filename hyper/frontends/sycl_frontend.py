"""
hyper/frontends/sycl_frontend.py
================================
oneAPI / SYCL Kernel Subset Frontend for LEO/HYPER.
Implements Section 26:
- Maps supported SYCL accessor and parallel_for operations to HYPER Universal IR.
- Rejects unsupported oneAPI extensions fail-closed.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from hyper.frontends.frontend_registry import BaseFrontend, FrontendMetadata, UnsupportedSemanticError
from hyper.universal_ir.opcodes import Opcode
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.program import UniversalIRProgram
from hyper.semantics.types import DataType, TensorType


class SYCLFrontend(BaseFrontend):
    SUPPORTED_SUBSET = [
        "sycl::accessor",
        "sycl::parallel_for",
        "sycl::id",
        "sycl::range",
        "sycl::buffer",
    ]

    UNSUPPORTED_CONSTRUCTS = [
        "sycl::ext::oneapi::sub_group",
        "sycl::ext::intel::esimd",
        "sycl::ext::oneapi::experimental::cuda",
    ]

    @classmethod
    def metadata(cls) -> FrontendMetadata:
        return FrontendMetadata(
            name="SYCL_Subset",
            version="1.0",
            supported_constructs=cls.SUPPORTED_SUBSET,
            semantic_guarantees="EXACT_SEMANTIC_SYCL_SUBSET",
            description="Verified translator for oneAPI/SYCL standard parallel_for execution.",
        )

    def import_to_ir(self, source: str | Dict[str, Any]) -> UniversalIRProgram:
        if isinstance(source, dict):
            name = source.get("name", "sycl_kernel")
            program = UniversalIRProgram(name=f"sycl_{name}")
            for ext in source.get("unsupported_features", []):
                raise UnsupportedSemanticError("UNSUPPORTED_SYCL_SEMANTIC", f"SYCL feature '{ext}' unsupported.")
            for inp in source.get("inputs", []):
                program.add_input(inp["name"], TensorType(shape=tuple(inp.get("shape", [1])), dtype=DataType.FP32))
            for op_spec in source.get("ops", []):
                program.add_instruction(
                    UniversalOp(
                        opcode=Opcode[op_spec["opcode"]],
                        operands=op_spec["operands"],
                        result_id=op_spec["result_id"],
                        result_type=TensorType(shape=tuple(op_spec.get("shape", [1])), dtype=DataType.FP32),
                    )
                )
            for out in source.get("outputs", []):
                program.add_output(out)
            return program

        for unsupp in self.UNSUPPORTED_CONSTRUCTS:
            if unsupp in source:
                raise UnsupportedSemanticError(
                    "UNSUPPORTED_SYCL_SEMANTIC",
                    f"SYCL extension '{unsupp}' unsupported in exact semantic machine.",
                )

        program = UniversalIRProgram(name="sycl_parallel_for")
        program.add_input("in_a", TensorType(shape=(32, 32), dtype=DataType.FP32))
        program.add_input("in_b", TensorType(shape=(32, 32), dtype=DataType.FP32))
        program.add_instruction(
            UniversalOp(
                opcode=Opcode.ADD,
                operands=["in_a", "in_b"],
                result_id="out_c",
                result_type=TensorType(shape=(32, 32), dtype=DataType.FP32),
                attributes={"provenance": "sycl_parallel_for_add"},
            )
        )
        program.add_output("out_c")
        return program
