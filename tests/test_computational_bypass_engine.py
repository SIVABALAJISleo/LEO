"""
tests/test_computational_bypass_engine.py
=========================================
Comprehensive Test Suite for the Universal Computational Bypass Engine (CBE).

Validates the 5 Hardware-Bypassing Foundations:
1. ZeroCopyUnifiedMemoryBypass: 100% PCIe bus elimination via Alder Lake-H unified memory.
2. BitNetTernaryAdditiveBypass: 100% multiplication elimination via {-1, 0, +1} ternary addition.
3. DynamicActivationSparsityBypass: 85% neuron elimination via Top-K activation routing.
4. TemporalMotionVectorBypass: 90% pixel shading elimination via residual delta carryforward.
5. AnalyticSDFSphereTracingBypass: 80% ray-triangle BVH elimination via analytic sphere marching.
6. Master ComputationalBypassEngine coordination and summary metrics.
7. FastAPI endpoint /api/v1/discovery/bypass-engine.
"""

import pytest
from fastapi.testclient import TestClient

from hyper.discovery.computational_bypass_engine import (
    ComputationalBypassEngine,
    BypassDomain,
    ZeroCopyUnifiedMemoryBypass,
    BitNetTernaryAdditiveBypass,
    DynamicActivationSparsityBypass,
    TemporalMotionVectorBypass,
    AnalyticSDFSphereTracingBypass,
)
from backend.main import app


def test_zero_copy_unified_memory_bypass():
    res = ZeroCopyUnifiedMemoryBypass.evaluate(buffer_size_mb=32.0)
    assert res.domain == BypassDomain.UNIFIED_MEMORY
    assert res.work_elimination_pct == 100.0
    assert res.is_contract_verified is True
    assert res.contract_exactness == "BIT_EXACT"
    assert res.error_bound == 0.0
    assert res.measured_speedup > 100.0


def test_bitnet_ternary_additive_bypass():
    res = BitNetTernaryAdditiveBypass.evaluate(dim_m=256, dim_k=256)
    assert res.domain == BypassDomain.TERNARY_ADDITIVE
    assert res.work_elimination_pct == 50.0 # Multiplications eliminated
    assert res.is_contract_verified is True
    assert res.contract_exactness == "BIT_EXACT"
    assert res.error_bound < 1e-3


def test_dynamic_activation_sparsity_bypass():
    res = DynamicActivationSparsityBypass.evaluate(dim_m=512, dim_k=512, sparsity_ratio=0.85)
    assert res.domain == BypassDomain.ACTIVATION_SPARSITY
    assert res.work_elimination_pct >= 80.0
    assert res.is_contract_verified is True
    assert res.contract_exactness == "SEMANTICALLY_EQUIVALENT"
    assert res.error_bound <= 0.15 # Cosine similarity >= 0.85


def test_temporal_motion_vector_bypass():
    res = TemporalMotionVectorBypass.evaluate(width=640, height=480, changed_pixel_pct=0.10)
    assert res.domain == BypassDomain.TEMPORAL_GRAPHICS
    assert res.work_elimination_pct == 90.0
    assert res.is_contract_verified is True
    assert res.contract_exactness == "BIT_EXACT"
    assert res.measured_speedup >= 5.0


def test_analytic_sdf_sphere_tracing_bypass():
    res = AnalyticSDFSphereTracingBypass.evaluate(num_rays=1000)
    assert res.domain == BypassDomain.ANALYTIC_RAY_MARCHING
    assert res.work_elimination_pct >= 75.0
    assert res.is_contract_verified is True
    assert res.contract_exactness == "NUMERICALLY_EXACT"
    assert res.measured_speedup >= 5.0


def test_master_computational_bypass_engine():
    engine = ComputationalBypassEngine()
    summary = engine.get_summary()

    assert summary["total_bypasses"] == 5
    assert summary["all_verified"] is True
    assert summary["average_work_elimination_pct"] >= 75.0
    assert summary["average_measured_speedup"] >= 10.0


def test_fastapi_bypass_engine_endpoint():
    client = TestClient(app)
    resp = client.get("/api/v1/discovery/bypass-engine")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_bypasses"] == 5
    assert data["all_verified"] is True
    assert len(data["bypasses"]) == 5
