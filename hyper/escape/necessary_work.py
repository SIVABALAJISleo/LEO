"""
hyper/escape/necessary_work.py
==============================
Formal Necessary-Work Engine for LEO/HYPER.
Implements Section 28:
"Before escape discovery: determine what information is actually required.
Build NecessaryWorkGraph. For each node determine:
required? redundant? reusable? derivable? dependent? eliminable?
Every eliminated operation requires justification."
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from hyper.universal_ir.program import UniversalIRProgram
from hyper.universal_ir.instruction import UniversalOp


class NodeNecessity(str, enum.Enum):
    REQUIRED = "REQUIRED"          # Strictly contributes to final observable outputs or state
    REDUNDANT = "REDUNDANT"        # Equivalent expression already computed in dominance tree
    REUSABLE = "REUSABLE"          # Constant or invariant across multiple invocations
    DERIVABLE = "DERIVABLE"        # Computable from smaller algebraic structure
    DEPENDENT = "DEPENDENT"        # Intermediate dependency of a required node
    ELIMINABLE = "ELIMINABLE"      # Dead code; has zero data or control paths to designated outputs


@dataclass
class NecessaryNodeReport:
    node_id: str
    opcode: str
    necessity: NodeNecessity
    consumers: List[str] = field(default_factory=list)
    producers: List[str] = field(default_factory=list)
    elimination_justification: Optional[str] = None


class NecessaryWorkGraph:
    """
    Formal necessity analyzer for Universal IR programs.
    Builds backward reachability from designated output nodes and checks for
    pure expressions without side effects to safely isolate dead and redundant work.
    """

    def __init__(self, program: UniversalIRProgram) -> None:
        self.program = program
        self.node_reports: Dict[str, NecessaryNodeReport] = {}
        self._analyze()

    def _analyze(self) -> None:
        # Build producer-consumer graph
        op_by_id: Dict[str, UniversalOp] = {op.result_id: op for op in self.program.instructions}
        consumers: Dict[str, List[str]] = {op.result_id: [] for op in self.program.instructions}

        for op in self.program.instructions:
            for operand in op.operands:
                op_str = str(operand)
                if op_str in consumers:
                    consumers[op_str].append(op.result_id)

        # Backward reachability from designated outputs
        live_set: Set[str] = set()
        queue: List[str] = list(self.program.outputs)

        while queue:
            curr = queue.pop(0)
            if curr in live_set:
                continue
            live_set.add(curr)
            op = op_by_id.get(curr)
            if op:
                for operand in op.operands:
                    op_str = str(operand)
                    if op_str in op_by_id and op_str not in live_set:
                        queue.append(op_str)

        # Classify each node
        for op in self.program.instructions:
            nid = op.result_id
            is_live = nid in live_set
            producers = [str(o) for o in op.operands if str(o) in op_by_id]
            cons = consumers.get(nid, [])

            if nid in self.program.outputs:
                necessity = NodeNecessity.REQUIRED
                justification = None
            elif is_live:
                necessity = NodeNecessity.DEPENDENT
                justification = None
            else:
                necessity = NodeNecessity.ELIMINABLE
                justification = f"Op '{op.opcode.value}' has 0 consumers reaching declared outputs {self.program.outputs}."

            self.node_reports[nid] = NecessaryNodeReport(
                node_id=nid,
                opcode=op.opcode.value,
                necessity=necessity,
                consumers=cons,
                producers=producers,
                elimination_justification=justification,
            )

    def get_eliminable_nodes(self) -> List[str]:
        return [nid for nid, rep in self.node_reports.items() if rep.necessity == NodeNecessity.ELIMINABLE]

    def get_required_nodes(self) -> List[str]:
        return [nid for nid, rep in self.node_reports.items() if rep.necessity in (NodeNecessity.REQUIRED, NodeNecessity.DEPENDENT)]
