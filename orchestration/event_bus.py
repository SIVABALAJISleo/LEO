import asyncio
import logging
from typing import Callable, List, Dict, Any

logger = logging.getLogger("HYPER-Events")

class EventBus:
    """
    Reactive Event Bus for decoupled, non-polling task execution.
    Reduces CPU usage by replacing loops with interrupts/events.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def emit(self, event_type: str, data: Any):
        logger.info(f"Event Emitted: {event_type}")
        if event_type in self.subscribers:
            tasks = [cb(data) if asyncio.iscoroutinefunction(cb) else asyncio.to_thread(cb, data) 
                     for cb in self.subscribers[event_type]]
            await asyncio.gather(*tasks)

if __name__ == "__main__":
    bus = EventBus()
    bus.subscribe("data_ready", lambda d: print(f"Processing: {d}"))
    asyncio.run(bus.emit("data_ready", {"id": 1}))
