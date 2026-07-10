"""
backend/analytics/telemetry_collector.py
Privacy-first real-user telemetry for the LEO Infinity Evolution Cycle.

All data is anonymized:
  - No raw queries are stored, only prompt class labels.
  - Hardware identifiers are SHA-256 hashed.
  - Local-first JSONL storage with optional Supabase sync stub.
  - Data feeds back into the evolution loop for weakness prioritization.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TelemetryCollector:
    """Privacy-first telemetry collector for inference and evolution events.

    Stores anonymized JSONL entries locally. Optional Supabase sync is
    stubbed for future integration.

    Args:
        storage_dir: Local directory for telemetry JSONL files.
        opt_in: If False, all recording methods are no-ops.
    """

    def __init__(self, storage_dir: str = "backend/analytics", opt_in: bool = True):
        self.storage_dir = storage_dir
        self.opt_in = opt_in
        self._inference_path = os.path.join(storage_dir, "telemetry_inferences.jsonl")
        self._evolution_path = os.path.join(storage_dir, "telemetry_evolution.jsonl")

        if self.opt_in:
            os.makedirs(storage_dir, exist_ok=True)

    @staticmethod
    def anonymize_hardware(hardware_info: Dict[str, Any]) -> str:
        """SHA-256 hash of hardware profile for anonymous correlation."""
        raw = json.dumps(hardware_info, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def record_inference(
        self,
        prompt_class: str,
        latency_ms: float,
        was_avoided: bool,
        hardware_hash: Optional[str] = None,
        tokens_generated: int = 0,
        energy_joules: float = 0.0,
    ):
        """Record an anonymized inference event."""
        if not self.opt_in:
            return

        entry = {
            "ts": time.time(),
            "type": "inference",
            "prompt_class": prompt_class,
            "latency_ms": round(latency_ms, 2),
            "was_avoided": was_avoided,
            "tokens": tokens_generated,
            "energy_j": round(energy_joules, 6),
            "hw_hash": hardware_hash or "unknown",
        }
        self._append_jsonl(self._inference_path, entry)

    def record_evolution(
        self,
        generation: int,
        fitness: float,
        weaknesses: List[str],
        mutations: Dict[str, Any],
    ):
        """Record an evolution cycle event."""
        if not self.opt_in:
            return

        entry = {
            "ts": time.time(),
            "type": "evolution",
            "generation": generation,
            "fitness": round(fitness, 6),
            "weaknesses": weaknesses,
            "mutations": mutations,
        }
        self._append_jsonl(self._evolution_path, entry)

    def get_aggregated_insights(self) -> Dict[str, Any]:
        """Compute aggregate insights from stored inference telemetry."""
        entries = self._read_jsonl(self._inference_path)
        if not entries:
            return {"total_inferences": 0}

        total = len(entries)
        avoided = sum(1 for e in entries if e.get("was_avoided"))
        classes: Dict[str, int] = {}
        total_latency = 0.0

        for e in entries:
            cls = e.get("prompt_class", "unknown")
            classes[cls] = classes.get(cls, 0) + 1
            total_latency += e.get("latency_ms", 0.0)

        return {
            "total_inferences": total,
            "avoidance_rate_pct": round(avoided / max(1, total) * 100, 2),
            "avg_latency_ms": round(total_latency / max(1, total), 2),
            "class_distribution": classes,
            "top_avoided_class": max(
                ((cls, sum(1 for e in entries if e.get("prompt_class") == cls and e.get("was_avoided")))
                 for cls in classes),
                key=lambda x: x[1],
                default=("none", 0),
            )[0],
        }

    def export_for_evolution(self) -> Dict[str, Any]:
        """Export telemetry data formatted for the evolution loop's weakness analysis."""
        insights = self.get_aggregated_insights()
        # Identify underperforming classes (high latency or low avoidance)
        entries = self._read_jsonl(self._inference_path)
        class_stats: Dict[str, Dict[str, Any]] = {}
        for e in entries:
            cls = e.get("prompt_class", "unknown")
            if cls not in class_stats:
                class_stats[cls] = {"count": 0, "avoided": 0, "total_latency": 0.0}
            class_stats[cls]["count"] += 1
            if e.get("was_avoided"):
                class_stats[cls]["avoided"] += 1
            class_stats[cls]["total_latency"] += e.get("latency_ms", 0.0)

        weak_classes = []
        for cls, stats in class_stats.items():
            avoid_rate = stats["avoided"] / max(1, stats["count"]) * 100
            avg_lat = stats["total_latency"] / max(1, stats["count"])
            if avoid_rate < 80.0 or avg_lat > 200.0:
                weak_classes.append({"class": cls, "avoidance_pct": avoid_rate, "avg_latency_ms": avg_lat})

        return {
            "insights": insights,
            "weak_classes": weak_classes,
        }

    def _append_jsonl(self, path: str, entry: Dict[str, Any]):
        """Append a JSON line to a file."""
        try:
            with open(path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Telemetry write failed: {e}")

    def _read_jsonl(self, path: str) -> List[Dict[str, Any]]:
        """Read all JSON lines from a file."""
        if not os.path.exists(path):
            return []
        entries = []
        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            logger.error(f"Telemetry read failed: {e}")
        return entries


# Singleton
_collector = TelemetryCollector()


def get_telemetry_collector() -> TelemetryCollector:
    return _collector
