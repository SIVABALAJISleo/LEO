"""
hyper_x/wormhole_compiler/closure_dashboard.py
=============================================================================
HYPER-Ω: Workload Closure Dashboard (Section 40 — Universal Closure Metric)
=============================================================================
Single-call closure_report() aggregates:
  - WorkloadRegistry (all registered outcomes)
  - OnlineAdaptationEngine priors (learning health)
  - BreakthroughRouter routing history (route distribution)
  - Parity100Gate evaluation (pass/fail closure gate)
  - Per-route work elimination statistics

Output formats: structured dict (JSON-ready), Markdown report, console summary.

Closure Formula:
  closure = (wormholes_found + necessity_proven) / total_evaluated
  100% closure requires: closure == 1.0 AND inconclusive == 0

IMPORTANT: 100% closure is a CONTRACT claim on defined workloads, NOT
a claim of hardware equivalence to RTX 5090.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Route Work Elimination Stats
# ---------------------------------------------------------------------------

@dataclass
class RouteStats:
    route: str
    invocation_count: int = 0
    total_work_eliminated: float = 0.0
    total_baseline_work: float = 0.0
    total_latency_ms: float = 0.0
    exact_count: int = 0
    verified_count: int = 0
    falsified_count: int = 0

    @property
    def mean_wer(self) -> float:
        if self.invocation_count == 0:
            return 0.0
        return self.total_work_eliminated / max(1.0, self.total_baseline_work)

    @property
    def mean_latency_ms(self) -> float:
        return self.total_latency_ms / max(1, self.invocation_count)

    @property
    def accuracy_rate(self) -> float:
        checked = self.verified_count + self.falsified_count
        if checked == 0:
            return 1.0
        return self.verified_count / checked

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route": self.route,
            "invocations": self.invocation_count,
            "mean_work_elimination_ratio": round(self.mean_wer, 4),
            "mean_latency_ms": round(self.mean_latency_ms, 3),
            "accuracy_rate": round(self.accuracy_rate, 4),
            "exact_invocations": self.exact_count,
            "verified_count": self.verified_count,
            "falsified_count": self.falsified_count,
        }


# ---------------------------------------------------------------------------
# Closure Dashboard
# ---------------------------------------------------------------------------

@dataclass
class ClosureReport:
    """Complete workload closure status at a point in time."""
    timestamp: float = field(default_factory=time.time)

    # Registry counts
    total_workloads_evaluated: int = 0
    wormholes_found: int = 0
    necessity_proven: int = 0
    search_inconclusive: int = 0

    # Closure gate
    closure_ratio: float = 0.0
    can_claim_100_percent: bool = False
    closure_gate_reasons: List[str] = field(default_factory=list)

    # Route distribution
    route_stats: Dict[str, RouteStats] = field(default_factory=dict)
    dominant_route: str = "UNKNOWN"
    total_work_eliminated_flops: float = 0.0
    total_baseline_flops: float = 0.0
    global_wer: float = 0.0

    # Adaptation engine health
    adaptation_domains_tracked: int = 0
    adaptation_total_failures: int = 0
    adaptation_global_top_route: str = "UNKNOWN"

    # Contract correctness
    exact_correctness_count: int = 0
    contract_correctness_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "closure": {
                "total_workloads_evaluated": self.total_workloads_evaluated,
                "wormholes_found": self.wormholes_found,
                "necessity_proven": self.necessity_proven,
                "search_inconclusive": self.search_inconclusive,
                "closure_ratio": round(self.closure_ratio, 4),
                "closure_percentage": f"{self.closure_ratio * 100:.2f}%",
                "can_claim_100_percent": self.can_claim_100_percent,
                "closure_gate_reasons": self.closure_gate_reasons,
            },
            "work_elimination": {
                "global_wer": round(self.global_wer, 4),
                "global_wer_pct": f"{self.global_wer * 100:.2f}%",
                "total_baseline_flops": self.total_baseline_flops,
                "total_eliminated_flops": self.total_work_eliminated_flops,
                "dominant_route": self.dominant_route,
            },
            "route_breakdown": {r: s.to_dict() for r, s in self.route_stats.items()},
            "adaptation_health": {
                "domains_tracked": self.adaptation_domains_tracked,
                "total_failures_recorded": self.adaptation_total_failures,
                "global_top_route": self.adaptation_global_top_route,
            },
            "correctness": {
                "exact_correct_workloads": self.exact_correctness_count,
                "contract_correct_workloads": self.contract_correctness_count,
            },
        }

    def to_markdown(self) -> str:
        lines = [
            "# HYPER-Ω Workload Closure Dashboard",
            f"*Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))}*",
            "",
            "## Closure Gate",
            f"| Metric | Value |",
            f"|---|---|",
            f"| Total Workloads Evaluated | {self.total_workloads_evaluated} |",
            f"| Wormholes Found | {self.wormholes_found} |",
            f"| Necessity Proven | {self.necessity_proven} |",
            f"| Search Inconclusive | {self.search_inconclusive} |",
            f"| **Closure Ratio** | **{self.closure_ratio * 100:.2f}%** |",
            f"| Can Claim 100% | {'✅ YES' if self.can_claim_100_percent else '❌ NO'} |",
            "",
        ]
        if self.closure_gate_reasons:
            lines += ["### Gate Reasons", ""]
            for r in self.closure_gate_reasons:
                lines.append(f"- {r}")
            lines.append("")

        lines += [
            "## Work Elimination",
            f"| Route | Invocations | Mean WER | Accuracy |",
            "|---|---|---|---|",
        ]
        for route, stats in sorted(self.route_stats.items(), key=lambda x: -x[1].invocation_count):
            lines.append(
                f"| {route} | {stats.invocation_count} "
                f"| {stats.mean_wer * 100:.1f}% "
                f"| {stats.accuracy_rate * 100:.1f}% |"
            )
        lines += [
            "",
            f"**Global Work Elimination: {self.global_wer * 100:.2f}%**",
            f"**Dominant Route: {self.dominant_route}**",
            "",
            "## Online Adaptation Health",
            f"- Domains tracked: {self.adaptation_domains_tracked}",
            f"- Total failures recorded: {self.adaptation_total_failures}",
            f"- Global top route: {self.adaptation_global_top_route}",
        ]
        return "\n".join(lines)

    def print_summary(self) -> None:
        closure_bar = "█" * int(self.closure_ratio * 20) + "░" * (20 - int(self.closure_ratio * 20))
        wer_bar = "█" * int(self.global_wer * 20) + "░" * (20 - int(self.global_wer * 20))
        gate = "✅ OPEN" if self.can_claim_100_percent else "❌ BLOCKED"
        print(f"""
╔══════════════════════════════════════════════════════════╗
║         HYPER-Ω WORKLOAD CLOSURE DASHBOARD               ║
╠══════════════════════════════════════════════════════════╣
║  Closure   [{closure_bar}] {self.closure_ratio * 100:5.1f}%  ║
║  Work Elim [{wer_bar}] {self.global_wer * 100:5.1f}%  ║
║  Gate: {gate:<50}║
║  Dominant Route: {self.dominant_route:<39}║
║  Workloads: {self.total_workloads_evaluated:<4} | Wormholes: {self.wormholes_found:<4} | Necessary: {self.necessity_proven:<4}  ║
╚══════════════════════════════════════════════════════════╝""")


class WorkloadClosureDashboard:
    """
    Aggregates state from all HYPER-Ω subsystems into one closure report.

    Usage:
        dashboard = WorkloadClosureDashboard(router=router, adaptation=engine)
        report = dashboard.closure_report()
        report.print_summary()
        json.dump(report.to_dict(), open("closure.json", "w"), indent=2)
    """

    ALL_11_ROUTES = [
        "EXACT_CONTENT_REUSE",
        "EXACT_CACHE",
        "EXACT_ZERO_ROW_PRUNE",
        "EXACT_SPARSE",
        "EXACT_ROW_DELTA",
        "EXACT_RESIDUAL",
        "OUTPUT_SENSITIVE",
        "EXACT_FACTORIZATION",
        "VERIFIED_ALTERNATIVE_ALGO",
        "CPU_IGPU_HETEROGENEOUS",
        "CPU_REFERENCE_FALLBACK",
        # Alias names that may appear in history
        "PREDICTIVE_TEMPORAL",
        "APPROXIMATE_LOW_RANK",
    ]

    def __init__(
        self,
        router: Optional[Any] = None,
        adaptation: Optional[Any] = None,
        registry: Optional[Any] = None,
        output_dir: str = ".",
    ):
        self.router = router
        self.adaptation = adaptation
        self.registry = registry
        self.output_dir = Path(output_dir)

    # ------------------------------------------------------------------
    # Main report generation
    # ------------------------------------------------------------------

    def closure_report(self) -> ClosureReport:
        """Generates a complete closure report from all available subsystems."""
        report = ClosureReport()

        # --- Registry stats ---
        if self.registry is not None:
            self._ingest_registry(report)

        # --- Router routing history ---
        if self.router is not None:
            self._ingest_router_history(report)

        # --- Adaptation engine ---
        if self.adaptation is not None:
            self._ingest_adaptation(report)

        # --- Closure gate evaluation ---
        self._evaluate_closure_gate(report)

        # --- Global WER ---
        if report.total_baseline_flops > 0:
            report.global_wer = report.total_work_eliminated_flops / report.total_baseline_flops

        # --- Dominant route ---
        if report.route_stats:
            report.dominant_route = max(
                report.route_stats, key=lambda r: report.route_stats[r].invocation_count
            )

        return report

    # ------------------------------------------------------------------
    # Subsystem ingestion
    # ------------------------------------------------------------------

    def _ingest_registry(self, report: ClosureReport) -> None:
        from hyper_x.wormhole_compiler.workload_registry import WorkloadOutcome
        entries = self.registry.entries
        report.total_workloads_evaluated = len(entries)
        for entry in entries.values():
            if entry.outcome == WorkloadOutcome.WORMHOLE_FOUND:
                report.wormholes_found += 1
            elif entry.outcome == WorkloadOutcome.NECESSARY_COMPUTATION_PROVEN:
                report.necessity_proven += 1
            else:
                report.search_inconclusive += 1
            if entry.exact_correctness:
                report.exact_correctness_count += 1
            if entry.contract_correctness:
                report.contract_correctness_count += 1

    def _ingest_router_history(self, report: ClosureReport) -> None:
        history = getattr(self.router, "routing_history", [])
        for decision in history:
            route = decision.route
            if route not in report.route_stats:
                report.route_stats[route] = RouteStats(route=route)
            s = report.route_stats[route]
            s.invocation_count += 1
            s.total_baseline_work += decision.baseline_work
            eliminated = decision.baseline_work - decision.required_work
            s.total_work_eliminated += max(0.0, eliminated)
            s.total_latency_ms += decision.latency_ms
            if decision.exact:
                s.exact_count += 1
            if decision.verification_status in ("PASSED", "VERIFIED"):
                s.verified_count += 1
            elif decision.verification_status == "FALSIFIED":
                s.falsified_count += 1

            report.total_baseline_flops += decision.baseline_work
            report.total_work_eliminated_flops += max(0.0, eliminated)

    def _ingest_adaptation(self, report: ClosureReport) -> None:
        summary = self.adaptation.summary()
        report.adaptation_domains_tracked = summary.get("domains_tracked", 0)
        report.adaptation_total_failures = summary.get("total_failures_recorded", 0)
        report.adaptation_global_top_route = summary.get("global_top_route", "UNKNOWN")

    def _evaluate_closure_gate(self, report: ClosureReport) -> None:
        total = report.total_workloads_evaluated
        resolved = report.wormholes_found + report.necessity_proven
        report.closure_ratio = resolved / max(1, total)
        reasons = []

        if total == 0:
            reasons.append("No workloads registered — closure cannot be evaluated.")
            report.can_claim_100_percent = False
            report.closure_gate_reasons = reasons
            return

        if report.search_inconclusive > 0:
            reasons.append(
                f"{report.search_inconclusive} workload(s) remain SEARCH_INCONCLUSIVE — "
                "must be resolved (wormhole found OR necessity proven)."
            )

        if report.closure_ratio < 1.0:
            reasons.append(
                f"Closure ratio is {report.closure_ratio * 100:.2f}% — must reach 100%."
            )

        if report.total_workloads_evaluated > 0 and report.contract_correctness_count < report.total_workloads_evaluated:
            gap = report.total_workloads_evaluated - report.contract_correctness_count
            reasons.append(f"{gap} workload(s) did not meet contract correctness.")

        report.can_claim_100_percent = len(reasons) == 0
        if report.can_claim_100_percent:
            reasons.append("All workloads resolved. 100% closure on registered workload set.")
        report.closure_gate_reasons = reasons

    # ------------------------------------------------------------------
    # File export
    # ------------------------------------------------------------------

    def export_json(self, report: ClosureReport, filename: str = "closure_report.json") -> Path:
        out = self.output_dir / filename
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report.to_dict(), indent=2, default=str), encoding="utf-8")
        return out

    def export_markdown(self, report: ClosureReport, filename: str = "CLOSURE_DASHBOARD.md") -> Path:
        out = self.output_dir / filename
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report.to_markdown(), encoding="utf-8")
        return out
