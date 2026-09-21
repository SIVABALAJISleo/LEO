"""
hyper/universal/parity/scorecard.py
===================================
Universal Parity Scorecard.
Computes dimension-by-dimension comparative evaluations across HYPER and the RTX 5090 reference.
Never compresses all dimensions into one single misleading percentage.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from .parity_vector import ParityVector, ParityClass


class UniversalParityScorecard:
    """Generates rigorous multi-dimensional parity scorecard comparing HYPER to RTX 5090."""

    @staticmethod
    def evaluate(
        hyper_vector: ParityVector,
        rtx_vector: ParityVector,
        claim_level: int = 2,
    ) -> Dict[str, Any]:
        dimensions = [
            {
                "dimension": "LATENCY",
                "unit": "ms",
                "hyper": hyper_vector.latency_ms,
                "rtx_5090": rtx_vector.latency_ms,
                "ratio_hyper_vs_rtx": round(rtx_vector.latency_ms / max(1e-6, hyper_vector.latency_ms), 2),
                "status": "PARITY_REACHED" if hyper_vector.latency_ms <= rtx_vector.latency_ms else "SUB_PARITY",
            },
            {
                "dimension": "THROUGHPUT",
                "unit": "ops/s",
                "hyper": hyper_vector.throughput_ops_per_sec,
                "rtx_5090": rtx_vector.throughput_ops_per_sec,
                "ratio_hyper_vs_rtx": round(hyper_vector.throughput_ops_per_sec / max(1e-6, rtx_vector.throughput_ops_per_sec), 2),
                "status": "PARITY_REACHED" if hyper_vector.throughput_ops_per_sec >= rtx_vector.throughput_ops_per_sec else "SUB_PARITY",
            },
            {
                "dimension": "PEAK_MEMORY",
                "unit": "MB",
                "hyper": hyper_vector.memory_peak_mb,
                "rtx_5090": rtx_vector.memory_peak_mb,
                "ratio_hyper_vs_rtx": round(hyper_vector.memory_peak_mb / max(1e-6, rtx_vector.memory_peak_mb), 2),
                "status": "MEMORY_EFFICIENT" if hyper_vector.memory_peak_mb <= rtx_vector.memory_peak_mb else "HIGH_MEMORY",
            },
            {
                "dimension": "ENERGY_CONSUMPTION",
                "unit": "mJ",
                "hyper": hyper_vector.energy_mj,
                "rtx_5090": rtx_vector.energy_mj,
                "ratio_hyper_vs_rtx": round(rtx_vector.energy_mj / max(1e-6, hyper_vector.energy_mj), 2),
                "status": "ENERGY_SUPERIOR" if hyper_vector.energy_mj < rtx_vector.energy_mj else "ENERGY_INFERIOR",
            },
            {
                "dimension": "CORRECTNESS",
                "unit": "binary",
                "hyper": "PASS" if hyper_vector.correctness_binary else "FAIL",
                "rtx_5090": "PASS",
                "status": "PASS" if hyper_vector.correctness_binary else "FAIL",
            },
            {
                "dimension": "RAW_HARDWARE_PARITY",
                "unit": "silicon",
                "hyper": "Intel Core i5-12450H (45W) + Intel UHD 48EU",
                "rtx_5090": "NVIDIA Blackwell GB202 (600W)",
                "status": "NOT_ACHIEVED (PHYSICALLY_DISJOINT)",
            },
        ]

        return {
            "claim_level": claim_level,
            "dimensions": dimensions,
            "hyper_metrics": hyper_vector.to_dict(),
            "rtx5090_metrics": rtx_vector.to_dict(),
            "summary_verdict": "CONTRACT_OR_ALGORITHMIC_SHORTCUT_EVALUATED",
        }
