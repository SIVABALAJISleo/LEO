"""
hyper/universal_ir/__init__.py
==============================
Canonical Universal Computation IR Package for LEO/HYPER.
"""

from hyper.universal_ir.opcodes import Opcode, MemorySpace, MemoryLayout
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.program import UniversalIRProgram

__all__ = [
    "Opcode",
    "MemorySpace",
    "MemoryLayout",
    "UniversalOp",
    "UniversalIRProgram",
]
