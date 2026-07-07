import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConsistencyEnforcer:
    """
    Module C: PERCEPTION CONSISTENCY ENFORCER
    - Ensure generated visuals remain self-consistent.
    - Prevent contradictions across time and views.
    - Plausibility > realism, continuity > accuracy.
    """
    
    def __init__(self):
        # Ephemeral memory of what has been "established" as true in this session
        self._established_facts: Dict[str, Any] = {}
    
    def enforce(self, entity_id: str, proposed_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if proposed state contradicts established facts.
        If it does, OVERWRITE the proposal with the established fact.
        """
        if entity_id in self._established_facts:
            established = self._established_facts[entity_id]
            
            # Simple check: if color changed, revert it
            if "color" in established and proposed_state.get("color") != established["color"]:
                logger.warning(f"Consistency Violation for {entity_id}: Color changed. Reverting.")
                proposed_state["color"] = established["color"]
                proposed_state["consistency_note"] = "Enforced by prior observation"
                
            # If type changed, revert it
            if "type" in established and proposed_state.get("type") != established["type"]:
                logger.warning(f"Consistency Violation for {entity_id}: Type changed. Reverting.")
                proposed_state["type"] = established["type"]
                
        else:
            # First time seeing this, establish it as fact
            self._established_facts[entity_id] = proposed_state.copy()
            
        return proposed_state

    def reset_session(self):
        self._established_facts.clear()
