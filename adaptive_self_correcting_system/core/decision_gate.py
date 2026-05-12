from dataclasses import dataclass, field
from typing import List, Optional, Any
from ..models.schemas import LeoV29Response, SystemStatus, RiskLevel, VerificationResult

@dataclass
class SystemState:
    ood_detected: bool = False
    ambiguity_high: bool = False
    missing_information: bool = False
    knowledge_out_of_scope: bool = False
    model_disagreement: bool = False
    low_confidence: bool = False
    verification_failed: bool = False
    meta_uncertainty_high: bool = False
    system_unstable: bool = False
    result: Any = None
    confidence: float = 0.0
    risk: str = "LOW"
    error_msg: str = ""

class DecisionCore:
    """
    NON-NEGOTIABLE SYSTEM CONTRACT
    """
    def decision_gate(self, state: SystemState) -> LeoV29Response:
        if (
            state.ood_detected
            or state.ambiguity_high
            or state.missing_information
            or state.knowledge_out_of_scope
            or state.model_disagreement
            or state.low_confidence
            or state.verification_failed
            or state.meta_uncertainty_high
            or state.system_unstable
        ):
            return self.safe_exit(state)

        return LeoV29Response(
            answer=state.result,
            status=SystemStatus.VERIFIED,
            confidence=state.confidence,
            risk=RiskLevel.LOW if state.risk == "LOW" else RiskLevel.HIGH,
            verification=VerificationResult.PASSED
        )

    def safe_exit(self, state: SystemState) -> LeoV29Response:
        notes = state.error_msg
        if state.ambiguity_high:
            return LeoV29Response(status=SystemStatus.AMBIGUOUS, confidence=0.0, risk=RiskLevel.LOW, verification=VerificationResult.FAILED, notes=f"CLARIFY_INTENT: {notes}")
        if state.missing_information:
            return LeoV29Response(status=SystemStatus.ABSTAINED, confidence=0.0, risk=RiskLevel.LOW, verification=VerificationResult.FAILED, notes=f"REQUEST_REQUIRED_INPUT: {notes}")
        if state.knowledge_out_of_scope:
            return LeoV29Response(status=SystemStatus.UNKNOWN, confidence=0.0, risk=RiskLevel.LOW, verification=VerificationResult.FAILED, notes=f"ABSTAIN_UNKNOWN_DOMAIN: {notes}")
        if state.verification_failed:
            return LeoV29Response(status=SystemStatus.ABSTAINED, confidence=0.5, risk=RiskLevel.MEDIUM, verification=VerificationResult.BOUNDED, notes=f"OUTPUT_WITH_BOUND_CERTIFICATE: {notes}")
        
        return LeoV29Response(status=SystemStatus.ABSTAINED, confidence=0.0, risk=RiskLevel.LOW, verification=VerificationResult.FAILED, notes=f"ABSTAIN_GENERIC: {notes}")

