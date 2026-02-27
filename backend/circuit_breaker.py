import time
import requests
import structlog

logger = structlog.get_logger()

class CircuitBreaker:
    def __init__(self, name, failure_threshold=5, recovery_timeout=60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("circuit_half_open", name=self.name)
            else:
                raise Exception(f"Circuit {self.name} is OPEN")

        try:
            result = func(*args, **kwargs)
            self.success()
            return result
        except Exception as e:
            self.failure()
            raise e

    def success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error("circuit_opened", name=self.name)

# Usage example
# breaker = CircuitBreaker("external-api")
# breaker.call(requests.get, "http://api.example.com")
