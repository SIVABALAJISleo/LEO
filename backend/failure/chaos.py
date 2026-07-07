import random

class ChaosEngine:
    """Injects simulated failures to test system resilience."""
    def __init__(self, failure_probability: float = 0.0):
        self.failure_probability = failure_probability

    def trigger(self):
        """Randomly raises an exception based on probability."""
        if random.random() < self.failure_probability: # nosec B311
            raise Exception("Simulated Chaos Failure")

class IdempotencyManager:
    """Ensures same request doesn't trigger side effects twice."""
    def __init__(self):
        self.processed_requests = set()

    def check_and_track(self, request_id: str) -> bool:
        if request_id in self.processed_requests:
            return False # Already processed
        self.processed_requests.add(request_id)
        return True
