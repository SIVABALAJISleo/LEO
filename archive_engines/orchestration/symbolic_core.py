import logging
from typing import Dict, Any, List, Callable, Optional

logger = logging.getLogger(__name__)

class SymbolicAICore:
    """
    Feature B: SYMBOLIC / LOGIC-FIRST AI CORE
    - detailed symbolic state representation
    - Event -> Rule -> Action pipeline
    - No backprop, no tensors.
    """
    
    def __init__(self):
        self.knowledge_graph: Dict[str, Any] = {}
        self.rules: List[Callable[[Dict[str, Any], Dict[str, Any]], Optional[str]]] = []

    def update_state(self, entity_id: str, attributes: Dict[str, Any]):
        """Update the symbolic knowledge graph."""
        if entity_id not in self.knowledge_graph:
            self.knowledge_graph[entity_id] = {}
        self.knowledge_graph[entity_id].update(attributes)

    def register_rule(self, rule_func: Callable[[Dict[str, Any], Dict[str, Any]], Optional[str]]):
        """Register a logical rule fn(event, state) -> action_id"""
        self.rules.append(rule_func)

    def process_event(self, event: Dict[str, Any]) -> List[str]:
        """
        Process a single discrete event through all logic rules.
        Returns a list of triggered actions.
        Latency is deterministic (O(NumRules)).
        """
        actions = []
        
        # 1. logical matching (CPU bounded)
        for rule in self.rules:
            action = rule(event, self.knowledge_graph)
            if action:
                actions.append(action)
                
        return actions

# Example Rule Definition Helpers
def create_proximity_rule(camera_id: str, threshold: float, action_name: str):
    """Factory for a simple symbolic rule."""
    def rule(event, state):
        if event.get("type") == "VISUAL_CHANGE" and event.get("camera_id") == camera_id:
            if event.get("magnitude", 0) > threshold:
                return action_name
        return None
    return rule
