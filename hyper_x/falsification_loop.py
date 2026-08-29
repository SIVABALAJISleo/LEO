"""
hyper_x/falsification_loop.py
=============================================================================
HYPER-X: Scientific Falsification & Reformulation Ledger
=============================================================================
Implements the active scientific search loop:
    Formulate -> Reduce -> Execute -> Verify -> Falsify -> Reformulate
Maintains a persistent record of failure reasons to guide representation discovery.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger("FalsificationLoop")

@dataclass
class FalsificationRecord:
    timestamp: float
    workload_domain: str
    formulation_id: str
    formulation_name: str
    failure_mode: str          # "TOLERANCE_VIOLATION", "SSIM_BELOW_THRESHOLD", "LATENCY_OVERRUN"
    measured_value: float
    required_threshold: float
    diagnosis: str
    suggested_adaptation: str

class ScientificFalsificationLoop:
    """Scientific falsification engine tracking algorithm viability and guiding reformulation."""

    def __init__(self):
        self.history: List[FalsificationRecord] = []
        self.formulation_scores: Dict[str, float] = {
            "FORM_SPARSE": 1.0,
            "FORM_LOW_RANK": 1.0,
            "FORM_MORTON": 1.2,
            "FORM_FREQUENCY": 0.8,
            "FORM_TERNARY": 0.9,
            "FORM_RESIDUAL": 1.5,
            "FORM_GRAPHICS_EVENT": 1.8,
            "FORM_GRAPHICS_HIERARCHICAL": 1.4
        }

    def record_falsification(
        self,
        domain: str,
        formulation_id: str,
        formulation_name: str,
        failure_mode: str,
        measured_val: float,
        threshold_val: float,
        diagnosis: str,
        adaptation: str
    ) -> FalsificationRecord:
        record = FalsificationRecord(
            timestamp=time.time(),
            workload_domain=domain,
            formulation_id=formulation_id,
            formulation_name=formulation_name,
            failure_mode=failure_mode,
            measured_value=measured_val,
            required_threshold=threshold_val,
            diagnosis=diagnosis,
            suggested_adaptation=adaptation
        )
        self.history.append(record)
        
        # Penalize failing formulation in score weights
        prev_score = self.formulation_scores.get(formulation_id, 1.0)
        self.formulation_scores[formulation_id] = max(0.1, prev_score * 0.8)

        logger.warning(f"[FALSIFIED] {formulation_name}: {failure_mode} ({measured_val:.4f} vs threshold {threshold_val:.4f}). Adaptation: {adaptation}")
        return record

    def record_success(self, formulation_id: str, cer: float):
        """Reinforces formulation weight upon contract verification."""
        prev = self.formulation_scores.get(formulation_id, 1.0)
        self.formulation_scores[formulation_id] = min(3.0, prev + (0.1 * cer))

    def get_ranked_formulations(self, available_formulations: List[Any]) -> List[Any]:
        """Ranks candidate formulations by empirical historical success score."""
        return sorted(
            available_formulations,
            key=lambda f: self.formulation_scores.get(f.formulation_id, 1.0),
            reverse=True
        )

    def get_falsification_summary(self) -> Dict[str, Any]:
        return {
            "total_falsifications_recorded": len(self.history),
            "current_formulation_weights": self.formulation_scores,
            "recent_falsifications": [asdict(r) for r in self.history[-5:]]
        }
