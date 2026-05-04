from typing import Optional, List
from ..models.schemas import Solution, VerificationResult

class BestSolution(Solution):
    score: float 
    status: str  # e.g. "PARTIALLY_VERIFIED", "FULLY_VERIFIED"
    verification: VerificationResult

class AnytimeManager:
    """
    10. ANYTIME LOGIC
    - always keep best working solution
    - improve progressively
    - return best verified if stopped early
    """
    def __init__(self):
        self.leaderboard: List[BestSolution] = []

    def update(self, solution: Solution, verification: VerificationResult):
        # Calculate a weighted score
        score = (
            verification.test_pass_rate * 0.4 +
            verification.coverage * 0.3 +
            verification.mutation_score * 0.2 +
            (1.0 if verification.type_check_passed else 0.0) * 0.1
        )
        
        status = "FULLY_VERIFIED" if verification.is_valid else "PARTIALLY_VERIFIED"
        
        new_sol = BestSolution(
            code=solution.code,
            explanation=solution.explanation,
            iteration=solution.iteration,
            proposer_id=solution.proposer_id,
            score=score,
            status=status,
            verification=verification
        )
        
        self.leaderboard.append(new_sol)
        # Keep sorted by score, then iteration (lower is better for same score)
        self.leaderboard.sort(key=lambda x: (x.score, -x.iteration), reverse=True)

    def get_best(self) -> Optional[BestSolution]:
        return self.leaderboard[0] if self.leaderboard else None

    def is_perfect(self) -> bool:
        best = self.get_best()
        return best.verification.is_valid if best else False
