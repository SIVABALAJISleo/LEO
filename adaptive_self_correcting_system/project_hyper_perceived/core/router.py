from .detector import limit_detector
from ..perception.layer import perception_layer
from ..schemas.contracts import QueryRequest, LeoPerceivedResponse

class LeoOrchestrator:
    """
    THE PERCEIVED 100% ENGINE
    Integrated pipeline: Detector -> Engine (Mock) -> Perception Layer
    """
    def execute(self, request: QueryRequest) -> LeoPerceivedResponse:
        # MODULE 1: DETECT LIMITS
        analysis = limit_detector.detect(request.prompt)
        
        # MODULE 2: PRIMARY ENGINE (Simplified for this version)
        # In a full system, this would be the model/RAG logic
        confidence = analysis["confidence_estimate"]
        risk = analysis["risk_level"]
        
        # MODULE 4, 5, 8: TRANSFORM INTO VALUE
        response = perception_layer.compose(request.prompt, confidence, risk)
        
        # MODULE 6: ALWAYS-HELP GUARANTEE
        # Ensured by LeoPerceivedResponse schema and PerceptionLayer logic
        return response

leo_orchestrator = LeoOrchestrator()
吐
