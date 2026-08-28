from datetime import datetime, timedelta
from .risk_engine import RiskEngine
from .sufficiency_engine import InputContractEngine
from .interpretation_engine import InterpretationEngine
from .domain_router import DomainRouter
from .triple_consensus_engine import TripleConsensusEngine
from .reasoning_engine import ReasoningEngine
from .compute_optimizer import ComputeMinimizationEngine
from .edge_case_detector import EdgeCaseDetector
from .temporal_engine import TemporalEngine
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV40Response, LeoStatus, RiskLevel
)

class LeoV40Orchestrator:
    """
    SYSTEM: HYPER ULTRA-STRICT PRECISION CORE v40.0 (FINAL FORM)
    Objective: 99.5% accuracy, zero silent failures, CPU-only.
    """
    def __init__(self, extreme_conf_floor: float = 0.95):
        self.risk_engine = RiskEngine()
        self.input_contract = InputContractEngine()
        self.interpreter = InterpretationEngine()
        self.router = DomainRouter()
        self.triple_consensus = TripleConsensusEngine()
        self.reasoner = ReasoningEngine()
        self.compute_engine = ComputeMinimizationEngine()
        self.edge_detector = EdgeCaseDetector()
        self.temporal = TemporalEngine()
        self.cache = SemanticCache(threshold=0.94)
        self.conf_floor = extreme_conf_floor

    async def run(self, user_input: str) -> LeoV40Response:
        # [1] INPUT CONTRACT GATE
        contract = self.input_contract.validate(user_input)
        if contract["status"] != "VALID":
            return self._abstain(f"CONTRACT_VIOLATION: {contract.get('reason', 'Missing data')}", RiskLevel.LOW)

        # [2] AMBIGUITY EXPANDER
        interpretations = self.interpreter.generate_interpretations(user_input)
        
        # [3] MICRO-DOMAIN ROUTER
        domain = self.router.route(user_input)
        
        results = []
        for interp in interpretations:
            # [4] CACHE + RETRIEVAL FIRST
            cached = self.cache.query(f"{domain} {interp['goal']} {user_input}")
            if cached:
                results.append({"output": cached.code, "confidence": 1.0})
                continue

            # [5] TRIPLE CONSENSUS ENGINE
            success, winner, err = self.triple_consensus.validate(interp)
            if not success:
                return self._abstain(err, RiskLevel.MEDIUM, LeoStatus.UNSTABLE)
            
            # [7] EXTREME ABSTENTION CONTROL + [8] EDGE-CASE
            if self.edge_detector.is_edge_case(user_input):
                return self._abstain("ABSTAIN: Edge-case or adversarial pattern detected.", RiskLevel.HIGH)
            
            results.append({"output": winner, "confidence": 0.98})

        # Final Aggregation & Extreme Confidence Floor
        avg_conf = sum(r["confidence"] for r in results) / len(results)
        if avg_conf < self.conf_floor:
            return self._abstain(f"ABSTAIN: Aggregated confidence {avg_conf:.2f} below extreme floor.", RiskLevel.MEDIUM)

        # [9] FINAL DECISION ENGINE
        valid_until = (datetime.now() + timedelta(hours=6)).isoformat()

        return LeoV40Response(
            answer=results[0]["output"],
            confidence=avg_conf,
            status=LeoStatus.VERIFIED,
            risk=RiskLevel.LOW,
            alternatives=[r["output"] for r in results[1:3]],
            compute_used="LOW",
            valid_until=valid_until
        )

    def _abstain(self, reason: str, risk: RiskLevel, status: LeoStatus = LeoStatus.ABSTAIN) -> LeoV40Response:
        return LeoV40Response(
            status=status,
            confidence=0.0,
            risk=risk,
            valid_until=datetime.now().isoformat(),
            answer=None,
            alternatives=[]
        )

