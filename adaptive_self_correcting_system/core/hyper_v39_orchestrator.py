import asyncio
from typing import List, Dict, Any, Tuple, Optional
from .reframing_engine import ReframingEngine
from .small_model_engine import SmallModelEngine
from .reasoning_engine import ReasoningEngine
from .trust_engine import ConsensusEngine
from .ood_detector import OODDetector
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV39Response, LeoStatus, ComputeMethod
)

class LeoV39Orchestrator:
    """
    SYSTEM: HYPER ZERO-GPU CORE v39.0
    Objective: 100% CPU-feasible limits. Zero GPU operations.
    """
    def __init__(self, conf_threshold: float = 0.90):
        self.reframer = ReframingEngine()
        self.small_model = SmallModelEngine()
        self.reasoner = ReasoningEngine()
        self.consensus = ConsensusEngine()
        self.ood = OODDetector()
        self.cache = SemanticCache(threshold=0.92)
        self.conf_threshold = conf_threshold

    async def run(self, user_input: str) -> LeoV39Response:
        # 1️⃣ SCOPE RESTRICTION ENGINE
        if "matrix" in user_input.lower() or "video" in user_input.lower() or "train model" in user_input.lower():
            return LeoV39Response(status=LeoStatus.REJECTED, method=ComputeMethod.RETRIEVAL, confidence=0.0, reason="OUT_OF_CPU_SCOPE: Task requires GPU-scale matrix or video compute.")

        # 6️⃣ CACHE + REUSE LAYER (Mandatory)
        cached = self.cache.query(user_input)
        if cached:
            return LeoV39Response(answer=cached.code, status=LeoStatus.VERIFIED, method=ComputeMethod.CACHE, confidence=1.0, reason="Retrieved from Zero-GPU semantic cache.")

        # 2️⃣ TASK CLASSIFIER + 3️⃣ REFRAME / SIMPLIFY
        complexity = self.small_model.estimate_complexity(user_input)
        if complexity == "HEAVY":
            # Mandatory Reframing for heavy tasks
            task_state = self.reframer.reframe(user_input)
            method = ComputeMethod.RETRIEVAL
        else:
            task_state = {"task": "DIRECT_SOLVE", "original": user_input}
            method = ComputeMethod.SMALL_MODEL

        # 4️⃣ RETRIEVAL-FIRST / 5️⃣ SMALL-MODEL EXECUTION
        # (Using small model for all allowed CPU tasks)
        result, conf = self.small_model.execute(task_state)

        # 7️⃣ VALIDATION ENGINE
        if conf < self.conf_threshold:
            return LeoV39Response(status=LeoStatus.ABSTAIN, method=method, confidence=conf, reason="Low confidence in CPU-bound reasoning outcome.")

        return LeoV39Response(
            answer=result,
            status=LeoStatus.VERIFIED,
            confidence=conf,
            method=method,
            reason=f"Resolved using CPU-optimized {method.value} path."
        )
吐
