import logging
import time
from typing import Any, Dict

logger = logging.getLogger(__name__)

class ReconciliationEngine:
    """
    Safely merges optimistic UI predictions with backend ground truth.
    Prevents "state-jitter" during high-latency reconciliations.
    """
    def __init__(self, tolerance: float = 0.05):
        self.tolerance = tolerance # Allowed numerical difference before hard correction
        self.pending_reconciliations = {}

    def record_prediction(self, task_id: str, predicted_state: Any):
        """Logs what the client/UI thought would happen."""
        self.pending_reconciliations[task_id] = {
            "prediction": predicted_state,
            "timestamp": time.time()
        }
        logger.debug(f"Recorded optimistic prediction for {task_id}")

    def reconcile(self, task_id: str, actual_state: Any) -> Dict[str, Any]:
        """
        Compares prediction vs truth and determines the correction strategy.
        """
        pending = self.pending_reconciliations.pop(task_id, None)
        if not pending:
            return {"status": "synced", "correction": None, "actual": actual_state}

        prediction = pending["prediction"]
        
        # Comparison logic
        divergence = self._calculate_divergence(prediction, actual_state)
        
        if divergence <= self.tolerance:
            logger.info(f"Reconciliation successful for {task_id}. Divergence {divergence:.4f} within tolerance.")
            return {
                "status": "confirmed", 
                "divergence": divergence,
                "reconciled_state": actual_state # Small errors are absorbed
            }
        else:
            logger.warning(f"Reconciliation DIVERGENCE for {task_id}: {divergence:.4f} > {self.tolerance}")
            return {
                "status": "corrected",
                "divergence": divergence,
                "correction": actual_state, # Hard reset to truth
                "reason": "Divergence exceeded tolerance"
            }

    def _calculate_divergence(self, a: Any, b: Any) -> float:
        """Simple Euclidean/Scalar divergence."""
        try:
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                return abs(a - b) / max(abs(a), abs(b), 1)
            # Add more types (dict, list) as needed
            return 0.0 if a == b else 1.0
        except Exception:
            return 1.0

if __name__ == "__main__":
    reconciler = ReconciliationEngine(tolerance=0.1)
    
    # Test case: Good prediction
    reconciler.record_prediction("t1", 10.5)
    print(f"Result 1: {reconciler.reconcile('t1', 10.6)}")
    
    # Test case: Bad prediction
    reconciler.record_prediction("t2", 10.5)
    print(f"Result 2: {reconciler.reconcile('t2', 12.0)}")
