"""
Search Space Compiler: Compiles workload, contract, constraints, and hardware
into a 9-dimensional typed search space.
"""
from typing import Any, Dict, Optional
from hyper_universal.contract_ir import ContractIR, ContractType
from hyper_universal.workload import UniversalWorkload
from hyper_omega.search_space_compiler.types import (
    CompiledSearchSpace,
    MathematicalOption,
    AlgorithmOption,
    RepresentationOption,
    ProgramOption,
    CompilerOption,
    ScheduleOption,
    MemoryLayoutOption,
    PrecisionOption,
    ExecutionOption,
)


class SearchSpaceCompiler:
    """
    Input: workload, contract, constraints, hardware
    Output: search space spanning 9 dimensions.
    """

    def compile(
        self,
        workload: UniversalWorkload,
        contract: ContractIR,
        constraints: Optional[Dict[str, Any]] = None,
        hardware: Optional[Dict[str, Any]] = None,
    ) -> CompiledSearchSpace:
        constraints = constraints or {}
        hardware = hardware or {}
        w_id = workload.workload_id

        # 1. Mathematical Space
        math_space = [
            MathematicalOption("standard_expansion", "f(x) = sum_i(a_i * x^i)", "always", "O(N^2)"),
            MathematicalOption("horner_rule", "f(x) = (...((a_n*x + a_{n-1})*x + ...))", "polynomials", "O(N)"),
            MathematicalOption("karatsuba_mult", "xy = z_2 B^2 + z_1 B + z_0", "bilinear_mult", "O(N^1.585)"),
            MathematicalOption("strassen_bilinear", "M = 7 multiplications for 2x2", "matrix_mult", "O(N^2.807)"),
        ]

        # 2. Algorithm Space
        algo_space = [
            AlgorithmOption("direct_iterative", "iterative", "O(N^2)", "exact"),
            AlgorithmOption("divide_and_conquer", "recursive_bisection", "O(N log N)", "exact"),
            AlgorithmOption("dynamic_programming_memoized", "memoized_dag", "O(N)", "exact"),
            AlgorithmOption("branch_and_bound", "pruning_search", "O(K)", "exact_under_bounds"),
        ]

        # 3. Representation Space
        rep_space = [
            RepresentationOption("dense_contiguous", "dense_array", "N * sizeof(T)", "O(1)"),
            RepresentationOption("sparse_csr", "csr_matrix", "2*nnz + N", "O(nnz)"),
            RepresentationOption("blocked_hierarchical", "hierarchical_tiles", "N * sizeof(T)", "O(N)"),
            RepresentationOption("frequency_domain", "fft_coefficients", "N * sizeof(complex)", "O(N log N)"),
        ]

        # 4. Program Space
        prog_space = [
            ProgramOption("baseline_loops", "naive_nested_for", vectorization=False),
            ProgramOption("unrolled_vectorized_avx2", "unroll_4x_avx2", vectorization=True),
            ProgramOption("fused_kernel", "loop_fusion_no_intermediates", vectorization=True),
            ProgramOption("branchless_conditional", "select_masking", vectorization=True),
        ]

        # 5. Compiler Space
        comp_space = [
            CompilerOption("default_o2", ["-O2"], "heuristic"),
            CompilerOption("aggressive_o3_fastmath", ["-O3", "-ffast-math"], "aggressive_inline"),
            CompilerOption("native_avx2_tuned", ["-O3", "-march=native", "-mavx2"], "always_inline_critical"),
        ]

        # 6. Schedule Space
        sched_space = [
            ScheduleOption(tile_size_l1=32, tile_size_l2=128, thread_count=4, pipeline_depth=2),
            ScheduleOption(tile_size_l1=64, tile_size_l2=256, thread_count=8, pipeline_depth=4),
            ScheduleOption(tile_size_l1=16, tile_size_l2=64, thread_count=1, pipeline_depth=1),
        ]

        # 7. Memory Layout Space
        mem_space = [
            MemoryLayoutOption("row_major_c", alignment_bytes=32),
            MemoryLayoutOption("col_major_fortran", alignment_bytes=32),
            MemoryLayoutOption("tiled_morton_z_curve", alignment_bytes=64),
        ]

        # 8. Precision Space
        prec_space = [
            PrecisionOption("FP32", None),
        ]
        # Only allow reduced precision if contract allows numerical tolerance
        if contract.contract_type in [ContractType.NUMERICAL, ContractType.NUMERICAL_TOLERANCE, ContractType.TOLERANCE, ContractType.PERCEPTUAL]:
            prec_space.extend([

                PrecisionOption("FP16", "ieee754_half"),
                PrecisionOption("BF16", "bfloat16"),
                PrecisionOption("INT8", "symmetric_per_tensor"),
                PrecisionOption("TERNARY_1_58", "bitnet_b1_58"),
            ])

        # 9. Execution Space
        exec_space = [
            ExecutionOption("CPU", offload_threshold_ops=1000),
            ExecutionOption("IGPU", offload_threshold_ops=50000),
            ExecutionOption("HYBRID_ASYNC", offload_threshold_ops=20000),
        ]

        return CompiledSearchSpace(
            workload_id=w_id,
            mathematical_space=math_space,
            algorithm_space=algo_space,
            representation_space=rep_space,
            program_space=prog_space,
            compiler_space=comp_space,
            schedule_space=sched_space,
            memory_layout_space=mem_space,
            precision_space=prec_space,
            execution_space=exec_space,
        )
