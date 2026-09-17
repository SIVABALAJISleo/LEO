"""
backend/caoe/telemetry.py
=========================
CAOE Real-Time Measurement & Telemetry Layer.

Records execution telemetry and computes aggregate parity statistics:
- Contract Parity % = (contract_met_count / total_runs) * 100
- Exact Parity % = (1.0 - mean_relative_error) * 100
- Average Speedup vs Baseline
- Cache Hit Rate %
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional


class TelemetryLayer:
    """Real-time execution measurement and parity tracker."""

    def __init__(self, log_path: Optional[str] = None) -> None:
        self._records: List[Dict[str, Any]] = []
        self._log_path = log_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "reports", "caoe_telemetry.jsonl"
        )
        os.makedirs(os.path.dirname(self._log_path), exist_ok=True)

    def record_execution(
        self,
        execution_id: str,
        shape: Any,
        precision: int,
        sparsity_eliminated: float,
        executor: str,
        latency_ms: float,
        speedup: float,
        contract_met: bool,
        error_rel: float,
        cache_hit: bool,
        notes: str = "",
    ) -> Dict[str, Any]:
        metric = {
            "execution_id": execution_id,
            "timestamp": time.time(),
            "input_shape": list(shape) if hasattr(shape, "__iter__") else str(shape),
            "precision": precision,
            "sparsity_eliminated_pct": round(sparsity_eliminated * 100.0, 1),
            "executor": executor,
            "latency_ms": round(latency_ms, 4),
            "speedup": round(speedup, 2),
            "contract_met": bool(contract_met),
            "error_rel": float(error_rel),
            "cache_hit": bool(cache_hit),
            "notes": notes,
        }

        self._records.append(metric)

        try:
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(metric) + "\n")
        except Exception:
            pass

        return metric

    def aggregate_metrics(self) -> Dict[str, Any]:
        """Compute aggregate contract parity, exact parity, and speedup."""
        if not self._records:
            return {
                "contract_parity_pct": 100.0,
                "exact_parity_pct": 100.0,
                "avg_speedup": 1.0,
                "cache_hit_rate_pct": 0.0,
                "total_runs": 0,
            }

        total = len(self._records)
        contracts_passed = sum(1 for r in self._records if r["contract_met"])
        cache_hits = sum(1 for r in self._records if r["cache_hit"])
        speedups = [r["speedup"] for r in self._records]
        rel_errors = [min(1.0, r["error_rel"]) for r in self._records]

        contract_parity = (contracts_passed / total) * 100.0
        exact_parity = max(0.0, (1.0 - (sum(rel_errors) / total))) * 100.0
        avg_speedup = sum(speedups) / total
        cache_hit_rate = (cache_hits / total) * 100.0

        return {
            "contract_parity_pct": round(contract_parity, 1),
            "exact_parity_pct": round(exact_parity, 1),
            "avg_speedup": round(avg_speedup, 2),
            "cache_hit_rate_pct": round(cache_hit_rate, 1),
            "total_runs": total,
        }
