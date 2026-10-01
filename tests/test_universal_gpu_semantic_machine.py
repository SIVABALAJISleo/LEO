"""
tests/test_universal_gpu_semantic_machine.py
============================================
Comprehensive Master Test Suite for LEO/HYPER Universal GPU Semantic Machine.
Fulfills Sections 5, 7, 8, 9, 10, 27, 28, 29, 30, 36, 37, 53, 54, 58 of Master Specification.
"""

import numpy as np
import pytest

from hyper.universal_ir.opcodes import UniversalOpcode
from hyper.universal_ir.program import UniversalIRProgram, UniversalOp, UniversalType
from hyper.executor.reference_executor import ReferenceExecutor
from hyper.semantics.types import DataType, TensorType
from hyper.semantics.gpu_isa import (
    AddressSpace,
    GPUGridConfig,
    GPUInstruction,
    GPUOpcode,
    MemoryOrdering,
)
from hyper.executor.gpu_simt_executor import GPUSIMTExecutor
from hyper.frontends.ptx_frontend import PTXFrontend
from hyper.escape.egraph import (
    EGraph,
    ENode,
    RuleSafety,
    default_cost_function,
    make_default_rules,
)
from hyper.escape.vsa_engine import VSAContract, VSAContractType, VSAEngine
from hyper.coverage.compatibility_matrix import (
    ExecutionBackend,
    NVIDIACompatibilityMatrix,
    PerformanceStatus,
    SemanticSupport,
)
from hyper.workloads.cuda_test_corpus import CUDATestCorpus
from hyper.scheduler.heterogeneous_scheduler import (
    ExecutionResource,
    HeterogeneousScheduler,
)


class TestGPUSIMTExecution:
    """Test GPU ISA and SIMT Executor execution semantics."""

    def test_warp_shuffle_butterfly(self):
        """Test cross-lane warp shuffle broadcast across 32 lanes."""
        executor = GPUSIMTExecutor()
        instructions = [
            GPUInstruction(
                opcode=GPUOpcode.GPU_LOAD,
                result_id="val",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("in_buf", "%threadIdx.x"),
            ),
            GPUInstruction(
                opcode=GPUOpcode.GPU_SHUFFLE,
                result_id="shfl_val",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("val", 0),  # Broadcast lane 0 value
            ),
            GPUInstruction(
                opcode=GPUOpcode.GPU_STORE,
                result_id="store_op",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("out_buf", "%threadIdx.x", "shfl_val"),
            ),
        ]
        in_arr = np.arange(32, dtype=np.float32) + 10.0
        out_arr = np.zeros(32, dtype=np.float32)
        res_mem = executor.execute_kernel(
            instructions,
            global_memory={"in_buf": in_arr, "out_buf": out_arr},
            config=GPUGridConfig(grid_dim=(1, 1, 1), block_dim=(32, 1, 1)),
        )
        # All 32 threads received value 10.0 from lane 0
        assert np.all(res_mem["out_buf"] == 10.0)

    def test_shared_memory_barrier_sync(self):
        """Test shared memory staging and barrier synchronization (__syncthreads)."""
        executor = GPUSIMTExecutor()
        instructions = [
            GPUInstruction(
                opcode=GPUOpcode.GPU_LOAD,
                result_id="val",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("in_buf", "%threadIdx.x"),
            ),
            GPUInstruction(
                opcode=GPUOpcode.GPU_STORE,
                result_id="st_smem",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("smem", "%threadIdx.x", "val"),
                address_space=AddressSpace.SHARED,
            ),
            GPUInstruction(
                opcode=GPUOpcode.GPU_BARRIER,
                result_id="bar",
                result_type=TensorType(shape=(1,), dtype=DataType.VOID),
                operands=(),
            ),
            GPUInstruction(
                opcode=GPUOpcode.GPU_LOAD,
                result_id="loaded_val",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("smem", "%threadIdx.x"),
                address_space=AddressSpace.SHARED,
            ),
            GPUInstruction(
                opcode=GPUOpcode.GPU_STORE,
                result_id="st_out",
                result_type=TensorType(shape=(1,), dtype=DataType.FP32),
                operands=("out_buf", "%threadIdx.x", "loaded_val"),
            ),
        ]
        in_arr = np.arange(32, dtype=np.float32) * 2.0
        out_arr = np.zeros(32, dtype=np.float32)
        res_mem = executor.execute_kernel(
            instructions,
            global_memory={"in_buf": in_arr, "out_buf": out_arr},
            config=GPUGridConfig(grid_dim=(1, 1, 1), block_dim=(32, 1, 1)),
        )
        assert np.array_equal(res_mem["out_buf"], in_arr)


class TestPTXFrontend:
    """Test PTX parsing, lowering, and staged coverage."""

    def test_parse_ptx_vector_add(self):
        ptx_source = """
        .version 7.0
        .target sm_70
        .address_size 64

        .visible .entry vecAdd(
            .param .u64 a_ptr,
            .param .u64 b_ptr,
            .param .u64 c_ptr,
            .param .u32 n
        )
        {
            .reg .f32 %f<4>;
            ld.global.f32 %f1, [%rd1];
            ld.global.f32 %f2, [%rd2];
            add.f32 %f3, %f1, %f2;
            st.global.f32 [%rd3], %f3;
            ret;
        }
        """
        frontend = PTXFrontend()
        kernel = frontend.parse_ptx(ptx_source)
        assert kernel.name == "vecAdd"
        assert len(kernel.instructions) == 4
        assert kernel.instructions[2].opcode == GPUOpcode.GPU_ADD

        prog = frontend.lower_to_universal_ir(kernel)
        assert prog.name == "vecAdd"
        assert len(prog.instructions) >= 1

    def test_ptx_staged_coverage(self):
        frontend = PTXFrontend()
        metrics = frontend.compute_coverage_metrics()
        assert metrics["CUDA_LANGUAGE_COVERAGE"] > 0.0
        assert metrics["CUDA_RUNTIME_COVERAGE"] > 0.0
        assert metrics["CUDA_LIBRARY_COVERAGE"] > 0.0
        assert metrics["PTX_COVERAGE"] > 0.0
        assert metrics["INSTRUCTION_SEMANTIC_COVERAGE"] > 0.0


class TestEGraphEqualitySaturation:
    """Test E-Graph rewriting and exact rule gating."""

    def test_exact_algebraic_reduction(self):
        """Verify that x + 0 and y * 1 collapse exactly to x and y."""
        eg = EGraph()
        c0 = eg.add(ENode(op="CONST_0"))
        x = eg.add(ENode(op="VAR", metadata=(("name", "x"),)))
        # Expr: x + 0
        expr_add = eg.add(ENode(op="ADD", children=(x, c0)))

        rules = make_default_rules()
        allowed = {RuleSafety.EXACT}
        matches = eg.apply_rules(rules, allowed_safeties=allowed)
        assert matches > 0

        # Verify x + 0 is equivalent to x
        assert eg.find(expr_add) == eg.find(x)

        best_node, cost = eg.extract_cheapest(expr_add, default_cost_function)
        assert best_node.op == "VAR"
        assert cost == 0.0

    def test_approximate_rule_gating_under_exact_contract(self):
        """Verify that LOW_RANK_APPROXIMATION is FORBIDDEN under exact contracts."""
        eg = EGraph()
        a = eg.add(ENode(op="VAR", metadata=(("name", "A"),)))
        b = eg.add(ENode(op="VAR", metadata=(("name", "B"),)))
        gemm = eg.add(ENode(op="MATMUL", children=(a, b)))

        rules = make_default_rules()
        # Strictly EXACT contract: do NOT allow APPROXIMATE rules
        allowed_exact = {RuleSafety.EXACT}
        matches = eg.apply_rules(rules, allowed_safeties=allowed_exact)
        assert matches == 0  # No rule applied

        best_node, cost = eg.extract_cheapest(gemm, default_cost_function)
        assert best_node.op == "MATMUL"

        # Now test with APPROXIMATE allowed
        allowed_approx = {RuleSafety.EXACT, RuleSafety.APPROXIMATE}
        matches_approx = eg.apply_rules(rules, allowed_safeties=allowed_approx)
        assert matches_approx > 0

        best_node_approx, cost_approx = eg.extract_cheapest(gemm, default_cost_function)
        assert best_node_approx.op == "LOW_RANK_APPROX_MATMUL"
        assert cost_approx < cost


class TestVSAEngineGating:
    """Test Vector Symbolic Architecture engine and contract gating."""

    def test_vsa_gating_exact_contract(self):
        vsa = VSAEngine(dimension_bits=1024)
        contract = VSAContract(contract_type=VSAContractType.EXACT_FP32)
        allowed, reason, meta = vsa.evaluate_vsa_applicability(contract)
        assert not allowed
        assert meta["status"] == "REJECTED_BY_TRUTH_GATE"

    def test_vsa_gating_symbolic_contract(self):
        vsa = VSAEngine(dimension_bits=1024)
        contract = VSAContract(contract_type=VSAContractType.VSA_SYMBOLIC_ASSOCIATIVE)
        allowed, reason, meta = vsa.evaluate_vsa_applicability(contract)
        assert allowed
        assert meta["status"] == "PROVEN_ESCAPE"

    def test_vsa_properties(self):
        vsa = VSAEngine(dimension_bits=1024)
        v1 = vsa.create_random_hypervector(seed=1)
        v2 = vsa.create_random_hypervector(seed=2)

        # Invertibility: (A ^ B) ^ A == B
        bound = vsa.bind(v1, v2)
        unbound = vsa.unbind(bound, v1)
        assert np.array_equal(unbound, v2)

        # Quasi-orthogonality of random hypervectors
        sim = vsa.cosine_similarity(v1, v2)
        assert abs(sim) < 0.2  # Should be close to 0


class TestNVIDIACompatibilityMatrix:
    """Test NVIDIA GPU Compatibility Matrix completeness and honesty."""

    def test_matrix_honesty(self):
        matrix = NVIDIACompatibilityMatrix()
        summary = matrix.get_summary()

        assert summary["total_features_cataloged"] >= 10
        assert summary["supported_features"] >= 7
        assert summary["unsupported_features"] >= 1
        assert summary["physical_nvidia_performance_parity"].startswith("NOT_CLAIMED")
        assert summary["external_gpu_measurements"] == "NOT_CLAIMED"

        # Check Blackwell is marked UNSUPPORTED and UNAVAILABLE_ON_TARGET
        blackwell = [e for e in matrix.entries if e.architecture == "Blackwell"][0]
        assert blackwell.semantic_support == SemanticSupport.UNSUPPORTED
        assert blackwell.execution_backend == ExecutionBackend.UNAVAILABLE_ON_TARGET
        assert blackwell.performance_status == PerformanceStatus.NOT_CLAIMED


class TestProgressiveCUDACorpus:
    """Test execution of all 19 progressive CUDA workloads through Universal IR and Reference Executor."""

    @pytest.mark.parametrize("workload_id", list(range(1, 20)))
    def test_cuda_workload_exactness(self, workload_id: int):
        corpus = CUDATestCorpus()
        wl = [w for w in corpus.get_all_workloads() if w.id == workload_id][0]

        inputs = wl.input_generator()
        expected = wl.reference_fn(inputs)
        prog = wl.ir_builder()

        executor = ReferenceExecutor()
        outputs = executor.execute(prog, inputs)
        assert isinstance(outputs, dict) and len(outputs) > 0, f"Workload {wl.name} produced empty outputs"

        actual = outputs["out"] if "out" in outputs else (
            outputs["C"] if "C" in outputs else outputs["dist"]
        )

        actual_arr = np.asarray(actual)
        expected_arr = np.asarray(expected)

        if wl.contract in ("BITWISE_EXACT", "INTEGER_EXACT"):
            if actual_arr.dtype in (np.int32, np.int64):
                assert np.array_equal(actual_arr.ravel(), expected_arr.ravel()), f"Workload {wl.name} integer mismatch"
            else:
                assert np.allclose(actual_arr, expected_arr, atol=1e-7, rtol=1e-7), f"Workload {wl.name} mismatch"
        else:
            assert np.allclose(actual_arr, expected_arr, atol=1e-4, rtol=1e-4), f"Workload {wl.name} numerical mismatch"


class TestHeterogeneousSchedulerZeroCopy:
    """Test Heterogeneous Scheduler zero-copy modeling and P-core/E-core/iGPU scheduling."""

    def test_zero_copy_memory_profile(self):
        sched = HeterogeneousScheduler()
        profile = sched.memory_profile
        assert profile.copy_required is False
        assert profile.zero_copy_possible is True
        assert profile.shared_memory_mb == 16384.0

    def test_scheduling_decision(self):
        sched = HeterogeneousScheduler()
        A = np.random.randn(32, 32).astype(np.float32)
        B = np.random.randn(32, 32).astype(np.float32)
        decision = sched.schedule(A, B)
        assert decision.chosen_resource in (
            ExecutionResource.CPU_P_CORES,
            ExecutionResource.CPU_E_CORES,
            ExecutionResource.INTEL_UHD_IGPU,
            ExecutionResource.CPU_IGPU_HYBRID,
        )
        assert len(decision.decision_reason) > 10
