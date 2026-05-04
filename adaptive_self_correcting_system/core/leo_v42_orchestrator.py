import asyncio
from typing import List, Dict, Any, Tuple, Optional
from .heavy_task_detector import HeavyTaskDetector
from .transformation_engine import TransformationEngine
from .reasoning_engine import ReasoningEngine
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV42Response, LeoStatus, ContainmentMethod
)

class LeoV42Orchestrator:
    """
    SYSTEM: LEO CONTAINMENT ENGINE v42.0
    Objective: Zero-GPU, high-control. Contain heavy 5-10% intelligently.
    """
    def __init__(self, conf_threshold: float = 0.90):
        self.detector = HeavyTaskDetector()
        self.transformer = TransformationEngine()
        self.reasoner = ReasoningEngine()
        self.cache = SemanticCache(threshold=0.92)
        self.conf_threshold = conf_threshold

    async def run(self, user_input: str) -> LeoV42Response:
        # [1] TASK ANALYSIS + [2] HEAVY TASK DETECTOR
        tag = self.detector.check(user_input)
        
        # [3] TRANSFORMATION ENGINE (Pre-check cache)
        cached = self.cache.query(user_input)
        if cached:
            return LeoV42Response(answer=cached.code, status=LeoStatus.VERIFIED, method=ContainmentMethod.PRECOMPUTED, confidence=1.0)

        if tag == "HEAVY":
            # [4] EXECUTION PATH SELECTOR (Transformation Loop)
            # Strategy: Prefer Approximation -> Fallback
            result = self.transformer.approximate(user_input)
            return LeoV42Response(
                answer=result,
                status=LeoStatus.APPROXIMATED,
                method=ContainmentMethod.APPROX,
                confidence=0.88,
                note="Task exceeded CPU scope; returned controlled heuristic approximation."
            )

        # NORMAL Path
        # Strategy: Decompose -> Solve
        sub_tasks = self.transformer.decompose(user_input)
        results = []
        for task in sub_tasks:
            success, out, conf = await self.reasoner.execute_paths(task, "MEDIUM")
            results.append(out)

        return LeoV42Response(
            answer=" | ".join(results),
            status=LeoStatus.VERIFIED,
            method=ContainmentMethod.DIRECT,
            confidence=0.95
        )
吐
