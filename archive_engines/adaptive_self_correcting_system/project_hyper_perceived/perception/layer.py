from .contracts import LeoPerceivedResponse, RiskLevel
from ..fallback.stack import fallback_stack

class PerceptionLayer:
    """
    MODULE 4 & 5 & 8: PERCEPTION & UX PROTECTION
    Transforms limitations into useful guidance.
    """
    def compose(self, prompt: str, confidence: float, risk: RiskLevel) -> LeoPerceivedResponse:
        # UX PROTECTION LOGIC
        if confidence > 0.8:
            return LeoPerceivedResponse(
                what_i_know=f"Full resolution for: {prompt}",
                best_possible_answer="Direct Answer: [SUCCESS]",
                confidence_score=confidence,
                next_steps=["Review results", "Execute next phase"],
                framing="Providing definitive results."
            )
        
        if confidence > 0.4:
            return LeoPerceivedResponse(
                what_i_know="Identified core objectives and primary constraints.",
                what_is_uncertain="Real-time drift parameters require verification.",
                best_possible_answer=fallback_stack.layer_1_refined(prompt),
                confidence_score=confidence,
                next_steps=["Refine input data", "Check secondary logic"],
                framing="Optimized response based on current data."
            )

        # CRITICAL / LOW CONFIDENCE PATH
        return LeoPerceivedResponse(
            what_i_know="The intent has been captured.",
            what_is_uncertain="Specific variables are currently outside standard confidence bounds.",
            best_possible_answer=fallback_stack.layer_3_partial(prompt),
            next_steps=["Simplify query", "Check system logs"],
            confidence_score=confidence,
            framing="Guiding you through the next logical steps."
        )

perception_layer = PerceptionLayer()

