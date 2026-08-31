# 🏛️ HYPER-100: Workload IR & Graph Specification

## 1. Internal Representation (`WorkloadIR`)
Every computational task entering HYPER is normalized into a unified, machine-readable `WorkloadIR`:
- **Operations:** Type, input/output tensors, estimated baseline FLOPs, memory footprint.
- **Dependencies:** DAG topology, critical path identification, and dead calculation pruning.
- **Attributes:** Sparsity, spectral rank, condition norm, necessity classification, precision tier.

```python
from hyper.ir import WorkloadIR, IROperation

ir = WorkloadIR(workload_id="gemm_2048", workload_name="Dense GEMM", domain="AI")
ir.add_operation(IROperation(
    op_id="op_matmul",
    op_name="Dense FP32 GEMM",
    op_category="linear_algebra",
    input_shapes=[[2048, 2048], [2048, 2048]],
    output_shape=[2048, 2048],
    estimated_flops=2 * 2048 * 2048 * 2048,
    estimated_memory_bytes=3 * 2048 * 2048 * 4
))
```
