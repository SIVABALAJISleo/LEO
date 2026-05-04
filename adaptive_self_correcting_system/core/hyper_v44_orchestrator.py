import asyncio
from typing import List, Dict, Any, Tuple, Optional
from .redefinition_engine import RedefinitionEngine
from .strategy_selector import StrategySelector
from .complexity_engine import ComplexityEngine
from .reasoning_engine import ReasoningEngine
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV44Response, LeoStatus, RedefineMethod
)

class LeoV44Orchestrator:
    """
    SYSTEM: HYPER GPU-MINIMIZATION CORE v44.0
    Objective: CPU-first performance through problem redefinition.
    """
    def __init__(self, conf_threshold: float = 0.90):
        self.redefiner = RedefinitionEngine()
        self.selector = StrategySelector()
        self.complexity_engine = ComplexityEngine()
        self.reasoner = ReasoningEngine()
        self.cache = SemanticCache(threshold=0.92)
        self.conf_threshold = conf_threshold

    async def run(self, user_input: str) -> LeoV44Response:
        # [1] INPUT ANALYSIS
        if len(user_input) < 1:
            return LeoV44Response(status=LeoStatus.REJECTED, confidence=0.0, method=RedefineMethod.APPROX, note="Input null.")

        # [2] COMPLEXITY DETECTION
        complexity = self.complexity_engine.estimate(user_input)
        
        # [6] CACHE CHECK (Intelligent Caching)
        cached = self.cache.query(user_input)
        if cached:
            return LeoV44Response(answer=cached.code, status=LeoStatus.VERIFIED, method=RedefineMethod.CACHE, confidence=1.0)

        # [3] PROBLEM REDEFINITION ENGINE
        redist = self.redefiner.redefine(user_input)
        strategy = self.selector.select(redist["task"])
        
        # [5] COMPUTE OPTIMIZATION (Using small CPU models)
        if complexity == "HIGH":
            # 9. GPU-DOMINANT TASK HANDLER
            # Redefinition is mandatory for GPU_CLASS
            result = f"REDEFINED_OUTPUT({redist['strategy']}): {redist['reason']}"
            return LeoV44Response(
                answer=result,
                status=LeoStatus.APPROXIMATED,
                method=RedefineMethod(redist["strategy"]),
                confidence=0.89,
                note=f"Task required {complexity} compute; redefined as CPU-solvable."
            )

        # [10] VALIDATION ENGINE (NORMAL Path)
        success, winner, conf = await self.reasoner.execute_paths(user_input, "MEDIUM")
        
        if conf < self.conf_threshold:
            return LeoV44Response(status=LeoStatus.REJECTED, confidence=conf, method=RedefineMethod.APPROX, note="Confidence floor violated.")

        return LeoV44Response(
            answer=winner,
            status=LeoStatus.VERIFIED,
            confidence=conf,
            method=RedefineMethod.RETRIEVAL
        )

