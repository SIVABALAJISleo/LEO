"""
tests/test_closure_dashboard.py
================================
Regression tests for the WorkloadClosureDashboard.
Validates: closure gate logic, route stats aggregation,
adaptation health ingestion, Markdown/JSON export.
"""

import json
import time
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from hyper_x.wormhole_compiler.closure_dashboard import (
    WorkloadClosureDashboard,
    ClosureReport,
    RouteStats,
)
from hyper_x.wormhole_compiler.online_adaptation_engine import (
    OnlineAdaptationEngine,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_decision(route: str, baseline: float = 1000.0, wer: float = 0.5,
                   exact: bool = True, verified: bool = True):
    """Creates a mock BreakthroughRouteDecision-like object."""
    d = MagicMock()
    d.route = route
    d.baseline_work = baseline
    d.required_work = baseline * (1.0 - wer)
    d.work_elimination_ratio = wer
    d.exact = exact
    d.verification_status = "PASSED" if verified else "FALSIFIED"
    d.latency_ms = 1.5
    d.baseline_latency_ms = 3.0
    d.speedup = 2.0
    return d


def _make_router_with_history(decisions):
    router = MagicMock()
    router.routing_history = decisions
    return router


def _make_registry(entries):
    from hyper_x.wormhole_compiler.workload_registry import (
        WorkloadRegistryEntry,
        WorkloadOutcome,
    )
    registry = MagicMock()
    registry.entries = {e.workload_id: e for e in entries}
    return registry


def _make_registry_entry(workload_id: str, outcome: str,
                          exact: bool = True, contract_ok: bool = True):
    from hyper_x.wormhole_compiler.workload_registry import (
        WorkloadRegistryEntry,
        WorkloadOutcome,
    )
    return WorkloadRegistryEntry(
        workload_id=workload_id,
        domain="TEST",
        contract_mode="EXACT",
        observable="output_tensor",
        outcome=WorkloadOutcome(outcome),
        speedup=2.0,
        work_elimination_ratio=0.5,
        gadr=0.8,
        hae=0.7,
        provenance_verified=True,
        holdout_passed=True,
        exact_correctness=exact,
        contract_correctness=contract_ok,
    )


# ---------------------------------------------------------------------------
# RouteStats unit tests
# ---------------------------------------------------------------------------

class TestRouteStats:
    def test_mean_wer_zero_when_no_invocations(self):
        s = RouteStats(route="EXACT_SPARSE")
        assert s.mean_wer == 0.0

    def test_mean_wer_computed_correctly(self):
        s = RouteStats(route="EXACT_SPARSE")
        s.invocation_count = 2
        s.total_baseline_work = 1000.0
        s.total_work_eliminated = 400.0
        assert abs(s.mean_wer - 0.4) < 1e-6

    def test_accuracy_rate_no_checks(self):
        s = RouteStats(route="CPU_REFERENCE_FALLBACK")
        assert s.accuracy_rate == 1.0

    def test_accuracy_rate_with_failures(self):
        s = RouteStats(route="EXACT_SPARSE")
        s.verified_count = 8
        s.falsified_count = 2
        assert abs(s.accuracy_rate - 0.8) < 1e-6

    def test_to_dict_keys(self):
        s = RouteStats(route="EXACT_ROW_DELTA", invocation_count=5)
        d = s.to_dict()
        assert "route" in d
        assert "invocations" in d
        assert "mean_work_elimination_ratio" in d
        assert "accuracy_rate" in d


# ---------------------------------------------------------------------------
# ClosureReport unit tests
# ---------------------------------------------------------------------------

class TestClosureReport:
    def test_to_dict_structure(self):
        r = ClosureReport(
            total_workloads_evaluated=10,
            wormholes_found=7,
            necessity_proven=3,
            search_inconclusive=0,
            closure_ratio=1.0,
            can_claim_100_percent=True,
        )
        d = r.to_dict()
        assert "closure" in d
        assert "work_elimination" in d
        assert "route_breakdown" in d
        assert "adaptation_health" in d
        assert "correctness" in d
        assert d["closure"]["can_claim_100_percent"] is True

    def test_to_markdown_contains_required_sections(self):
        r = ClosureReport(
            total_workloads_evaluated=5,
            wormholes_found=5,
            closure_ratio=1.0,
            can_claim_100_percent=True,
        )
        md = r.to_markdown()
        assert "HYPER-Ω" in md
        assert "Closure Gate" in md
        assert "Work Elimination" in md

    def test_print_summary_does_not_raise(self, capsys):
        r = ClosureReport(
            total_workloads_evaluated=5,
            wormholes_found=3,
            closure_ratio=0.6,
            global_wer=0.4,
            dominant_route="EXACT_SPARSE",
        )
        r.print_summary()  # Should not raise
        captured = capsys.readouterr()
        assert "HYPER" in captured.out


# ---------------------------------------------------------------------------
# WorkloadClosureDashboard integration tests
# ---------------------------------------------------------------------------

class TestClosureDashboardEmpty:
    def test_empty_report_no_100_percent(self):
        dash = WorkloadClosureDashboard()
        report = dash.closure_report()
        assert report.can_claim_100_percent is False
        assert report.total_workloads_evaluated == 0

    def test_empty_report_closure_ratio_zero(self):
        dash = WorkloadClosureDashboard()
        report = dash.closure_report()
        assert report.closure_ratio == 0.0


class TestClosureDashboardWithRouter:
    def test_route_stats_populated_from_history(self):
        decisions = [
            _make_decision("EXACT_SPARSE", wer=0.7),
            _make_decision("EXACT_SPARSE", wer=0.6),
            _make_decision("CPU_REFERENCE_FALLBACK", wer=0.0),
        ]
        router = _make_router_with_history(decisions)
        dash = WorkloadClosureDashboard(router=router)
        report = dash.closure_report()

        assert "EXACT_SPARSE" in report.route_stats
        assert report.route_stats["EXACT_SPARSE"].invocation_count == 2
        assert "CPU_REFERENCE_FALLBACK" in report.route_stats

    def test_dominant_route_is_most_invoked(self):
        decisions = [_make_decision("EXACT_SPARSE")] * 5 + [_make_decision("EXACT_ROW_DELTA")]
        router = _make_router_with_history(decisions)
        dash = WorkloadClosureDashboard(router=router)
        report = dash.closure_report()
        assert report.dominant_route == "EXACT_SPARSE"

    def test_global_wer_computed(self):
        decisions = [_make_decision("EXACT_SPARSE", baseline=1000.0, wer=0.5)] * 4
        router = _make_router_with_history(decisions)
        dash = WorkloadClosureDashboard(router=router)
        report = dash.closure_report()
        # 4 * 500 eliminated / 4 * 1000 baseline = 0.5
        assert abs(report.global_wer - 0.5) < 1e-6


class TestClosureDashboardWithRegistry:
    def test_all_wormholes_claims_100_percent(self):
        entries = [
            _make_registry_entry(f"WL_{i}", "WORMHOLE_FOUND") for i in range(5)
        ]
        registry = _make_registry(entries)
        dash = WorkloadClosureDashboard(registry=registry)
        report = dash.closure_report()
        assert report.closure_ratio == 1.0
        assert report.can_claim_100_percent is True
        assert report.wormholes_found == 5

    def test_inconclusive_blocks_100_percent(self):
        entries = [
            _make_registry_entry("WL_OK", "WORMHOLE_FOUND"),
            _make_registry_entry("WL_INCONC", "SEARCH_INCONCLUSIVE"),
        ]
        registry = _make_registry(entries)
        dash = WorkloadClosureDashboard(registry=registry)
        report = dash.closure_report()
        assert report.can_claim_100_percent is False
        assert any("SEARCH_INCONCLUSIVE" in r or "inconclusive" in r.lower()
                   for r in report.closure_gate_reasons)

    def test_necessity_proven_counts_toward_closure(self):
        entries = [
            _make_registry_entry("WL_1", "WORMHOLE_FOUND"),
            _make_registry_entry("WL_2", "NECESSARY_COMPUTATION_PROVEN"),
        ]
        registry = _make_registry(entries)
        dash = WorkloadClosureDashboard(registry=registry)
        report = dash.closure_report()
        assert report.closure_ratio == 1.0
        assert report.necessity_proven == 1


class TestClosureDashboardWithAdaptation:
    def test_adaptation_health_ingested(self):
        adaptation = OnlineAdaptationEngine(
            failure_file="/nonexistent/path.json", mode="PASSIVE"
        )
        adaptation.record_failure("EXACT_SPARSE", domain="DENSE_GEMM")
        adaptation.record_success("CPU_REFERENCE_FALLBACK", domain="DENSE_GEMM")
        dash = WorkloadClosureDashboard(adaptation=adaptation)
        report = dash.closure_report()
        assert report.adaptation_domains_tracked >= 1
        assert report.adaptation_total_failures >= 1
        assert report.adaptation_global_top_route != "UNKNOWN"


class TestClosureDashboardExport:
    def test_export_json_creates_file(self, tmp_path):
        dash = WorkloadClosureDashboard(output_dir=str(tmp_path))
        report = dash.closure_report()
        out = dash.export_json(report, "test_closure.json")
        assert out.exists()
        data = json.loads(out.read_text())
        assert "closure" in data

    def test_export_markdown_creates_file(self, tmp_path):
        dash = WorkloadClosureDashboard(output_dir=str(tmp_path))
        report = dash.closure_report()
        out = dash.export_markdown(report, "TEST_CLOSURE.md")
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "HYPER" in content

    def test_exported_json_is_valid(self, tmp_path):
        decisions = [_make_decision("EXACT_SPARSE", wer=0.6)] * 3
        router = _make_router_with_history(decisions)
        dash = WorkloadClosureDashboard(router=router, output_dir=str(tmp_path))
        report = dash.closure_report()
        out = dash.export_json(report)
        loaded = json.loads(out.read_text())
        assert loaded["work_elimination"]["global_wer"] > 0


class TestClosureGateReasons:
    def test_gate_open_when_all_conditions_met(self):
        entries = [_make_registry_entry(f"WL_{i}", "WORMHOLE_FOUND") for i in range(3)]
        registry = _make_registry(entries)
        dash = WorkloadClosureDashboard(registry=registry)
        report = dash.closure_report()
        assert report.can_claim_100_percent is True
        assert any("100%" in r or "resolved" in r.lower()
                   for r in report.closure_gate_reasons)

    def test_gate_blocked_by_contract_failure(self):
        entries = [
            _make_registry_entry("WL_FAIL", "WORMHOLE_FOUND", contract_ok=False),
        ]
        registry = _make_registry(entries)
        dash = WorkloadClosureDashboard(registry=registry)
        report = dash.closure_report()
        assert report.can_claim_100_percent is False

    def test_populate_canonical_universe_and_closure(self, tmp_path):
        from hyper_x.wormhole_compiler.workload_registry import UniversalWorkloadRegistry
        reg = UniversalWorkloadRegistry(registry_path=tmp_path / "test_reg.json")
        reg.populate_canonical_universe()
        assert len(reg.entries) >= 7
        dash = WorkloadClosureDashboard(registry=reg, output_dir=str(tmp_path))
        report = dash.closure_report()
        assert report.can_claim_100_percent is True
        assert report.closure_ratio == 1.0
        assert report.search_inconclusive == 0
        assert report.wormholes_found >= 6
        assert report.necessity_proven >= 1
