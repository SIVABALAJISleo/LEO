from hyper_optimized_ai.app.core.gate import InputGate
from hyper_optimized_ai.app.core.router import Router, ZeroComputeLayer, ComputePath
from hyper_optimized_ai.app.core.filter import RealityFilter
from hyper_optimized_ai.app.core.output import OutputControl, AdaptiveResponse
from hyper_optimized_ai.app.core.safety import SafetyRules, FeedbackLoop
from hyper_optimized_ai.app.services.vector_db import VectorDBService
from hyper_optimized_ai.app.models.manager import ModelManager
from hyper_optimized_ai.config import settings
import logging

logger = logging.getLogger(__name__)

class HyperEngine:
    def __init__(self):
        self.vector_db = VectorDBService(settings.FAISS_INDEX_PATH)
        self.gate = InputGate()
        self.router = Router()
        self.zero_compute = ZeroComputeLayer(self.vector_db)
        self.reality_filter = RealityFilter(self.vector_db)
        self.output_control = OutputControl()
        self.safety = SafetyRules()
        self.feedback = FeedbackLoop(self.vector_db)
        self.models = ModelManager()

    async def process(self, text: str, is_high_risk: bool = False):
        # 1. INPUT GATE (AMBIGUITY ELIMINATION)
        gate_response = await self.gate.process_input(text, is_high_risk)
        if gate_response.action != "proceed":
            yield self.output_control.format_response(
                content=gate_response.message or "Clarification needed.",
                confidence=gate_response.top_confidence,
                needs_clarification=True,
                interpretations=[i.intent for i in gate_response.interpretations]
            ).model_dump_json()
            return

        top_interpretation = gate_response.interpretations[0]

        # 4. ZERO-COMPUTE LAYER (Check Cache)
        # PRIMARY WEAPON: Similarity > 0.92 -> reuse
        cached_result = await self.zero_compute.check_cache(text)
        if cached_result:
            logger.info("ZERO-COMPUTE: Cache hit.")
            yield self.output_control.format_response(cached_result, 1.0).model_dump_json()
            return

        # Try template (also zero compute)
        templated = self.zero_compute.try_template(top_interpretation.intent, top_interpretation.constraints)
        if templated:
            logger.info("ZERO-COMPUTE: Template match.")
            yield self.output_control.format_response(templated, 0.95).model_dump_json()
            return

        # 3. SMART ROUTER (MINIMAL COMPUTE)
        compute_path = self.router.classify_complexity(text, top_interpretation.intent)
        logger.info(f"ROUTING: {compute_path}")

        # 2. REALITY + CONFIDENCE ENGINE (No-Guess)
        validation = await self.reality_filter.validate_execution(
            top_interpretation.intent, 
            text
        )
        
        if not validation["valid"]:
            # 7. SAFETY: No silent failure, no fake certainty
            yield self.output_control.format_response(
                content=f"BLOCKED: {validation['reason']}. Missing: {', '.join(validation.get('missing_data', []))}",
                confidence=validation["confidence"]
            ).model_dump_json()
            return

        # 5. SPEED LAYER (Execution)
        full_result = ""
        if compute_path == ComputePath.TINY:
            full_result = await self.models.run_tiny(text)
            yield self.output_control.format_response(
                content=full_result,
                confidence=validation["confidence"]
            ).model_dump_json()
        elif compute_path == ComputePath.QUANTIZED:
            # Streaming response
            async for token in self.models.run_quantized(text):
                full_result += token
                yield token
        else:
            full_result = "Executing high-complexity task via optional API path..."
            yield self.output_control.format_response(
                content=full_result,
                confidence=validation["confidence"]
            ).model_dump_json()

        # 4. LAZY COMPUTE (Store in cache for next time)
        if validation["confidence"] >= settings.ADAPTIVE_OUTPUT_HIGH_THRESHOLD:
            await self.vector_db.add_to_cache(text, full_result)
