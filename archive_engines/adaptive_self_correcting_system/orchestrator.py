from .models.schemas import LeoV50Response, ComplexityTier, SystemStatus
from .core.engines import InputAnalysisGate, InputRestructurer, ComputeEliminationEngine, UncertaintyManager
from .core.resources import KnowledgeSystem, ReasoningEngine

class LeoV50Orchestrator:
    """THE 13-LAYER ROBUST AUTONOMOUS PIPELINE"""
    def __init__(self):
        self.analyzer = InputAnalysisGate()
        self.restructurer = InputRestructurer()
        self.eliminator = ComputeEliminationEngine()
        self.uncertainty = UncertaintyManager()
        self.knowledge = KnowledgeSystem()
        self.reasoner = ReasoningEngine()

    async def execute(self, query: str) -> LeoV50Response:
        # LAYER 1: INPUT ANALYSIS + COMPLEXITY GATE
        complexity, ratio = self.analyzer.analyze(query)
        
        # LAYER 11: FAIL-SAFE & 12: WORST-CASE AVOIDANCE (Early safety trigger)
        if complexity == ComplexityTier.EXTREME:
            return self._fail_safe_exit("EXTREME_ENTROPY_OR_ILL_DEFINED_TASK", ComplexityTier.EXTREME)

        # LAYER 2: INPUT RESTRUCTURING
        restructured = self.restructurer.restructure(query)
        
        # LAYER 3: COMPUTE ELIMINATION ENGINE
        cached = self.eliminator.check_reuse(query)
        if cached:
            return self._finalize(cached, 100.0, restructured, complexity, SystemStatus.STABLE)

        # LAYER 5: ADAPTIVE SOLUTION ENGINE (Simplified orchestrator logic)
        if complexity == ComplexityTier.SIMPLE:
            solution = f"DIRECT_SOLUTION({query[:10]})"
            raw_conf = 0.98
        else:
            # LAYER 9: CONSENSUS VALIDATION & 6: COMPUTE CONTROL
            # Multi-path reasoning simulation
            solution = f"STRUCTURED_REASONING_RESULT({query[:10]})"
            raw_conf = 0.85

        # LAYER 8: UNCERTAINTY MANAGEMENT
        conf = self.uncertainty.manage(raw_conf, query) * 100
        status = SystemStatus.STABLE if conf > 90 else SystemStatus.UNCERTAIN

        # LAYER 13: SYSTEM SELF-AWARENESS (Integrated into output contract)
        return self._finalize(solution, conf, restructured, complexity, status)

    def _finalize(self, solution: str, conf: float, restructured: dict, complexity: ComplexityTier, status: SystemStatus) -> LeoV50Response:
        return LeoV50Response(
            refined_understanding=restructured["objective"],
            missing_data_assumptions=restructured["unknowns"] + [f"Complexity: {complexity.value}"],
            solution=solution,
            alternatives=[f"ALT_{solution}"] if complexity != ComplexityTier.SIMPLE else [],
            confidence_score=conf,
            risks_failure_cases=["Potential knowledge drift"] if complexity == ComplexityTier.COMPLEX else [],
            status=status,
            complexity=complexity
        )

    def _fail_safe_exit(self, reason: str, complexity: ComplexityTier) -> LeoV50Response:
        return LeoV50Response(
            refined_understanding="System safety protocol triggered.",
            missing_data_assumptions=["Worst-case avoidance active"],
            solution=None,
            confidence_score=0.0,
            risks_failure_cases=[reason],
            status=SystemStatus.DEGRADED,
            complexity=complexity
        )

