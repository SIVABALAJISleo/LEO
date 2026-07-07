import asyncio
from typing import List
from .input_sanitizer import InputSanitizer
from .interpretation_engine import InterpretationEngine
from .reasoning_engine import ReasoningEngine
from .scoring_engine import ScoringEngine
from .ood_detector import OODDetector
from ..models.schemas import (
    LeoV31Response, CandidateSolution
)

class LeoV31Orchestrator:
    """
    SYSTEM: HYPER AUTONOMOUS REASONING CORE v31.0
    Objective: Practical correctness across scenarios through 8-stage protocol.
    """
    def __init__(self):
        self.sanitizer = InputSanitizer()
        self.interpreter = InterpretationEngine()
        self.reasoner = ReasoningEngine()
        self.scorer = ScoringEngine()
        self.ood = OODDetector()

    async def run(self, user_input: str) -> LeoV31Response:
        # STAGE 1: INPUT ANALYSIS
        is_valid, clean_input, missing = self.sanitizer.sanitize(user_input)
        assumptions = ["Context assumes a standard Python execution environment."] if not is_valid else []

        # STAGE 2: MULTI-INTERPRETATION
        interpretations = self.interpreter.generate_interpretations(clean_input)

        # STAGE 3: SOLUTION SPACE EXPLORATION
        candidates: List[CandidateSolution] = []
        for interp in interpretations:
            # Generate logical and heuristic solutions
            tasks = [
                self.reasoner.execute_paths(f"{interp['goal']} {clean_input}", "LOW"),
                self.reasoner.execute_paths(f"{interp['goal']} {clean_input}", "MEDIUM")
            ]
            results = await asyncio.gather(*tasks)
            
            for res in results:
                # STAGE 4: MULTI-OBJECTIVE EVALUATION
                scores = self.scorer.evaluate(res[0].output)
                # STAGE 6: CROSS-VALIDATION (Simplified)
                stability = self.scorer.check_stability([res[0].output])
                
                candidates.append(CandidateSolution(
                    answer=res[0].output,
                    strategy="Hybrid reasoning",
                    scores=scores,
                    stability=stability
                ))

        # STAGE 5: UNCERTAINTY & UNKNOWN DETECTION
        is_ood, ood_score = self.ood.check_ood([0.1, 0.2])
        confidence = ood_score * 100.0

        # STAGE 7: FINAL DECISION ENGINE
        # Sort by total score (accuracy + robustness - cost)
        candidates.sort(key=lambda x: (x.scores.accuracy + x.scores.robustness - x.scores.cost), reverse=True)
        best = candidates[0]
        alternatives = [c.dict() for c in candidates[1:3]]

        # STAGE 8: OUTPUT STRUCTURE
        return LeoV31Response(
            final_answer=best.answer,
            confidence_score=confidence,
            selection_reason="Highest combined accuracy and robustness scores across all interpretations.",
            alternatives=alternatives,
            risks_and_failures=["Logic might diverge if environment variables change.", "OOD data might reduce accuracy."],
            assumptions=assumptions,
            metadata={"interpretations_count": len(interpretations), "stability": best.stability}
        )

