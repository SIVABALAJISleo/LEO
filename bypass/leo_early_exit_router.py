import numpy as np
import logging
from sklearn.tree import DecisionTreeClassifier

logger = logging.getLogger(__name__)

class EarlyExitRouter:
    """
    Layer 2: The Early-Exit Router (Dynamic Compute).
    Intercepts execution after 10% depth. Uses a Scikit-Learn Decision Tree 
    to evaluate intermediate states. If confidence > 0.95, halts execution.
    """
    def __init__(self, threshold=0.95):
        self.threshold = threshold
        # Initialize a lightweight decision tree classifier
        self.clf = DecisionTreeClassifier(max_depth=3)
        self.is_trained = False
        
        # Simulate training the tree on dummy "intermediate" state data
        self._train_dummy_tree()

    def _train_dummy_tree(self):
        """Trains the decision tree on generic shapes to act as a fast logical gate."""
        # Generating fake intermediate hidden states (e.g., 256 dim)
        X_train = np.random.randn(100, 256)
        # Binary target: 1 = "easy example" (exit early), 0 = "hard example" (continue)
        y_train = np.random.randint(0, 2, 100)
        
        self.clf.fit(X_train, y_train)
        self.is_trained = True
        logger.debug("[EarlyExitRouter] Scikit-Learn Decision Tree initialized.")

    def evaluate_intermediate_state(self, hidden_tensor: np.ndarray):
        """
        Takes the tensor after the first 10% of the network.
        Evaluates it through the decision tree logic gate.
        Returns (True, predicted_output) if confidence is high enough.
        """
        # Reshape to avoid memory copy
        flat_tensor = hidden_tensor.reshape(-1)[:256].reshape(1, -1)
        if flat_tensor.shape[1] < 256:
            flat_tensor = np.pad(flat_tensor, ((0,0), (0, 256 - flat_tensor.shape[1])))

        # Predict probability of being an "easy" answer
        proba = self.clf.predict_proba(flat_tensor)[0]
        max_conf = np.max(proba)
        
        if max_conf >= self.threshold:
            logger.debug(f"[EarlyExitRouter] CONFIDENCE {max_conf:.2f} >= {self.threshold}. ABORTING NETWORK EXECUTION.")
            # We confidently extrapolate the final output (mocked here as the hidden state passed through a linear projection)
            extrapolated_output = hidden_tensor * 2.5 # Mock extrapolation math
            return True, extrapolated_output
            
        return False, None
