"""
tests/test_frontends_and_expansions.py
======================================
Tests for Universal Frontends (CIR, TensorGraph, CUDA, OpenCL, SYCL),
Semantic Normalizer, Memory Aliasing, Control Flow, and Necessary Work.
Implements Sections 19, 20, 21, 23, 24, 25, 26, 27, 28.
"""

import pytest
import numpy as np

from hyper.frontends import (
    FrontendRegistry,
    CIRFrontend,
    TensorGraphFrontend,
    CUDALikeFrontend,
    OpenCLFrontend,
    SYCLFrontend,
    SemanticNormalizer,
    UnsupportedSemanticError,
)
from hyper.semantics.aliasing import MemoryAliasAnalyzer, MemoryRegion, AliasVerdict
from hyper.semantics.control_flow import StructuredLoop, StructuredBranch, LoopKind
from hyper.escape.necessary_work import NecessaryWorkGraph, NodeNecessity
from hyper.universal_ir.program import UniversalIRProgram
from hyper.universal_ir.instruction import UniversalOp
from hyper.universal_ir.opcodes import Opcode
from hyper.semantics.types import DataType, TensorType
from hyper.executor.reference_executor import UniversalReferenceExecutor
from hyper.executor.exact_executor import UniversalExactExecutor


def test_frontend_registry():
    frontends = FrontendRegistry.list_frontends()
    assert len(frontends) >= 5
    names = {f.name.lower() for f in frontends}
    assert "cir" in names
    assert "tensorgraph" in names
    assert "cuda_subset" in names
    assert "opencl_subset" in names
    assert "sycl_subset" in names


def test_cuda_frontend_valid_subset():
    frontend = CUDALikeFrontend()
    cuda_code = """
    __global__ void vectorAdd(const float* A, const float* B, float* C, int N) {
        int i = blockIdx.x * blockDim.x + threadIdx.x;
        __syncthreads();
        if (i < N) {
            C[i] = A[i] + B[i];
        }
    }
    """
    program = frontend.import_to_ir(cuda_code)
    assert program.name == "cuda_vectorAdd"
    assert "A" in program.inputs
    assert "B" in program.inputs
    assert "C" in program.outputs
    # Verify execution
    exec_engine = UniversalExactExecutor()
    inputs = {
        "A": np.full((64, 64), 2.0, dtype=np.float32),
        "B": np.full((64, 64), 3.0, dtype=np.float32),
    }
    res, backend, _ = exec_engine.execute_exact(program, inputs)
    assert np.allclose(res["C"], 5.0)


def test_cuda_frontend_unsupported_semantic_fail_closed():
    frontend = CUDALikeFrontend()
    cuda_code_unsupported = """
    __global__ void warpReduce(float* data) {
        float val = data[threadIdx.x];
        val += __shfl_down_sync(0xffffffff, val, 16);
    }
    """
    with pytest.raises(UnsupportedSemanticError) as exc_info:
        frontend.import_to_ir(cuda_code_unsupported)
    assert "UNSUPPORTED_CUDA_SEMANTIC" in str(exc_info.value)


def test_opencl_frontend_valid_and_unsupported():
    frontend = OpenCLFrontend()
    cl_code = """
    __kernel void add_arrays(__global float* A, __global float* B, __global float* C) {
        int id = get_global_id(0);
        barrier(CLK_LOCAL_MEM_FENCE);
        C[id] = A[id] + B[id];
    }
    """
    program = frontend.import_to_ir(cl_code)
    assert "C" in program.outputs

    # Unsupported extension
    cl_unsupported = """
    #pragma OPENCL EXTENSION cl_khr_subgroups : enable
    __kernel void subgroup_op() {}
    """
    with pytest.raises(UnsupportedSemanticError) as exc:
        frontend.import_to_ir(cl_unsupported)
    assert "UNSUPPORTED_OPENCL_SEMANTIC" in str(exc.value)


def test_sycl_frontend_valid_and_unsupported():
    frontend = SYCLFrontend()
    prog = frontend.import_to_ir("sycl::parallel_for")
    assert "out_c" in prog.outputs

    with pytest.raises(UnsupportedSemanticError) as exc:
        frontend.import_to_ir("sycl::ext::intel::esimd")
    assert "UNSUPPORTED_SYCL_SEMANTIC" in str(exc.value)


def test_tensor_graph_frontend():
    frontend = TensorGraphFrontend()
    spec = {
        "name": "simple_mlp",
        "inputs": [
            {"name": "X", "shape": [4, 8], "dtype": "FP32"},
            {"name": "W", "shape": [8, 4], "dtype": "FP32"},
        ],
        "nodes": [
            {"op_type": "MatMul", "inputs": ["X", "W"], "output": "h1", "output_shape": [4, 4]},
            {"op_type": "Relu", "inputs": ["h1"], "output": "out", "output_shape": [4, 4]},
        ],
        "outputs": ["out"],
    }
    program = frontend.import_to_ir(spec)
    assert "X" in program.inputs
    assert "out" in program.outputs
    inputs = {
        "X": np.ones((4, 8), dtype=np.float32),
        "W": np.full((8, 4), 0.5, dtype=np.float32),
    }
    exec_engine = UniversalExactExecutor()
    res, _, _ = exec_engine.execute_exact(program, inputs)
    assert np.allclose(res["out"], 4.0)


def test_memory_aliasing_analyzer():
    analyzer = MemoryAliasAnalyzer()
    analyzer.register_region(MemoryRegion(buffer_id="buf_A", base_offset=0, size_bytes=1024))
    analyzer.register_region(MemoryRegion(buffer_id="buf_B", base_offset=0, size_bytes=1024))

    # Distinct buffers
    assert analyzer.analyze_alias("buf_A", "buf_B") == AliasVerdict.NO_ALIAS
    assert analyzer.can_safely_reorder("buf_A", "buf_B") is True

    # Same buffer identical index
    assert analyzer.analyze_alias("buf_A", "buf_A", index_a=5, index_b=5) == AliasVerdict.MUST_ALIAS

    # Same buffer distinct scalar indices
    assert analyzer.analyze_alias("buf_A", "buf_A", index_a=3, index_b=7) == AliasVerdict.NO_ALIAS

    # Disjoint slices
    slc1 = (slice(0, 10),)
    slc2 = (slice(15, 25),)
    assert analyzer.analyze_alias("buf_A", "buf_A", index_a=slc1, index_b=slc2) == AliasVerdict.NO_ALIAS


def test_structured_control_flow():
    # Test Bounded Loop
    loop = StructuredLoop(
        loop_id="loop_test",
        kind=LoopKind.FOR_BOUNDED,
        max_iterations=10,
        induction_var="i",
        lower_bound=0,
        upper_bound=5,
        step=1,
        body_fn=lambda env, idx: {"acc": env["acc"] + 2.0},
    )
    env_out = loop.execute_bounded({"acc": 0.0})
    assert env_out["acc"] == 10.0

    # Test Branch with PHI
    branch = StructuredBranch(
        branch_id="br_test",
        condition_var="cond",
        then_vars=["v_then"],
        else_vars=["v_else"],
        merge_vars=["v_merged"],
        phi_mappings={"v_merged": ("v_then", "v_else")},
    )
    then_env = {"v_then": np.array([10.0, 20.0])}
    else_env = {"v_else": np.array([1.0, 2.0])}
    cond_true = np.array([True, False])
    merged = branch.evaluate_phi(cond_true, then_env, else_env)
    assert np.allclose(merged["v_merged"], [10.0, 2.0])


def test_necessary_work_and_semantic_normalizer():
    # Program with a dead instruction
    p = UniversalIRProgram(name="prog_with_dead_node")
    t_type = TensorType(shape=(4, 4), dtype=DataType.FP32)
    p.add_input("A", t_type)
    p.add_input("B", t_type)

    p.add_instruction(UniversalOp(opcode=Opcode.ADD, result_id="useful_add", result_type=t_type, operands=("A", "B")))
    p.add_instruction(UniversalOp(opcode=Opcode.MUL, result_id="dead_mul", result_type=t_type, operands=("A", "B")))
    p.add_output("useful_add")

    # Analyze necessity
    nwg = NecessaryWorkGraph(p)
    assert "dead_mul" in nwg.get_eliminable_nodes()
    assert "useful_add" in nwg.get_required_nodes()

    # Normalize program
    normalizer = SemanticNormalizer()
    p_norm = normalizer.normalize(p)
    assert len(p_norm.instructions) == 1
    assert p_norm.instructions[0].result_id == "useful_add"
