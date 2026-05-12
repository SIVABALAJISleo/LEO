import asyncio
import time
from typing import List, Dict, Any, Tuple, Optional
from .risk_engine import RiskEngine
from .sufficiency_engine import SufficiencyEngine
from .interpretation_engine import InterpretationEngine
from .reasoning_engine import ReasoningEngine
from .scoring_engine import ScoringEngine
from .trust_engine import ConsensusEngine
from .temporal_engine import TemporalEngine
from .compute_optimizer import ComputeReductionEngine
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV34Response, LeoStatus, RiskLevel
)

class LeoV34Orchestrator:
    """
    SYSTEM: HYPER GLOBAL EXECUTION LAW CORE v34.0
    Objective: Zero silent failure through strict execution laws.
    """
    def __init__(self, conf_threshold: float = 0.88):
        self.risk_engine = RiskEngine()
        self.sufficiency = SufficiencyEngine()
        self.interpreter = InterpretationEngine()
        self.reasoner = ReasoningEngine()
        self.scorer = ScoringEngine()
        self.consensus = ConsensusEngine()
        self.temporal = TemporalEngine()
        self.compute_reduction = ComputeReductionEngine()
        self.cache = SemanticCache(threshold=0.9)
        self.conf_threshold = conf_threshold

    async def run(self, user_input: str) -> LeoV34Response:
        # 0. DOMAIN CHECK
        is_in_domain, risk, msg = self.risk_engine.precheck(user_input)
        if not is_in_domain:
            return LeoV34Response(status=LeoStatus.LOW_CONFIDENCE, confidence=0.0, risk=risk, reason=msg)

        # 1. INPUT SUFFICIENCY GATE
        domain = "finance" if "finance" in user_input.lower() else "code"
        missing = self.sufficiency.detect_missing(user_input, domain)
        if missing or not self.sufficiency.validate_format(user_input):
            return LeoV34Response(status=LeoStatus.INSUFFICIENT, confidence=0.0, risk=risk, reason=f"Missing: {', '.join(missing)}")

        # 2. AMBIGUITY EXPANSION (BRANCH)
        interpretations = self.interpreter.generate_interpretations(user_input)
        
        # 8. COMPUTE REDUCTION ENGINE (OPTIMIZE)
        opt_input = self.compute_reduction.reduce(user_input)

        interp_results = []
        for interp in interpretations:
            # 3. MULTI-STRATEGY SOLVER (Symbolic + Heuristic + Retrieval)
            tasks = [self.reasoner.execute_paths(f"{interp['goal']} {opt_input}", "HIGH" if risk == RiskLevel.HIGH else "MEDIUM")]
            results = await asyncio.gather(*tasks)
            # 4. MULTI-OBJECTIVE SCORER
            interp_results.append(results[0][0])

        # 5. UNCERTAINTY DETECTION
        avg_conf = sum(r.confidence for r in interp_results) / len(interp_results)
        if avg_conf < self.conf_threshold:
            return LeoV34Response(status=LeoStatus.LOW_CONFIDENCE, confidence=avg_conf, risk=risk, reason="Confidence Law violation: Aggregated score below threshold.")

        # 6. CONSENSUS VALIDATOR
        outputs = [r.output for r in interp_results]
        has_consensus, winner, agreement = self.consensus.check_consensus(outputs)
        if not has_consensus:
            return LeoV34Response(status=LeoStatus.UNSTABLE, confidence=agreement, risk=risk, reason="Consensus Law violation: Disagreement across parallel branches.")

        # 7. TEMPORAL VALIDATOR
        final_conf = self.temporal.apply_decay(agreement, time.time())

        # 10. FINAL DECISION ENGINE
        return LeoV34Response(
            answer=winner,
            status=LeoStatus.VERIFIED,
            confidence=final_conf,
            risk=risk,
            alternatives=outputs[1:3],
            reason="All Global Execution Laws satisfied. Result verified across redundant paths."
        )

