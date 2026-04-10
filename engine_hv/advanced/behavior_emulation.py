import logging
import json
import os
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

class BehavioralEmulationLayer:
    """
    Replaces expensive physical or logical simulations with 
    learned state transitions, heuristics, and lookup tables.
    
    Core Principle: "Outcome over Accuracy" - If the state transition 
    feels correct to the observer, the expensive math is skipped.
    """
    def __init__(self, data_path: Optional[str] = None):
        self.state_db: Dict[str, Any] = {}
        self.heuristics: List[Callable[[Dict], Optional[Dict]]] = []
        if data_path and os.path.exists(data_path):
            self._load_transitions(data_path)

    def _load_transitions(self, path: str):
        try:
            with open(path, 'r') as f:
                self.state_db = json.load(f)
            logger.info(f"Loaded {len(self.state_db)} behavioral transitions.")
        except Exception as e:
            logger.error(f"Failed to load behavioral data: {e}")

    def add_heuristic(self, rule_func: Callable[[Dict], Optional[Dict]]):
        """Adds a logical rule to predict the next state without simulation."""
        self.heuristics.append(rule_func)

    def predict_next_state(self, current_state: Dict[str, Any], action: str) -> Dict[str, Any]:
        """
        Main entry point for emulating a state change.
        """
        # 1. Try Heuristics First (Fastest)
        for rule in self.heuristics:
            prediction = rule(current_state)
            if prediction:
                logger.debug(f"Behavioral Emulation: Heuristic hit for action '{action}'")
                return prediction

        # 2. Try Lookup Table (Moderate)
        state_key = f"{current_state.get('id')}:{action}"
        if state_key in self.state_db:
            logger.debug(f"Behavioral Emulation: Lookup hit for key '{state_key}'")
            return self.state_db[state_key]

        # 3. Fallback: Interpolation or Default
        logger.warning(f"No emulation data for action '{action}'. Using default fallback.")
        return {**current_state, "status": "transitioned", "last_action": action}

if __name__ == "__main__":
    def gravity_rule(state):
        if state.get("type") == "falling":
            return {**state, "y": state.get("y", 0) - 9.8}
        return None

    emuser = BehavioralEmulationLayer()
    emuser.add_heuristic(gravity_rule)
    
    initial = {"id": "obj1", "type": "falling", "y": 100}
    next_s = emuser.predict_next_state(initial, "step")
    print(f"Emulated State: {next_s}")
