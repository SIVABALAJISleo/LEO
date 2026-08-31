"""
hyper/ir/workload_ir.py
=======================
Universal Workload Intermediate Representation (Section 7):
Provides WorkloadIR, DependencyGraph, DataFlowGraph, ControlFlowGraph,
MemoryGraph, ExecutionGraph, and ContractGraph models.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Set, Optional


@dataclass
class IROperation:
    op_id: str
    op_name: str
    op_category: str  # "linear_algebra", "fft", "attention", "reduction", "render", "stencil"
    input_shapes: List[List[int]] = field(default_factory=list)
    output_shape: List[int] = field(default_factory=list)
    dtype: str = "float32"
    estimated_flops: int = 0
    estimated_memory_bytes: int = 0
    is_parallel: bool = True
    dependencies: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkloadIR:
    """
    Unified Intermediate Representation across all computational domains.
    """
    workload_id: str
    workload_name: str
    domain: str  # "AI", "Graphics", "Simulation", "Numerical", "Media"
    operations: Dict[str, IROperation] = field(default_factory=dict)
    total_baseline_flops: int = 0
    total_baseline_memory_bytes: int = 0
    contract_id: Optional[str] = None

    def add_operation(self, op: IROperation) -> None:
        self.operations[op.op_id] = op
        self.total_baseline_flops += op.estimated_flops
        self.total_baseline_memory_bytes += op.estimated_memory_bytes

    def get_critical_path(self) -> List[str]:
        """Returns topological ordering of critical operations."""
        visited: Set[str] = set()
        order: List[str] = []

        def dfs(op_id: str):
            visited.add(op_id)
            if op_id in self.operations:
                for dep in self.operations[op_id].dependencies:
                    if dep not in visited:
                        dfs(dep)
            order.append(op_id)

        for op_id in self.operations:
            if op_id not in visited:
                dfs(op_id)
        return order
