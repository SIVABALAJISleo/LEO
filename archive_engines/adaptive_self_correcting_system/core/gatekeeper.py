from ..models.schemas import VerificationResult

class Gatekeeper:
    """
    12. OUTPUT GATE
    IF all_tests_pass AND mutation >= 0.9 AND invariants hold:
        return solution
    ELSE:
        continue or fail explicitly
    """
    def __init__(self, mutation_threshold: float = 0.9, coverage_threshold: float = 0.85):
        self.mutation_threshold = mutation_threshold
        self.coverage_threshold = coverage_threshold

    def verify_final(self, result: VerificationResult) -> bool:
        if not result.is_valid:
            return False
            
        return (
            result.test_pass_rate == 1.0 and
            result.mutation_score >= self.mutation_threshold and
            result.coverage >= self.coverage_threshold and
            result.type_check_passed and
            result.invariants_held
        )
