import logging
import copy
from typing import Dict, Any

logger = logging.getLogger(__name__)

class StatePredictor:
    """
    Predict-then-correct model for replacing expensive physics.
    Uses discrete state transitions and simple interpolation.
    """
    def __init__(self):
        self.last_known_state: Dict[str, Any] = {}

    def predict_next(self, current: Dict[str, Any], delta_time: float) -> Dict[str, Any]:
        """
        Extrapolates state based on simple heuristics (e.g. constant velocity).
        """
        prediction = copy.deepcopy(current)
        velocity = current.get("velocity", [0, 0, 0])
        pos = current.get("position", [0, 0, 0])
        
        # Simple linear prediction
        prediction["position"] = [
            pos[0] + velocity[0] * delta_time,
            pos[1] + velocity[1] * delta_time,
            pos[2] + velocity[2] * delta_time
        ]
        
        logger.debug(f"State Predicted: {prediction['position']}")
        return prediction

    def reconcile(self, predicted: Dict[str, Any], actual: Dict[str, Any], lerp_factor: float = 0.5) -> Dict[str, Any]:
        """
        Blends predicted state with actual ground truth from backend.
        """
        logger.info("Reconciling prediction with ground truth.")
        # Simple LERP for smooth correction
        reconciled = copy.deepcopy(actual)
        p_pos = predicted.get("position", [0, 0, 0])
        a_pos = actual.get("position", [0, 0, 0])
        
        reconciled["position"] = [
            p_pos[i] + (a_pos[i] - p_pos[i]) * lerp_factor for i in range(3)
        ]
        return reconciled
