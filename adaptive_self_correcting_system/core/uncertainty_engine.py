from ..models.schemas import UncertaintyLevel, RecommendedAction
from typing import Tuple

class UncertaintyEngine:
    """
    5) UNCERTAINTY ESTIMATION
    7) DECISION CONTROL (CRITICAL)
    """
    def __init__(self):
        pass

    def estimate(self, confidence: float, conflict: bool, meta_u: bool) -> Tuple[UncertaintyLevel, str, RecommendedAction]:
        # 7) DECISION CONTROL Mapping
        if confidence >= 0.95 and not conflict and not meta_u:
            level = UncertaintyLevel.LOW
            reason = "High consensus and verified reasoning."
            action = RecommendedAction.PROCEED
        elif confidence >= 0.85:
            level = UncertaintyLevel.MEDIUM
            reason = "Moderate confidence; some minor variance detected."
            action = RecommendedAction.PROCEED_WITH_WARNING
        elif confidence >= 0.6:
            level = UncertaintyLevel.MEDIUM
            reason = "Significant uncertainty or conflict detected. Validation required."
            action = RecommendedAction.REQUIRE_VALIDATION
        else:
            level = UncertaintyLevel.HIGH
            reason = "Low confidence or meta-uncertainty detected. Unsafe to proceed."
            action = RecommendedAction.BLOCK_AND_ESCALATE
            
        return level, reason, action
吐
