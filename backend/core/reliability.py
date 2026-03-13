import asyncio
import time
from typing import Callable, Any, Dict, Optional
from backend.observability.telemetry import logger

class CircuitBreaker:
    """Prevents system collapse by stopping requests to failing services."""
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN
        self.last_failure_time = 0

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
            else:
                raise Exception("Circuit Breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"

class ReliabilityOrchestrator:
    """Manages fallback strategies and recovery logic."""
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.cb = circuit_breaker
        self.fallback_data = {}

    async def execute(self, action_name: str, func: Callable, *args, **kwargs):
        """Executes action with circuit breaking and fallback."""
        try:
            result = await self.cb.call(func, *args, **kwargs)
            # Store as Last Known Good (LKG)
            self.fallback_data[action_name] = result
            return result
        except Exception as e:
            logger.error(f"Action '{action_name}' failed. Falling back.", {"error": str(e)})
            return self._get_fallback(action_name)

    def _get_fallback(self, action_name: str) -> Any:
        """Returns LKG or a bounded estimation."""
        return self.fallback_data.get(action_name, "Fallback: Service Temporarily Unavailable")
