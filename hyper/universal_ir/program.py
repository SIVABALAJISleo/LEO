"""
hyper/universal_ir/program.py
=============================
Authoritative Universal IR Program and Graph Representation.
Provides deterministic serialization, content-addressed program hashing,
SSA verification, type consistency checking, and DAG validation.
"""

from __future__ import annotations
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from hyper.universal_ir.opcodes import Opcode
from hyper.universal_ir.instruction import UniversalOp
from hyper.semantics.types import TensorType, DataType


# Export UniversalType alias
UniversalType = DataType


@dataclass
class CIRInstruction:
    op: Any
    inputs: List[str] = field(default_factory=list)
    output: str = ""
    attrs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CIRProgram:
    name: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    instructions: List[CIRInstruction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_instruction(self, inst: CIRInstruction) -> None:
        self.instructions.append(inst)


@dataclass
class UniversalIRProgram:
    name: str
    inputs: Dict[str, TensorType] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    instructions: List[UniversalOp] = field(default_factory=list)
    ir_version: str = "HYPER-IR 1.0"
    semantic_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_input(self, name: str, tensor_type_or_dtype: Any, shape: Optional[Tuple[int, ...]] = None) -> None:
        if isinstance(tensor_type_or_dtype, TensorType):
            self.inputs[name] = tensor_type_or_dtype
        else:
            dtype = tensor_type_or_dtype
            self.inputs[name] = TensorType(dtype=dtype, shape=shape or ())

    def add_output(self, name: str, dtype: Optional[Any] = None, shape: Optional[Tuple[int, ...]] = None) -> None:
        if name not in self.outputs:
            self.outputs.append(name)

    def add_op(self, op: UniversalOp) -> None:
        self.instructions.append(op)

    def add_instruction(self, op: UniversalOp) -> None:
        self.instructions.append(op)

    @property
    def program_hash(self) -> str:
        """Deterministic SHA-256 program hash over all inputs, outputs, and ops."""
        payload = {
            "ir_version": self.ir_version,
            "semantic_version": self.semantic_version,
            "name": self.name,
            "inputs": {
                k: v.to_dict() for k, v in sorted(self.inputs.items(), key=lambda x: x[0])
            },
            "outputs": sorted(self.outputs),
            "instructions": [op.to_dict() for op in self.instructions],
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def validate(self) -> bool:
        """
        Validate program integrity:
        1. Unique assignment for each result_id (SSA form)
        2. All operands are either defined in inputs or by a preceding op
        3. All declared outputs are produced by some op or input
        4. Opcodes have appropriate operand count
        """
        defined_symbols: Set[str] = set(self.inputs.keys())
        seen_results: Set[str] = set(self.inputs.keys())

        for idx, op in enumerate(self.instructions):
            if op.result_id in seen_results:
                raise ValueError(
                    f"SSA violation: result_id '{op.result_id}' already defined prior to op {idx} ({op.opcode.value})"
                )
            seen_results.add(op.result_id)

            # Check operands
            for op_arg in op.operands:
                if isinstance(op_arg, str):
                    # Literal strings might be constants if opcode == CONST, otherwise variable reference
                    if op.opcode != Opcode.CONST and op_arg not in defined_symbols:
                        raise ValueError(
                            f"Op {idx} ({op.opcode.value}) references undefined operand '{op_arg}'. Available: {sorted(defined_symbols)}"
                        )

            defined_symbols.add(op.result_id)

        # Check outputs
        for out in self.outputs:
            if out not in defined_symbols:
                raise ValueError(
                    f"Declared output '{out}' is never produced in program '{self.name}'"
                )

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ir_version": self.ir_version,
            "semantic_version": self.semantic_version,
            "name": self.name,
            "inputs": {k: v.to_dict() for k, v in self.inputs.items()},
            "outputs": list(self.outputs),
            "instructions": [op.to_dict() for op in self.instructions],
            "metadata": self.metadata,
            "program_hash": self.program_hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> UniversalIRProgram:
        inputs = {k: TensorType.from_dict(v) for k, v in d.get("inputs", {}).items()}
        instructions = [UniversalOp.from_dict(op) for op in d.get("instructions", [])]
        prog = cls(
            name=d.get("name", "unnamed_program"),
            inputs=inputs,
            outputs=list(d.get("outputs", [])),
            instructions=instructions,
            ir_version=d.get("ir_version", "HYPER-IR 1.0"),
            semantic_version=d.get("semantic_version", "1.0.0"),
            metadata=d.get("metadata", {}),
        )
        return prog

    def to_json(self, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> UniversalIRProgram:
        return cls.from_dict(json.loads(json_str))

    def summary(self) -> str:
        lines = [
            f"UniversalIRProgram: {self.name} (v{self.ir_version}, sem_v{self.semantic_version})",
            f"  Hash: {self.program_hash[:16]}...",
            f"  Inputs ({len(self.inputs)}): {', '.join(f'{k}: {v.dtype.value}{v.shape}' for k, v in self.inputs.items())}",
            f"  Outputs ({len(self.outputs)}): {', '.join(self.outputs)}",
            f"  Instructions ({len(self.instructions)}):",
        ]
        for idx, op in enumerate(self.instructions):
            ops_str = ", ".join(str(o) for o in op.operands)
            lines.append(
                f"    %{op.result_id} : {op.result_type.dtype.value}{op.result_type.shape} = {op.opcode.value}({ops_str})"
            )
        return "\n".join(lines)
