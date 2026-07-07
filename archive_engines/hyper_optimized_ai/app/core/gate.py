from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from archive_engines.hyper_optimized_ai.config import settings

class Interpretation(BaseModel):
    intent: str
    constraints: Dict[str, Any] = {}
    missing_info: List[str] = []
    confidence: float

class InputGateResponse(BaseModel):
    interpretations: List[Interpretation]
    top_confidence: float
    action: str # "proceed", "clarify", "force_structured"
    message: Optional[str] = None

class InputGate:
    """
    1. INPUT GATE (AMBIGUITY ELIMINATION)
    - Extract {intent, constraints, missing}
    - Generate top 3 interpretations
    - If confidence < 0.8 -> ask 1 clarification
    - For high-risk -> force structured input (no free text)
    """
    
    async def process_input(self, text: str, is_high_risk: bool = False) -> InputGateResponse:
        # High-risk detection logic
        high_risk_keywords = ["delete", "format", "reinstall", "overwrite", "critical"]
        if is_high_risk or any(k in text.lower() for k in high_risk_keywords):
            return InputGateResponse(
                interpretations=[],
                top_confidence=0.0,
                action="force_structured",
                message="High-risk action detected. Please confirm via structured command palette."
            )
        
        # Intent Extraction (Simulated for CPU-first efficiency)
        # In production, this would call a tiny ONNX model (e.g. BERT-tiny)
        interpretations = self._extract_intent(text)
        
        top_confidence = max(i.confidence for i in interpretations) if interpretations else 0.0
        
        if top_confidence < settings.INPUT_GATE_CONFIDENCE_THRESHOLD:
            return InputGateResponse(
                interpretations=interpretations,
                top_confidence=top_confidence,
                action="clarify",
                message=f"I'm only {top_confidence:.0%} sure of your intent. Did you mean '{interpretations[0].intent}'?" if interpretations else "I couldn't understand the intent. Please rephrase."
            )
            
        return InputGateResponse(
            interpretations=interpretations[:3],
            top_confidence=top_confidence,
            action="proceed"
        )

    def _extract_intent(self, text: str) -> List[Interpretation]:
        # Simple rule-based extraction for zero-compute demo
        text_lower = text.lower()
        results = []
        
        if "nvidia" in text_lower or "gpu" in text_lower:
            results.append(Interpretation(intent="hardware_optimize", constraints={"target": "NVIDIA"}, confidence=0.88))
        if "cache" in text_lower or "compute" in text_lower:
            results.append(Interpretation(intent="system_config", constraints={"parameter": "compute_mode"}, confidence=0.82))
        if "code" in text_lower or "write" in text_lower:
            results.append(Interpretation(intent="code_gen", confidence=0.75))
            
        # Fallback interpretation
        results.append(Interpretation(intent="general_query", confidence=0.5))
        
        return sorted(results, key=lambda x: x.confidence, reverse=True)
