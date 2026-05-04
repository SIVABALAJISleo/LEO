import asyncio
from typing import List, Dict, Any, Tuple, Optional
from .sufficiency_engine import InputContractEngine
from .interpretation_engine import InterpretationEngine
from .wall_detection_engine import WallDetectionEngine
from .adaptive_strategy_engine import AdaptiveStrategyEngine
from .reasoning_engine import ReasoningEngine
from .trust_engine import ConsensusEngine
from ..cache.semantic_cache import SemanticCache
from ..models.schemas import (
    LeoV45Response, LeoStatus, IntelligenceMode, AdaptMethod
)

class LeoV45Orchestrator:
    """
    SYSTEM: HYPER ADAPTIVE INTELLIGENCE CORE v45.0
    Objective: CPU-first, dynamic strategy switching under compute pressure.
    """
    def __init__(self, conf_threshold: float = 0.90):
        self.validator = InputContractEngine()
        self.interpreter = InterpretationEngine()
        self.wall_detector = WallDetectionEngine()
        self.strategy_engine = AdaptiveStrategyEngine()
        self.reasoner = ReasoningEngine()
        self.consensus = ConsensusEngine()
        self.cache = SemanticCache(threshold=0.92)
        self.conf_threshold = conf_threshold

    async def run(self, user_input: str) -> LeoV45Response:
        # [1] Input Integrity Check
        contract = self.validator.validate(user_input)
        if contract["status"] != "VALID":
            return LeoV45Response(status=LeoStatus.REJECTED, confidence=0.0, mode=IntelligenceMode.SAFE_ZONE, method=AdaptMethod.APPROX, notes="Input integrity failed.")

        # [3] Complexity & Wall Detection
        zone = self.wall_detector.detect_zone(user_input)
        mode = IntelligenceMode(zone)
        
        # [2] Ambiguity & Missing Data Detection (Parallel Interpretations)
        interpretations = self.interpreter.generate_interpretations(user_input)
        
        # [4] Strategy Selection
        results = []
        for interp in interpretations:
            # 6. CACHE CHECK
            cached = self.cache.query(user_input)
            if cached:
                results.append({"output": cached.code, "confidence": 1.0, "method": AdaptMethod.RAG})
                continue

            strategy = self.strategy_engine.select_strategy(zone, "GENERAL")
            method = AdaptMethod(strategy)
            
            # [5] Execution Engine
            if mode == IntelligenceMode.WALL_ZONE:
                # Controlled Degraded Execution (Reduced/Approx)
                result = f"ADAPTIVE_DEGRADED_RESULT({method.value}): Managed complexity zone."
                results.append({"output": result, "confidence": 0.88, "method": method})
            else:
                # Fast Optimized Execution
                success, out, conf = await self.reasoner.execute_paths(user_input, "MEDIUM")
                results.append({"output": out, "confidence": conf, "method": method})

        # [6] Validation & Consensus
        avg_conf = sum(r["confidence"] for r in results) / len(results)
        
        # [7] Confidence + Safety Gate
        if avg_conf < self.conf_threshold:
            return LeoV45Response(status=LeoStatus.PARTIAL, confidence=avg_conf, mode=mode, method=results[0]["method"])

        return LeoV45Response(
            answer=results[0]["output"],
            status=LeoStatus.VERIFIED,
            confidence=avg_conf,
            mode=mode,
            method=results[0]["method"]
        )
吐
