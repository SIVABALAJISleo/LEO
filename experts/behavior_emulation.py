import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BehavioralEmulationLayer:
    """
    Replaces expensive physics/logic simulations with learned state transitions.
    Uses lookup tables and simple heuristics to emulate "likely" outcomes.
    """
    def __init__(self):
        # State transitions lookup: (current_state_key, action_key) -> next_state_proxy
        self.lookup_table = {}
        logger.info("BehavioralEmulationLayer initialized (Lookup-First)")

    def train_on_seed(self, seed_trajectories: List[Dict[str, Any]]):
        """
        Populate the lookup table from real high-fidelity simulation seeds.
        """
        for entry in seed_trajectories:
            key = (entry['state'], entry['action'])
            self.lookup_table[key] = entry['next_state']
        logger.info(f"Emulation trained with {len(self.lookup_table)} entries.")

    def predict_next_state(self, current_state: str, action: str) -> Any:
        """
        Returns the emulated next state.
        """
        key = (current_state, action)
        if key in self.lookup_table:
            logger.info(f"Emulation hit: {key}")
            return self.lookup_table[key]
        
        # Heuristic fallback if not in table
        logger.warning(f"Emulation miss for {key}. Using heuristic.")
        return f"heuristic_next_{current_state}_{action}"

if __name__ == "__main__":
    bel = BehavioralEmulationLayer()
    bel.train_on_seed([{"state": "idle", "action": "jump", "next_state": "mid_air"}])
    print(f"Prediction: {bel.predict_next_state('idle', 'jump')}")
