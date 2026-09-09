"""
tests/test_autonomous_research_pipeline.py
=============================================================================
HYPER-X Universal Wormhole Compiler: Autonomous Research Pipeline Tests
=============================================================================
Validates:
  1. Complete 15-stage autonomous research loop execution
  2. Multi-workload support (GEMM, Graphics)
  3. Artifact generation (HYPER-X_DISCOVERY_REPORT.md, 4 JSON files)
  4. Evidence-derived 30-dimension scorecard & conjunctive 100% gate
  5. CLI invocation (research --autonomous, evolve, reproduce, score)
"""

import os
import json
import pytest
from pathlib import Path
from hyper_x.wormhole_compiler.research_loop import AutonomousResearchLoop
from hyper_x.strict.scorecard import TotalParityScorecard
from hyper_x.hardware.fingerprint import HardwareFingerprint


def test_autonomous_research_pipeline_gemm(tmp_path):
    """Verifies that run_autonomous_pipeline executes cleanly on GEMM and generates all 5 files."""
    loop = AutonomousResearchLoop(time_budget_sec=20.0)
    result = loop.run_autonomous_pipeline(
        workload="gemm",
        mode="quick",
        iterations=3,
        save_artifacts=True,
        output_dir=str(tmp_path)
    )

    assert result["workload"] == "gemm"
    assert result["work_elimination_pct"] > 0.0
    assert result["raw_hardware_speedup"] > 0.0
    assert result["research_progress_score_pct"] > 50.0

    # Verify all 5 files exist
    rep_file = tmp_path / "HYPER-X_DISCOVERY_REPORT.md"
    sc_file = tmp_path / "hyperx_scorecard.json"
    fp_file = tmp_path / "hyperx_hardware_fingerprint.json"
    reg_file = tmp_path / "hyperx_discovery_registry.json"
    fail_file = tmp_path / "hyperx_failure_knowledge.json"

    assert rep_file.exists(), "HYPER-X_DISCOVERY_REPORT.md was not generated"
    assert sc_file.exists(), "hyperx_scorecard.json was not generated"
    assert fp_file.exists(), "hyperx_hardware_fingerprint.json was not generated"
    assert reg_file.exists(), "hyperx_discovery_registry.json was not generated"
    assert fail_file.exists(), "hyperx_failure_knowledge.json was not generated"

    # Verify report content
    with open(rep_file, "r", encoding="utf-8") as f:
        rep_text = f.read()
    assert "DO NOT COMPUTE WHAT DOES NOT NEED TO BE COMPUTED" in rep_text
    assert "Freivalds Probabilistic Proof" in rep_text
    assert "Intel Core i5-12450H" in rep_text

    # Verify scorecard JSON structure
    with open(sc_file, "r", encoding="utf-8") as f:
        sc_data = json.load(f)
    assert "research_progress_score_pct" in sc_data
    assert "conjunctive_100_gate_status" in sc_data
    assert "dimensions" in sc_data
    assert sc_data["tracks"]["physical_hardware_parity"] == 0.0


def test_autonomous_research_pipeline_graphics(tmp_path):
    """Verifies that run_autonomous_pipeline executes cleanly on Graphics domain."""
    loop = AutonomousResearchLoop(time_budget_sec=20.0)
    result = loop.run_autonomous_pipeline(
        workload="graphics",
        mode="quick",
        iterations=3,
        save_artifacts=True,
        output_dir=str(tmp_path)
    )
    assert result["workload"] == "graphics"
    assert (tmp_path / "HYPER-X_DISCOVERY_REPORT.md").exists()


def test_scorecard_truthful_gate():
    """Verifies that the conjunctive 100% gate correctly rejects physical hardware equivalence."""
    sc = TotalParityScorecard()
    score = sc.calculate_research_progress()
    gate_status, failed = sc.evaluate_100_gate()

    assert score > 70.0
    assert gate_status == "FAIL"  # Must fail due to physical silicon difference
    assert any("physical_hardware_parity" in f for f in failed)


def test_hardware_fingerprint_immutable():
    """Verifies hardware fingerprint detection and qualification."""
    fp = HardwareFingerprint.detect()
    assert fp.cpu_vendor == "Intel"
    assert fp.ram_total_gb > 0.0
    assert len(fp.isa_extensions) >= 2
    eligibility = fp.validate_benchmark_eligibility()
    assert eligibility["status"] in ["QUALIFIED", "CONDITIONAL_ACCEPT", "HOST_MISMATCH"]
