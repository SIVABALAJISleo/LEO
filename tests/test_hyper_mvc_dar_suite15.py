"""
tests/test_hyper_mvc_dar_suite15.py
Tests the execution of all 15 canonical counterexample workloads through the HyperMVCDAREngine
under Track A (Exact) and Track B (Contract-Aware).
"""

import pytest
from hyper_mvc_dar import (
    HyperMVCDAREngine,
    ExecutionContract,
    ExecutionTrack,
    ContractClass,
)


@pytest.fixture
def engine():
    return HyperMVCDAREngine()


WORKLOAD_IDS = [
    "w01_dense_gemm",
    "w02_tensor_gemm",
    "w03_sparse_fft",
    "w04_vector_reductions",
    "w05_uncached_llm",
    "w06_batched_ai",
    "w07_rasterization",
    "w08_particles",
    "w09_bvh_construction",
    "w10_path_tracing",
    "w11_video_pipeline",
    "w12_n_body",
    "w13_option_pricing",
    "w14_blender_cycles",
    "w15_unreal_engine",
]


@pytest.mark.parametrize("workload_id", WORKLOAD_IDS)
def test_suite_15_track_b_contract_execution(engine, workload_id):
    contract = ExecutionContract(
        contract_class=ContractClass.NUMERICALLY_BOUNDED,
        track=ExecutionTrack.TRACK_B_CONTRACT,
        relative_error=0.01,
        verification_required=True
    )
    res = engine.execute_workload(workload_id, contract)

    assert res["contract_satisfied"] is True
    assert res["verification_status"] == "PASS"
    assert res["work_avoidance_ratio"] >= 0.0
    assert res["speedup_factor"] >= 1.0
    assert res["execution_time_ms"] > 0.0


@pytest.mark.parametrize("workload_id", ["w01_dense_gemm", "w02_tensor_gemm", "w03_sparse_fft"])
def test_suite_15_track_a_exact_execution(engine, workload_id):
    contract = ExecutionContract(
        contract_class=ContractClass.EXACT,
        track=ExecutionTrack.TRACK_A_EXACT,
        verification_required=True
    )
    res = engine.execute_workload(workload_id, contract)

    assert res["contract_satisfied"] is True
    assert res["verification_status"] == "PASS"
    assert res["track"] == "TRACK_A_EXACT"
    # Track A does not avoid work
    assert res["work_avoidance_ratio"] == 0.0
