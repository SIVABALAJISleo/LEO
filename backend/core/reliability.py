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
    """
    Manages fallback strategies and recovery logic.
    Supports 'Dynamic Graceful Degradation' using rule-based templates.
    """
    def __init__(self, circuit_breaker: CircuitBreaker):
        self.cb = circuit_breaker
        self.lkg_data = {} # Last Known Good
        self.rules = {
            "definition": "Information about {entity} is currently being updated. Please try again in 30 seconds.",
            "comparison": "The comparison between {entity} elements is temporarily unavailable.",
            "default": "Service is under heavy load. Returning cached/simplified result."
        }

    async def execute(self, action_name: str, func: Callable, query_metadata: Dict[str, Any], *args, **kwargs):
        """Executes action with circuit breaking and rule-based fallback."""
        try:
            result = await self.cb.call(func, *args, **kwargs)
            self.lkg_data[action_name] = result
            return result
        except Exception as e:
            logger.error(f"reliability_event: action={action_name} error={e}")
            return self._get_dynamic_fallback(action_name, query_metadata)

    def _get_dynamic_fallback(self, action_name: str, kwargs: dict) -> dict:
        # Tier 1: Last Known Good (if < 5 minutes old)
        lkg = self.lkg_data.get(action_name)
        if lkg:
            import time
            age = time.time() - lkg.get("timestamp", 0) # Handle potential missing timestamp
            if age < 300:
                result = lkg.copy() if isinstance(lkg, dict) else {"result": lkg}
                result["_fallback"] = "lkg"
                return result

        # Tier 2: Rule-based answer
        query = kwargs.get("query", "") or kwargs.get("question", "")
        if query:
            return {
                "answer": f"System is under high load. Your question '{query[:50]}...' has been queued.",
                "source": "RULE_BASED_FALLBACK",
                "confidence": 0.3,
                "_fallback": "rule_based",
            }

        # Tier 3: Structured error (never a bare string)
        return {
            "answer": "Service temporarily unavailable. Please retry in 30 seconds.",
            "source": "SYSTEM_FALLBACK",
            "confidence": 0.0,
            "_fallback": "system",
            "retry_after": 30,
        }
