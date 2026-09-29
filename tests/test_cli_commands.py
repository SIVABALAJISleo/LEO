"""
tests/test_cli_commands.py
===========================
End-to-End Unit & Integration Tests for the 12 Mandated CLI Subcommands (Section 35).
"""

import argparse
import io
import json
import sys
import pytest

from hyper.research_engine import cli_commands


def test_cli_audit(capsys):
    args = argparse.Namespace(full=False, json=True)
    cli_commands.cmd_audit(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["status"] == "PASS"
    assert "Intel Core i5-12450H" in data["target_hardware"]["cpu"]
    assert data["target_hardware"]["external_gpu"] == "NONE (STRICT_LOCAL_ENFORCED)"
    assert data["claim_status"]["hardware_parity"] == "NOT CLAIMED (PHYSICALLY_DISJOINT)"


def test_cli_discover(capsys):
    args = argparse.Namespace(workload="GEMM_STANDARD", budget="fast", json=True)
    cli_commands.cmd_discover(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["workload_id"] == "GEMM_STANDARD"
    assert "discovery_id" in data
    assert "discovered_algorithm" in data
    assert "complexity_estimate_discovered" in data


def test_cli_search(capsys):
    args = argparse.Namespace(workload="GEMM_STANDARD", budget="fast", strategy="beam", json=True)
    cli_commands.cmd_search(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["workload_id"] == "GEMM_STANDARD"
    assert data["budget_level"] == "LEVEL_1_FAST"
    assert data["total_nodes_in_graph"] >= 1
    assert "pathway_graph.json" in data["graph_saved"]


def test_cli_verify(capsys):
    args = argparse.Namespace(workload="GEMM_STANDARD", candidate=None, json=True)
    cli_commands.cmd_verify(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["workload_id"] == "GEMM_STANDARD"
    assert data["is_verified"] is True
    assert data["adversarial_tests_evaluated"] >= 8
    assert data["counterexamples_found"] == 0


def test_cli_benchmark(capsys):
    args = argparse.Namespace(workload="GEMM_STANDARD", runs=2, amortized=100, json=True)
    cli_commands.cmd_benchmark(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "components_ms" in data
    assert "one_shot_total_cost_ms" in data
    assert "amortized_cost_ms_over_100_runs" in data
    assert data["telemetry"]["cpu_utilization_pct"] >= 0.0


def test_cli_blind(capsys):
    args = argparse.Namespace(rounds=2, domain="all", json=True)
    cli_commands.cmd_blind(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_blind_rounds"] == 2
    assert data["verified_pass_count"] >= 1
    assert data["generalization_score"] > 0.0


def test_cli_challenge(capsys):
    args = argparse.Namespace(rounds=2, categories="all", json=True)
    cli_commands.cmd_challenge(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_unseen_workloads"] == 2
    assert data["exact_workload_coverage"] > 0.0
    assert data["hardware_parity"] == "NOT CLAIMED (PHYSICALLY_DISJOINT)"


def test_cli_pathway(capsys):
    args = argparse.Namespace(workload="GEMM_STANDARD", export=None, json=True)
    cli_commands.cmd_pathway(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["total_nodes"] >= 1
    assert "edges" in data


def test_cli_replay(capsys):
    args = argparse.Namespace(proof_file=None, experiment_id=None, candidate=None, json=True)
    cli_commands.cmd_replay(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["replay_status"] == "REPRODUCIBLE_AND_VERIFIED"
    assert len(data["deterministic_seeds_evaluated"]) == 3


def test_cli_proof(capsys):
    args = argparse.Namespace(workload="GEMM_STANDARD", out_dir="proofs", json=True)
    cli_commands.cmd_proof(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["proof_version"] == "2.0-ULTRA-SONIC"
    assert data["contract"]["workload_id"] == "GEMM_STANDARD"
    assert data["verification"]["is_verified"] is True


def test_cli_report(capsys):
    args = argparse.Namespace(final=False, file=None, json=True)
    cli_commands.cmd_report(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "report_path" in data
    assert data["size_bytes"] > 0
