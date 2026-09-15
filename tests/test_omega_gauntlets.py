"""
tests/test_omega_gauntlets.py
=============================
Tests for Omega Research Mode:
- Necessary-Work Compiler (Part 8)
- Exact Compute Gauntlet (Part 36)
- Escape Gauntlet (Part 37)
- Anti-Structure Falsification Gauntlet (Part 32)
- Four Core Leaderboards (Part 54)
- Impossibility Engine (Part 57)
- RTX 5090 Gap Engine (Part 43)
"""

import pytest
from hyper_x.necessary_work import UniversalNecessaryWorkCompiler, OperationClass
from hyper_x.gauntlets import HyperExactGauntlet, HyperEscapeGauntlet, AntiStructureGauntlet
from hyper_x.leaderboards import FourCoreLeaderboards, LeaderboardEntry, LeaderboardCategory
from hyper_x.impossibility import ImpossibilityEngine, ImpossibilityClass
from hyper_x.gpu_ecosystem.gap_engine import RTX5090GapEngine


def test_necessary_work_compiler_gemm():
    compiler = UniversalNecessaryWorkCompiler()
    rep = compiler.analyze_gemm(512, 512, 512, effective_rank=32)
    assert rep.classification == OperationClass.LOW_RANK
    assert rep.necessary_work < rep.original_work
    assert rep.work_elimination_pct > 80.0
    assert rep.ccr > 1.0


def test_hyper_exact_gauntlet():
    gauntlet = HyperExactGauntlet()
    res = gauntlet.run_dense_gemm(N=128)
    assert res.passed_exact_parity is True
    assert len(res.exact_output_hash) == 64
    assert res.operations_count == 2 * 128 * 128 * 128


def test_hyper_escape_gauntlet():
    gauntlet = HyperEscapeGauntlet()
    res = gauntlet.run_low_rank_gemm(N=256, rank=16)
    assert res.contract_satisfied is True
    assert res.independent_verification_passed is True
    assert res.eliminated_work_pct > 50.0


def test_anti_structure_attacks():
    gauntlet = AntiStructureGauntlet()
    results = gauntlet.run_all()
    assert len(results) == 3
    for r in results:
        assert r["passed_falsification"] is True
        assert r["correctness_preserved"] is True


def test_four_core_leaderboards():
    boards = FourCoreLeaderboards()
    boards.add_entry(LeaderboardEntry(
        workload_id="gemm_dense",
        category=LeaderboardCategory.A_SAME_COMPUTATION,
        target_hardware="i5-12450H",
        reference_hardware="RTX 5090",
        target_metric_val=15.0,
        reference_metric_val=0.4,
        metric_unit="ms",
        ratio=37.5,
        parity_achieved=False,
        evidence_class="MEASURED"
    ))
    boards.add_entry(LeaderboardEntry(
        workload_id="gemm_lr",
        category=LeaderboardCategory.B_EXACT_REDUCED_COMPUTATION,
        target_hardware="i5-12450H",
        reference_hardware="RTX 5090",
        target_metric_val=0.42,
        reference_metric_val=0.35,
        metric_unit="ms",
        ratio=1.2,
        parity_achieved=True,
        evidence_class="MEASURED"
    ))
    summary = boards.summary()
    assert "LEADERBOARD_A_SAME_COMPUTATION" in summary
    assert "LEADERBOARD_B_EXACT_REDUCED_COMPUTATION" in summary
    assert summary["LEADERBOARD_A_SAME_COMPUTATION"]["parity_percentage"] == 0.0
    assert summary["LEADERBOARD_B_EXACT_REDUCED_COMPUTATION"]["parity_percentage"] == 100.0


def test_impossibility_engine():
    engine = ImpossibilityEngine()
    assessment = engine.classify_failure(
        workload_id="large_stream",
        arithmetic_intensity=0.5,
        achieved_vs_target_ratio=0.1,
        contract_is_exact=False,
        uses_dedicated_silicon=False
    )
    assert assessment.impossibility_class == ImpossibilityClass.BANDWIDTH_BOUND
    assert assessment.reformulation_viable is True


def test_rtx5090_gap_engine():
    gap_engine = RTX5090GapEngine()
    decomp = gap_engine.analyze_workload(
        workload_id="dense_llm_attention",
        hyper_latency_ms=18.4,
        rtx5090_latency_ms=4.5,
        arithmetic_intensity=1.2,
        uses_tensor_cores=True
    )
    assert decomp.primary_bottleneck == "MEMORY_BANDWIDTH_BOUND"
    assert "Hypothesis:" in decomp.next_research_hypothesis
