import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AuthorshipBoundary:
    """
    Module F: AUTHORSHIP BOUNDARY & SAFETY ENFORCER
    - System NEVER claims real-world truth.
    - World is explicitly declared synthetic.
    - Prevent misuse in scientific / safety-critical domains.
    - Contracts: M, N, R
    """
    
    def __init__(self):
        self._disclaimer = "NON_PHYSICAL_REALITY_SYNTHETIC_ONLY"
        self._identity = {
            "system_type": "Synthetic World Engine",
            "perception_mode": "Deterministic Perception System",
            "reality_status": "Non-Physical Reality"
        }

    def get_identity(self) -> Dict[str, str]:
        """Contract R: Final Identity Seal"""
        return self._identity

    def wrap_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inject metadata into every output.
        Contracts: M (Perception Only), N (Non-Claim)
        """
        data["_meta"] = {
            "type": "synthetic_author_defined",
            "safety_disclaimer": self._disclaimer,
            "verification_status": "unverified_for_real_world_use",
            "synthetic": True,
            "not_real_world": True,
            "simulation_fidelity": 0.0, # Explicitly zero to deny physics claims
            "predictive_validity": "none"
        }
        return data

    def validate_request(self, query: str) -> bool:
        """
        Filter out requests that might imply reliance on real-world accuracy.
        Contract N: Formal Non-Claim Enforcer
        """
        forbidden_topics = [
            "medical_diagnosis", 
            "structural_safety_calc", 
            "financial_advice",
            "weather_prediction",
            "trajectory_forecast",
            "clinical_trial"
        ]
        query_lower = query.lower()
        for topic in forbidden_topics:
            if topic in query_lower:
                logger.warning(f"Request blocked due to Authorship Boundary (Contract N): {topic}")
                return False
        return True
