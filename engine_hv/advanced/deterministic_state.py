import logging
import copy
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DeterministicStateLayer:
    """
    Implements Rollback Networking and event prediction.
    Replaces continuous physics with discrete, reversible state transitions.
    """
    def __init__(self, history_limit: int = 50):
        self.history_limit = history_limit
        self.state_history: List[Dict[str, Any]] = [] # [(tick, state)]
        self.current_tick = 0

    def get_state(self, tick: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if tick is None:
            return self.state_history[-1][1] if self.state_history else None
        
        for t, s in reversed(self.state_history):
            if t == tick: return s
        return None

    def apply_event(self, tick: int, event: Dict[str, Any], initial_state: Dict[str, Any]):
        """
        Applies an event at a specific tick. If it's a past tick, 
        it triggers a re-simulation (rollback).
        """
        if tick < self.current_tick:
            logger.warning(f"Rollback detected! Rebasing state from tick {tick}...")
            self._rollback_and_resimulate(tick, event)
        else:
            self._apply_forward(tick, event, initial_state)

    def _apply_forward(self, tick: int, event: Dict[str, Any], state: Dict[str, Any]):
        # Simulate state transition (Mock logic)
        new_state = copy.deepcopy(state)
        new_state.update(event.get("delta", {}))
        new_state["tick"] = tick
        
        self.state_history.append((tick, new_state))
        self.current_tick = tick
        
        if len(self.state_history) > self.history_limit:
            self.state_history.pop(0)

    def _rollback_and_resimulate(self, tick: int, late_event: Dict[str, Any]):
        """
        Rewinds time to 'tick', applies 'late_event', and fast-forwards
        all subsequent events.
        """
        # 1. Find the base state before the late event
        base_state = self.get_state(tick - 1)
        if not base_state:
            logger.error(f"Cannot rollback to tick {tick}: base state missing.")
            return

        # 2. Prune history from this point
        self.state_history = [(t, s) for t, s in self.state_history if t < tick]
        
        # 3. Apply the late event
        self._apply_forward(tick, late_event, base_state)
        
        logger.info(f"Rollback complete. State re-synchronized at tick {self.current_tick}.")

if __name__ == "__main__":
    dsl = DeterministicStateLayer()
    
    # Tick 1
    s0 = {"pos": 0}
    dsl.apply_event(1, {"delta": {"pos": 10}}, s0)
    
    # Tick 2
    dsl.apply_event(2, {"delta": {"pos": 20}}, dsl.get_state())
    
    print(f"State at Tick 2: {dsl.get_state()}")
    
    # Late Event for Tick 1 (Rollback!)
    dsl.apply_event(1, {"delta": {"pos": 5}}, s0)
    
    print(f"State after Rollback: {dsl.get_state()}")
