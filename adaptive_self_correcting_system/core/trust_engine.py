from typing import List, Any, Tuple

class ConsensusEngine:
    """
    4. CONSENSUS LAYER
    6. CONTRADICTION DETECTOR
    """
    def __init__(self):
        pass

    def check_consensus(self, outputs: List[Any]) -> Tuple[bool, Any, float]:
        if not outputs: return False, None, 0.0
        
        # Majority vote logic
        unique_outputs = list(set(outputs))
        counts = [outputs.count(o) for o in unique_outputs]
        max_count = max(counts)
        winner = unique_outputs[counts.index(max_count)]
        
        agreement_ratio = max_count / len(outputs)
        has_consensus = agreement_ratio >= 0.6 # Strict consensus threshold
        
        return has_consensus, winner, agreement_ratio

class TrustEngine:
    """
    5. DATA TRUST SCORING
    confidence = reliability * agreement * freshness
    """
    def calculate_trust(self, reliability: float, agreement: float, freshness: float) -> float:
        return reliability * agreement * freshness
吐
