import logging
import numpy as np
from typing import Dict, Any, List

from .entropy_estimator import EntropyEstimator
from .divergence_analyzer import EmbeddingDivergenceAnalyzer
from .temporal_scorer import TemporalSimilarityScorer

logger = logging.getLogger("HyperCore.NoveltyEstimator")

class NoveltyEstimationEngine:
    """
    HyperCore MODULE 3 — Novelty Estimation Engine
    
    Estimates how much new information exists in an input.
    Combines:
    1. Entropy Estimation (Information density)
    2. Embedding Divergence (Semantic distance from context)
    3. Temporal Similarity (Time-decayed redundancy)
    
    Output: novelty score ∈ [0,1]
    
    Behavior / Routing Output:
    - low novelty (< 0.3) -> replay/retrieval
    - medium novelty (0.3 - 0.7) -> sparse execution
    - high novelty (> 0.7) -> dense execution
    """
    def __init__(self, low_threshold=0.3, high_threshold=0.7):
        self.entropy_estimator = EntropyEstimator()
        self.divergence_analyzer = EmbeddingDivergenceAnalyzer()
        self.temporal_scorer = TemporalSimilarityScorer(decay_halflife_seconds=3600.0)
        
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        
        self.entropy_history = []
        logger.info(f"NoveltyEstimationEngine initialized with thresholds: low={low_threshold}, high={high_threshold}")

    def estimate_novelty(self, text: str, input_embedding: np.ndarray, context_embeddings: List[np.ndarray], time_since_last_seen: float = float('inf')) -> Dict[str, Any]:
        """
        Calculates a combined novelty score and determines the recommended routing tier.
        """
        # 1. Entropy Score (Intrinsic novelty / density of the text itself)
        entropy_score = self.entropy_estimator.estimate(text)
        
        # 2. Divergence Score (Semantic novelty relative to context)
        divergence_score = self.divergence_analyzer.calculate_divergence(input_embedding, context_embeddings)
        
        # 3. Temporal Score (Decays similarity over time, boosting novelty if seen long ago)
        # Max similarity is 1.0 - divergence
        max_sim = 1.0 - divergence_score
        temporal_novelty = self.temporal_scorer.score(max_sim, time_since_last_seen)
        
        # Combine scores (weighted average)
        # We weigh divergence heavily because semantic difference is the strongest indicator of novelty.
        # Entropy acts as a modifier (highly dense text gets a slight bump).
        # Temporal novelty acts as a cap on redundancy.
        
        combined_score = (0.6 * divergence_score) + (0.2 * entropy_score) + (0.2 * temporal_novelty)
        novelty_score = float(np.clip(combined_score, 0.0, 1.0))
        
        # Update history
        self.entropy_history.append(novelty_score)
        if len(self.entropy_history) > 1000:
            self.entropy_history.pop(0)
            
        # Determine routing tier
        if novelty_score < self.low_threshold:
            routing_tier = "replay_retrieval"
            tier_desc = "Zero-Compute (Replay/Retrieval)"
        elif novelty_score < self.high_threshold:
            routing_tier = "sparse_execution"
            tier_desc = "Sparse Compute (MoE/Adaptive Depth)"
        else:
            routing_tier = "dense_execution"
            tier_desc = "Dense Compute (Full Engine)"
            
        result = {
            "novelty_score": round(novelty_score, 4),
            "routing_tier": routing_tier,
            "tier_description": tier_desc,
            "components": {
                "entropy": float(round(entropy_score, 4)),
                "divergence": float(round(divergence_score, 4)),
                "temporal": float(round(temporal_novelty, 4))
            }
        }
        
        logger.debug(f"Novelty Score: {novelty_score:.4f} -> Tier: {routing_tier}")
        return result
