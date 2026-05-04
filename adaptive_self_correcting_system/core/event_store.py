import time
from typing import List, Dict, Any

class EventStore:
    """
    7. EVENT SOURCING
    - Rebuild truth from event logs
    - Maintain versioned history
    """
    def __init__(self):
        self.events: List[Dict[str, Any]] = []

    def commit_event(self, event_type: str, data: Dict[str, Any]):
        event = {
            "version": len(self.events) + 1,
            "timestamp": time.time(),
            "type": event_type,
            "data": data
        }
        self.events.append(event)

    def get_state(self) -> Dict[str, Any]:
        # Rebuild state from scratch
        state = {}
        for event in self.events:
            state.update(event["data"])
        return state
吐
