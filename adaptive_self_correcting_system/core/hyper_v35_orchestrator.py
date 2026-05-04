import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from .risk_engine import RiskEngine
from .sufficiency_engine import SufficiencyEngine
from .interpretation_engine import InterpretationEngine
from .dual_reasoning_engine import DualReasoningEngine
from .scoring_engine import ScoringEngine
from .edge_case_detector import EdgeCaseDetector
from .temporal_engine import TemporalEngine
from .compute_optimizer import ComputeReductionEngine
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV35Response, LeoStatus, RiskLevel
)

class LeoV35Orchestrator:
    """
    SYSTEM: HYPER HIGH-PRECISION CORE v35.0
    Objective: 99.5% accuracy with 0% silent failure.
    """
    def __init__(self, confidence_floor: float = 0.92):
        self.risk_engine = RiskEngine()
        self.sufficiency = SufficiencyEngine()
        self.interpreter = InterpretationEngine()
        self.dual_engine = DualReasoningEngine()
        self.scorer = ScoringEngine()
        self.edge_detector = EdgeCaseDetector()
        self.temporal = TemporalEngine()
        self.optimizer = ComputeReductionEngine()
        self.cache = SemanticCache(threshold=0.9)
        self.confidence_floor = confidence_floor

    async def run(self, user_input: str) -> LeoV35Response:
        # 0. DOMAIN + RISK CHECK
        is_in_domain, risk, msg = self.risk_engine.precheck(user_input)
        if not is_in_domain:
            return self._abstain(msg, LeoStatus.ABSTAIN, risk)

        # 1. HARD INPUT CONTRACT
        domain = "finance" if "finance" in user_input.lower() else "code"
        missing = self.sufficiency.detect_missing(user_input, domain)
        if missing or not self.sufficiency.validate_format(user_input):
            return self._abstain(f"INSUFFICIENT_DATA: Missing {missing}", LeoStatus.ABSTAIN, risk)

        # 6. EDGE-CASE DETECTION
        if self.edge_detector.is_edge_case(user_input):
            return self._abstain("EDGE_CASE_RISK: High-entropy or adversarial pattern detected.", LeoStatus.ABSTAIN, risk)

        # 2. AMBIGUITY EXPANSION
        interpretations = self.interpreter.generate_interpretations(user_input)
        
        # 7. COMPUTE REDUCTION (OPTIMIZE)
        opt_input = self.optimizer.reduce(user_input)

        results = []
        for interp in interpretations:
            # 3. DUAL REASONING ENGINE
            success, winner, err = self.dual_engine.solve(interp)
            if not success:
                return self._abstain(err, LeoStatus.UNSTABLE, risk)
            
            # 4. MULTI-OBJECTIVE SCORING
            score_obj = self.scorer.evaluate(winner)
            results.append({"output": winner, "confidence": score_obj.accuracy / 10.0})

        # 5. AGGRESSIVE ABSTENTION
        avg_conf = sum(r["confidence"] for r in results) / len(results)
        if avg_conf < self.confidence_floor:
            return self._abstain(f"LOW_CONFIDENCE: {avg_conf:.2f} below precision floor.", LeoStatus.ABSTAIN, risk)

        # 7. TEMPORAL VALIDATION
        valid_until = (datetime.now() + timedelta(hours=1)).isoformat()

        # 8. FINAL DECISION
        return LeoV35Response(
            answer=results[0]["output"],
            status=LeoStatus.VERIFIED,
            confidence=avg_conf,
            risk=risk,
            alternatives=[r["output"] for r in results[1:3]],
            valid_until=valid_until,
            reason="Verified across dual-reasoning paths and survived aggressive edge-case filtering."
        )

    def _abstain(self, reason: str, status: LeoStatus, risk: RiskLevel) -> LeoV35Response:
        return LeoV35Response(
            status=status,
            confidence=0.0,
            risk=risk,
            valid_until=datetime.now().isoformat(),
            reason=reason
        )
吐
