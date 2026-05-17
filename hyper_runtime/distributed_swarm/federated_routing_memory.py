import logging
from typing import Dict, Any

logger = logging.getLogger("HyperCore.FederatedRoutingMemory")

class FederatedRoutingMemory:
    """
    HyperCore Distributed Layer — Federated Collective Exploration
    
    Shares exploration outcomes across nodes so that if Node A discovers
    that a query can be safely routed to Sparse MoE, Node B instantly inherits
    that routing confidence without spending shadow traffic to explore it again.
    """
    def __init__(self):
        # Maps query semantic cluster to optimal routing path
        self.global_routing_table: Dict[str, Dict[str, Any]] = {}
        
    def apply_delta(self, delta: Dict[str, Any]):
        """
        Applies a routing update broadcasted from a peer node over the coherence bus.
        """
        if delta["topic"] == "route_discovery":
            cluster_id = delta["delta"]["cluster_id"]
            best_route = delta["delta"]["best_route"]
            confidence = delta["delta"]["confidence"]
            
            # CRDT Last-Writer-Wins / Max Confidence merge
            if cluster_id not in self.global_routing_table or confidence > self.global_routing_table[cluster_id].get("confidence", 0):
                self.global_routing_table[cluster_id] = {
                    "best_route": best_route,
                    "confidence": confidence,
                    "discovered_by": delta["node_id"]
                }
                logger.info(f"Updated global routing for {cluster_id[:8]} -> {best_route} (Conf: {confidence:.2f})")
                
    def get_route(self, cluster_id: str) -> str:
        if cluster_id in self.global_routing_table:
            return self.global_routing_table[cluster_id]["best_route"]
        return "UNKNOWN"
