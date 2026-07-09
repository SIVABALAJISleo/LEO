import logging
from typing import List, Dict, Any
from collections import Counter

class ByzantineConsensus:
    def __init__(self, threshold: float = 2/3):
        self.logger = logging.getLogger("ByzantineConsensus")
        self.threshold = threshold
        self.quarantined_nodes = set()
        self.voting_history = {}
        
    def reach_consensus(self, proposals: List[Dict[str, Any]]) -> dict:
        """
        Applies a mathematically provable threshold consensus.
        proposals: list of dicts like {"node_id": "n1", "answer_hash": "abc12"}
        """
        total_votes = len(proposals)
        if total_votes == 0:
            return {"status": "failed", "reason": "No proposals"}
            
        # Group proposals by answer
        answers = [p["answer_hash"] for p in proposals if p["node_id"] not in self.quarantined_nodes]
        if not answers:
            return {"status": "failed", "reason": "All nodes quarantined"}
            
        counts = Counter(answers)
        best_answer, max_votes = counts.most_common(1)[0]
        
        ratio = max_votes / len(answers)
        
        if ratio >= self.threshold:
            self.logger.info(f"Consensus reached on {best_answer} ({ratio*100:.1f}% majority)")
            
            # Penalize dissenting nodes
            dissenters = [p["node_id"] for p in proposals if p["answer_hash"] != best_answer]
            self._update_voting_history(dissenters)
            
            return {
                "status": "consensus_reached",
                "accepted_answer": best_answer,
                "confidence": ratio,
                "dissenting_nodes": len(dissenters)
            }
        else:
            self.logger.warning(f"Consensus failed. Max majority was {ratio*100:.1f}%.")
            return {
                "status": "consensus_failed",
                "confidence": ratio
            }
            
    def _update_voting_history(self, dissenters: List[str]):
        """
        Tracks malicious or consistently hallucinating nodes.
        """
        for node in dissenters:
            self.voting_history[node] = self.voting_history.get(node, 0) + 1
            if self.voting_history[node] > 5:
                self.quarantined_nodes.add(node)
                self.logger.error(f"[QUARANTINE] Node {node} exceeded dissent threshold.")
                
    def get_quarantined_nodes(self) -> List[str]:
        return list(self.quarantined_nodes)
