"""
hyper_v3/runtime/execution_graph.py
Executes topologically ordered ComputationGraphIR nodes across heterogeneous backends.
"""

from typing import Dict, Any, Tuple
import numpy as np
from hyper_v3.ir.graph import ComputationGraphIR
from hyper_v3.ir.operation import OpType
from hyper_v3.runtime.scheduler import HeterogeneousScheduler


class ExecutionGraphRuntime:
    """Executes a ComputationGraphIR instance."""

    def __init__(self):
        self.scheduler = HeterogeneousScheduler()

    def execute_graph(self, graph: ComputationGraphIR, inputs: Dict[str, np.ndarray]) -> Tuple[Dict[str, np.ndarray], float]:
        intermediates: Dict[str, np.ndarray] = dict(inputs)
        total_time_us = 0.0

        for node in graph.topological_sort():
            if node.annotations.is_dead:
                continue

            if node.op_type == OpType.MATMUL:
                a = intermediates[node.inputs[0].name]
                b = intermediates[node.inputs[1].name]
                out, t_us = self.scheduler.dispatch_matmul(a, b, node.target_device)
                intermediates[node.outputs[0].name] = out
                total_time_us += t_us
            elif node.op_type == OpType.FFT:
                sig = intermediates[node.inputs[0].name]
                out, t_us = self.scheduler.cpu.execute_fft(sig)
                intermediates[node.outputs[0].name] = out
                total_time_us += t_us
            elif node.op_type == OpType.REDUCTION:
                vec = intermediates[node.inputs[0].name]
                out, t_us = self.scheduler.cpu.execute_reduction(vec)
                intermediates[node.outputs[0].name] = np.array([out])
                total_time_us += t_us

        outputs = {name: intermediates[name] for name in graph.output_tensors if name in intermediates}
        return outputs, total_time_us
