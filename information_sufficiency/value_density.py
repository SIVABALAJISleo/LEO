"""
information_sufficiency/value_density.py
Evaluates the Computation Value Density (Information Gain / Cost) of computational stages,
enabling prioritization of high-value paths and elimination of marginal computation.
"""

from typing import Dict, Any, List
import numpy as np


class ComputationValueDensityEvaluator:
    """Calculates information value per unit of computational work."""

    @staticmethod
    def evaluate_stage(
        stage_name: str,
        information_gain_bits: float,
        flops: int,
        bytes_transferred: int,
        latency_us: float
    ) -> Dict[str, Any]:
        """Scores a computational stage by its information density."""
        # Cost metric: composite of FLOPs and memory bytes
        work_units = flops + bytes_transferred * 4
        # Value density = bits of entropy reduced or precision gained per work unit
        value_density = (information_gain_bits * 1e6) / max(work_units, 1)

        # Classify value tier
        if value_density > 10.0:
            tier = "CRITICAL_VALUE"
            action = "EXECUTE_PRIORITY"
        elif value_density > 1.0:
            tier = "STANDARD_VALUE"
            action = "EXECUTE"
        elif value_density > 0.1:
            tier = "MARGINAL_VALUE"
            action = "CONDITIONAL_APPROXIMATION"
        else:
            tier = "NEGLIGIBLE_VALUE"
            action = "ELIMINATE_OR_PRUNE"

        return {
            "stage_name": stage_name,
            "information_gain_bits": information_gain_bits,
            "work_units": work_units,
            "latency_us": latency_us,
            "value_density": float(value_density),
            "value_tier": tier,
            "recommended_action": action
        }

    @staticmethod
    def rank_stages(stages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks a list of candidate computational stages by value density in descending order."""
        evaluated = [
            ComputationValueDensityEvaluator.evaluate_stage(
                stage_name=s.get("name", "stage"),
                information_gain_bits=s.get("info_gain", 1.0),
                flops=s.get("flops", 1000),
                bytes_transferred=s.get("bytes", 100),
                latency_us=s.get("latency_us", 10.0)
            )
            for s in stages
        ]
        return sorted(evaluated, key=lambda x: x["value_density"], reverse=True)
