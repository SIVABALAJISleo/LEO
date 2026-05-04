import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from .risk_engine import RiskEngine
from .sufficiency_engine import InputContractEngine
from .interpretation_engine import InterpretationEngine
from .cascade_engine import CascadeEngine
from .dual_reasoning_engine import DualReasoningEngine
from .reasoning_engine import ReasoningEngine
from .compute_optimizer import ComputeMinimizationEngine
from .trust_engine import ConsensusEngine
from .ood_detector import OODDetector
from .edge_case_detector import EdgeCaseDetector
from .temporal_engine import TemporalEngine
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV38Response, LeoStatus, RiskLevel, ComputeLevel
)

class LeoV38Orchestrator:
    """
    SYSTEM: LEO ULTRA PRECISION CORE v38.0
    Objective: 99% accuracy, <10% GPU dependency.
    """
    def __init__(self, conf_threshold: float = 0.92):
        self.risk_engine = RiskEngine()
        self.input_contract = InputContractEngine()
        self.interpreter = InterpretationEngine()
        self.cascade = CascadeEngine()
        self.dual_reasoner = DualReasoningEngine()
        self.reasoner = ReasoningEngine()
        self.compute_engine = ComputeMinimizationEngine()
        self.consensus = ConsensusEngine()
        self.ood = OODDetector()
        self.edge_detector = EdgeCaseDetector()
        self.temporal = TemporalEngine()
        self.cache = SemanticCache(threshold=0.92)
        self.conf_threshold = conf_threshold

    async def run(self, user_input: str) -> LeoV38Response:
        # [1] INPUT CONTRACT GATE
        is_in_domain, risk, msg = self.risk_engine.precheck(user_input)
        if not is_in_domain:
            return self._abstain(msg, risk)
            
        contract = self.input_contract.validate(user_input)
        if contract["status"] != "VALID":
            return self._abstain(f"CONTRACT_FAIL: {contract.get('reason', contract.get('missing'))}", risk)

        # [2] AMBIGUITY EXPANDER
        interpretations = self.interpreter.generate_interpretations(user_input)
        
        all_interp_results = []
        compute_method = "SMALL_MODEL"

        for interp in interpretations:
            # [3] CACHE-FIRST EXECUTION
            key = f"{interp['goal']} {user_input}"
            cached = self.cache.query(key)
            if cached:
                all_interp_results.append({"output": cached.code, "confidence": 1.0})
                compute_method = "CACHE"
                continue

            # [4] CASCADE / SPECULATIVE ENGINE
            draft, d_conf = self.cascade.generate_draft(user_input)
            if self.cascade.verifier_accepts(draft, d_conf):
                winner, conf = draft, d_conf
            else:
                # [5] DUAL REASONING VALIDATION (Fallback to heavy)
                compute_method = "LARGE_MODEL"
                success, winner, err = self.dual_reasoner.solve(interp)
                if not success:
                    return self._abstain(err, risk, LeoStatus.UNSTABLE)
                conf = 0.98

            # [6] COMPUTE MINIMIZATION (Pre-optimization)
            # [7] UNCERTAINTY + EDGE DETECTION
            if self.edge_detector.is_edge_case(user_input):
                return self._abstain("EDGE_CASE_REJECTED", risk)
            
            all_interp_results.append({"output": winner, "confidence": conf})

        # [5] CONSENSUS check across interpretations
        outputs = [r["output"] for r in all_interp_results]
        has_consensus, winner, agreement = self.consensus.check_consensus(outputs)
        
        # Aggressive Uncertainty check
        avg_conf = sum(r["confidence"] for r in all_interp_results) / len(all_interp_results)
        if avg_conf < self.conf_threshold or not has_consensus:
            return self._abstain(f"LOW_CONFIDENCE: Score {avg_conf:.2f}, Consensus={has_consensus}", risk)

        # [8] TEMPORAL VALIDATION
        valid_until = (datetime.now() + timedelta(hours=4)).isoformat()
        c_level = self.compute_engine.get_compute_level(compute_method)

        # [9] FINAL DECISION ENGINE
        return LeoV38Response(
            answer=winner,
            confidence=avg_conf,
            status=LeoStatus.VERIFIED,
            risk=risk,
            compute_used=ComputeLevel(c_level),
            valid_until=valid_until,
            alternatives=outputs[1:3]
        )

    def _abstain(self, reason: str, risk: RiskLevel, status: LeoStatus = LeoStatus.ABSTAIN) -> LeoV38Response:
        return LeoV38Response(
            status=status,
            confidence=0.0,
            risk=risk,
            compute_used=ComputeLevel.LOW,
            valid_until=datetime.now().isoformat(),
            alternatives=[],
            answer=None
        )
吐
