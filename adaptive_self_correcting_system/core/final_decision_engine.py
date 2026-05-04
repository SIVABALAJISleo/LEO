from dataclasses import dataclass
from typing import Optional, Any
from ..models.schemas import LeoV30Response, SystemStatus, RiskLevel, VerificationResult

@dataclass
class PipelineState:
    ambiguity: bool = False
    missing_info: bool = False
    ood_detected: bool = False
    knowledge_gap: bool = False
    disagreement: bool = False
    low_confidence: bool = False
    verification_failed: bool = False
    meta_uncertainty: bool = False
    system_instability: bool = False
    result: Any = None
    confidence: float = 0.0
    risk: str = "low"
    explanation: str = ""

class FinalDecisionEngine:
    """
    ABSOLUTE SYSTEM CONTRACT: output_contract(state)
    """
    def output_contract(self, state: PipelineState) -> LeoV30Response:
        # ABSOLUTE SYSTEM CONTRACT
        if (
            state.ambiguity
            or state.missing_info
            or state.ood_detected
            or state.knowledge_gap
            or state.disagreement
            or state.low_confidence
            or state.verification_failed
            or state.meta_uncertainty
            or state.system_instability
        ):
            return self.safe_response(state)
        
        return self.verified_response(state)

    def safe_response(self, state: PipelineState) -> LeoV30Response:
        status = SystemStatus.ABSTAINED
        next_action = "retry"
        
        if state.ambiguity:
            status = SystemStatus.AMBIGUOUS
            next_action = "clarify"
        elif state.missing_info:
            status = SystemStatus.ABSTAINED
            next_action = "clarify"
        elif state.ood_detected or state.knowledge_gap:
            status = SystemStatus.UNKNOWN
            next_action = "retry"
        elif state.verification_failed:
            status = SystemStatus.ABSTAINED
            next_action = "accept" if state.result else "clarify"
            
        return LeoV30Response(
            answer=state.result,
            status=status,
            confidence=state.confidence,
            risk=RiskLevel.LOW if state.risk == "low" else RiskLevel.HIGH,
            verification=VerificationResult.FAILED if not state.verification_failed else VerificationResult.BOUNDED,
            explanation=state.explanation,
            next_action=next_action
        )

    def verified_response(self, state: PipelineState) -> LeoV30Response:
        return LeoV30Response(
            answer=state.result,
            status=SystemStatus.VERIFIED,
            confidence=state.confidence,
            risk=RiskLevel.LOW if state.risk == "low" else RiskLevel.HIGH,
            verification=VerificationResult.PASSED,
            explanation="System output verified across all layers.",
            next_action="accept"
        )
吐
