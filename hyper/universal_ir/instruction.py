"""
hyper/universal_ir/instruction.py
=================================
Deterministic, content-addressable Universal IR Instruction representation.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from hyper.universal_ir.opcodes import Opcode, MemoryLayout, MemorySpace
from hyper.semantics.types import DataType, TensorType


@dataclass(frozen=True)
class UniversalOp:
    opcode: Opcode
    result_id: str
    result_type: TensorType
    operands: Tuple[Union[str, int, float, bool], ...]
    attributes: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def instruction_id(self) -> str:
        """Deterministic SHA-256 hash of this operation."""
        payload = {
            "opcode": self.opcode.value,
            "result_id": self.result_id,
            "result_type": self.result_type.to_dict(),
            "operands": [
                op if not isinstance(op, float) else f"{op:.17g}"
                for op in self.operands
            ],
            "attributes": {
                k: v for k, v in sorted(self.attributes.items(), key=lambda x: x[0])
            },
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opcode": self.opcode.value,
            "result_id": self.result_id,
            "result_type": self.result_type.to_dict(),
            "operands": list(self.operands),
            "attributes": self.attributes,
            "provenance": self.provenance,
            "instruction_id": self.instruction_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> UniversalOp:
        return cls(
            opcode=Opcode(d["opcode"]),
            result_id=d["result_id"],
            result_type=TensorType.from_dict(d["result_type"]),
            operands=tuple(d.get("operands", [])),
            attributes=d.get("attributes", {}),
            provenance=d.get("provenance", {}),
        )
