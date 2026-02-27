import time
import random
import logging
from typing import Callable, Any

logger = logging.getLogger("HYPER-Chaos")

class ChaosManager:
    def __init__(self):
        self.chaos_enabled = False
        self.latency_prob = 0.2
        self.error_prob = 0.05
        self.max_delay = 2.0 # seconds

    def toggle(self, state: bool):
        self.chaos_enabled = state
        logger.info(f"Chaos Mode focus: {'ENABLED' if state else 'DISABLED'}")

    def inject(self, func: Callable, *args, **kwargs) -> Any:
        if not self.chaos_enabled:
            return func(*args, **kwargs)

        # Inject Latency
        if random.random() < self.latency_prob:
            delay = random.uniform(0.5, self.max_delay)
            logger.info(f"Chaos: Injecting {delay:.2f}s latency into {func.__name__}")
            time.sleep(delay)

        # Inject Errors
        if random.random() < self.error_prob:
            logger.error(f"Chaos: Simulating failure in {func.__name__}")
            raise Exception(f"Simulated Expert Failure (Chaos Mode)")

        return func(*args, **kwargs)

chaos_manager = ChaosManager()
