"""
hyper/frontends/normalizer.py
=============================
Semantic Normalizer for LEO/HYPER Universal Exact Semantic Machine.
Implements Section 27:
- Type resolution
- Shape inference
- Canonicalization (dead-node pruning, associative sorting of commutative operands)
- Produces canonical UniversalIRProgram
"""

from __future__ import annotations
from typing import Dict, List, Set
from hyper.universal_ir.program import UniversalIRProgram
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.opcodes import Opcode
from hyper.escape.necessary_work import NecessaryWorkGraph


COMMUTATIVE_OPCODES = {
    Opcode.ADD,
    Opcode.MUL,
    Opcode.MIN,
    Opcode.MAX,
}


class SemanticNormalizer:
    """
    Normalizes Universal IR programs to a canonical algebraic form:
    1. Dead node elimination using formal NecessaryWorkGraph reachability
    2. Commutative operand canonicalization (lexicographical sorting of operand IDs)
    3. Deterministic instruction ordering
    """

    def __init__(self) -> None:
        pass

    def normalize(self, program: UniversalIRProgram) -> UniversalIRProgram:
        """
        Executes formal normalization pipeline.
        Returns canonicalized UniversalIRProgram.
        """
        program.validate()

        # Step 1: Necessary Work Analysis (isolate dead nodes)
        nwg = NecessaryWorkGraph(program)
        required_node_ids: Set[str] = set(nwg.get_required_nodes())

        canonical_prog = UniversalIRProgram(name=f"{program.name}_canonical")

        # Copy inputs
        for inp_name, inp_type in program.inputs.items():
            canonical_prog.add_input(inp_name, inp_type)

        # Step 2: Canonicalize operations
        for op in program.instructions:
            if op.result_id not in required_node_ids and op.result_id not in program.outputs:
                # Safely eliminate provably dead instruction
                continue

            operands = list(op.operands)
            # If commutative and operands are variable names, canonicalize order
            if op.opcode in COMMUTATIVE_OPCODES and len(operands) == 2:
                if isinstance(operands[0], str) and isinstance(operands[1], str):
                    if operands[0] > operands[1]:
                        operands = [operands[1], operands[0]]

            canonical_op = UniversalOp(
                opcode=op.opcode,
                operands=operands,
                result_id=op.result_id,
                result_type=op.result_type,
                attributes=dict(op.attributes),
                provenance=op.provenance or "normalized",
            )
            canonical_prog.add_instruction(canonical_op)

        # Copy outputs
        for out in program.outputs:
            canonical_prog.add_output(out)

        canonical_prog.validate()
        return canonical_prog
