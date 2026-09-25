import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from hyper.discovery.cir import CIRGraph, CIRTensorMeta, DataType, OpType
from hyper.discovery.contract import VerificationMode, WorkloadContract

client = TestClient(app)


def test_api_parity_report():
    response = client.get("/api/v1/parity/report")
    assert response.status_code == 200
    data = response.json()
    assert data["hardware_parity"] == "NO_HARDWARE_PARITY"
    assert "BIT_EXACT" in data["supported_verification_modes"]


def test_api_dashboard_endpoint():
    response = client.get("/api/v1/pathway/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "HYPER" in response.text
    assert "Performance parity does not imply hardware parity" in response.text


def test_api_analyze_and_execute():
    g = CIRGraph(name="api_test_gemm")
    in_a = g.add_input("A", shape=(4, 4), dtype=DataType.FP32)
    in_b = g.add_input("B", shape=(4, 4), dtype=DataType.FP32)
    op_mm = g.add_op(OpType.MATMUL, [in_a, in_b], name="result", output_meta=CIRTensorMeta(shape=(4, 4), dtype=DataType.FP32))
    g.mark_output(op_mm)

    req_payload = {
        "workload_name": "api_test_gemm",
        "graph": g.to_dict(),
        "inputs": {
            "A": np.eye(4, dtype=np.float32).tolist(),
            "B": np.eye(4, dtype=np.float32).tolist(),
        },
        "strategy": "A_STAR",
        "benchmark_repetitions": 3,
    }

    # 1. Analyze
    resp_analyze = client.post("/api/v1/pathway/analyze", json=req_payload)
    assert resp_analyze.status_code == 200
    analyze_data = resp_analyze.json()
    assert "predicted_cost" in analyze_data
    assert "scheduling_decision" in analyze_data

    # 2. Execute & Discover
    resp_exec = client.post("/api/v1/pathway/execute", json=req_payload)
    assert resp_exec.status_code == 200
    exec_data = resp_exec.json()
    assert "pathway_id" in exec_data
    assert "proof_record" in exec_data
    assert "reproducibility_manifest" in exec_data
    assert exec_data["proof_record"]["verification"] == "PASSED"

    pw_id = exec_data["pathway_id"]

    # 3. Retrieve Proof & Trace
    resp_proof = client.get(f"/api/v1/pathway/{pw_id}/proof")
    assert resp_proof.status_code == 200
    assert "explanation" in resp_proof.json()

    resp_trace = client.get(f"/api/v1/pathway/{pw_id}/trace")
    assert resp_trace.status_code == 200
    assert "pathway_ascii_diff" in resp_trace.json()


def test_api_adversarial_challenge():
    payload = {
        "category": "BLIND_HOLDOUT_SET",
        "adversarial_type": "PRIME_DIMENSIONS",
    }
    resp = client.post("/api/v1/pathway/adversarial", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "adversarial_workload" in data
    assert "execution_report" in data
    assert data["adversarial_workload"]["category"] == "BLIND_HOLDOUT_SET"
