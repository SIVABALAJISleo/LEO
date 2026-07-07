import numpy as np
import logging
from typing import Dict

logger = logging.getLogger("HyperCore.ContextualBandit")

class ThompsonSamplingRouter:
    """
    HyperCore INTELLIGENCE LAYER — Self-Building Value Function
    
    Implements a Contextual Multi-Armed Bandit using Thompson Sampling.
    It learns online from production traffic to select the optimal routing pathway:
    - Arm 0: Semantic Replay (Zero Compute)
    - Arm 1: Speculative Decoding (Low Compute)
    - Arm 2: Sparse MoE Routing (Medium Compute)
    - Arm 3: Exact Fallback (Dense Compute)
    
    Rewards combine: Latency reduction (higher is better) and Quality (higher is better).
    """
    def __init__(self, num_arms: int = 4):
        self.num_arms = num_arms
        # Beta distribution parameters for each arm (successes, failures)
        # We start with prior Beta(1, 1) for uniform exploration
        self.alpha = np.ones(num_arms, dtype=np.float32)
        self.beta = np.ones(num_arms, dtype=np.float32)
        
        self.arm_names = [
            "Semantic Replay",
            "Speculative Decoding",
            "Sparse MoE",
            "Exact Fallback"
        ]
        
    def select_pathway(self, context_vector: np.ndarray) -> int:
        """
        Selects the best pathway (arm) using Thompson Sampling.
        Context vector can modify the selection in advanced settings, but here
        we draw samples from Beta(alpha, beta) for each arm.
        """
        # Draw a sample from the Beta distribution for each arm
        samples = np.random.beta(self.alpha, self.beta)
        
        # In a contextual setup, we could weigh these samples based on context (e.g., complexity)
        # For simplicity, we choose the arm with the highest drawn probability sample
        chosen_arm = int(np.argmax(samples))
        
        logger.debug(f"Thompson Sampling drew: {samples} -> Selected Pathway: {self.arm_names[chosen_arm]}")
        return chosen_arm
        
    def update_feedback(self, arm: int, reward: float):
        """
        Updates the value function based on production outcome.
        reward: float ∈ [0, 1] (Combination of latency savings and semantic success)
        """
        # Thompson sampling updates Beta parameters
        # We model success as binary-like, or perform fractional updates
        self.alpha[arm] += reward
        self.beta[arm] += (1.0 - reward)
        
        logger.debug(f"Updated {self.arm_names[arm]} value function: Alpha={self.alpha[arm]:.2f}, Beta={self.beta[arm]:.2f}")
        
    def get_routing_probabilities(self) -> Dict[str, float]:
        """Returns the expected success probability of each arm."""
        expected_values = self.alpha / (self.alpha + self.beta)
        return {self.arm_names[i]: float(expected_values[i]) for i in range(self.num_arms)}
