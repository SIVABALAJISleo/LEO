"""
tests/test_silicon_virtualizer_and_hardware_bridge.py
=====================================================
Unit & Integration tests for:
- DormantSiliconHarvester
- MicroHardwareCatalog
- SoftwareDefinedVirtualSilicon
- FastAPI omega hardware bridge endpoints
"""

import pytest
from fastapi.testclient import TestClient

from hyper_omega.hardware_bridge import (
    DormantSiliconHarvester,
    MicroHardwareCatalog,
    SoftwareDefinedVirtualSilicon,
    HardwareIrrelevanceReport,
)
from backend.main import app


def test_dormant_silicon_harvester():
    harvester = DormantSiliconHarvester()
    summary = harvester.get_summary()
    assert summary["total_unlocked_on_die_tops"] > 0.0
    assert "Intel Deep Learning Boost (VNNI)" in summary["active_engines"]
    assert "Intel Xe-LP DP4A Matrix Accelerator" in summary["active_engines"]
    assert summary["pcie_transfer_latency_ms"] == 0.001


def test_micro_hardware_catalog():
    options = MicroHardwareCatalog.get_options()
    assert len(options) >= 4
    # Hailo-8 delivers 26 TOPS for ~$28
    hailo = next(opt for opt in options if "Hailo" in opt.name)
    assert hailo.int8_tops == 26.0
    assert hailo.cost_usd < 35.0
    assert hailo.power_watts <= 2.5

    rtx_comp = MicroHardwareCatalog.get_rtx_5090_comparison()
    assert rtx_comp["power_watts"] == 600.0
    assert rtx_comp["cost_usd"] > 1500.0


def test_software_defined_virtual_silicon_complexity_collapse():
    sdvs = SoftwareDefinedVirtualSilicon()
    report = sdvs.evaluate_complexity_collapse(problem_size=4096, rank_k=64)

    assert isinstance(report, HardwareIrrelevanceReport)
    # Scientific truth preservation: Never claim physical hardware fabrication
    assert report.physical_hardware_claimed is False
    assert report.physical_hardware_status == "NOT CLAIMED (PHYSICALLY_DISJOINT)"

    # Work elimination: O(N^2) vs O(N)
    assert report.work_elimination_factor > 10.0
    assert report.unlocked_on_die_tops > 0.0
    assert report.application_contract_parity_pct == 100.0
    assert report.hardware_disadvantage_irrelevance_pct == 100.0
    assert "irrelevant" in report.conclusion.lower()


def test_fastapi_omega_hardware_endpoints():
    client = TestClient(app)

    # 1. Test dormant silicon endpoint
    r1 = client.get("/api/v1/omega/dormant_silicon")
    assert r1.status_code == 200
    d1 = r1.json()
    assert "summary" in d1
    assert d1["summary"]["total_unlocked_on_die_tops"] > 0

    # 2. Test micro hardware endpoint
    r2 = client.get("/api/v1/omega/micro_hardware")
    assert r2.status_code == 200
    d2 = r2.json()
    assert "rtx_5090_reference" in d2
    assert len(d2["micro_hardware_options"]) >= 4

    # 3. Test complexity collapse endpoint
    r3 = client.post("/api/v1/omega/complexity_collapse", json={"problem_size": 2048, "rank_k": 32})
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["physical_hardware_claimed"] is False
    assert d3["work_elimination_factor"] > 1.0
    assert d3["hardware_disadvantage_irrelevance_pct"] == 100.0
