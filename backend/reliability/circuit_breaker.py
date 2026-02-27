import time
import logging
from enum import Enum
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed" # Normal operation
    OPEN = "open" # Service failing, bypassing calls
    HALF_OPEN = "half_open" # Attempting recovery

class CircuitBreaker:
    """
    Prevents cascading failures by stopping calls to a failing service.
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info("Circuit Breaker: Entering HALF_OPEN state...")
                self.state = CircuitState.HALF_OPEN
            else:
                logger.warning("Circuit Breaker is OPEN. Bypassing call.")
                raise RuntimeError("Service temporarily unavailable (Circuit Open)")

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            if self.state == CircuitState.HALF_OPEN:
                logger.info("Circuit Breaker: Success in HALF_OPEN. CLOSING circuit.")
                self._reset()
            return result
        
        except Exception as e:
            self._handle_failure()
            raise e

    def _handle_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            logger.error(f"Circuit Breaker: Failure threshold {self.failure_threshold} reached. OPENING circuit.")
            self.state = CircuitState.OPEN

    def _reset(self):
        self.failures = 0
        self.state = CircuitState.CLOSED

if __name__ == "__main__":
    import asyncio
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
    
    async def fail(): raise ValueError("Crash")
    async def ok(): return "Success"

    async def test():
        try: await cb.call(fail)
        except: pass
        try: await cb.call(fail)
        except: pass # Should trigger open
        
        try: await cb.call(ok)
        except Exception as e: print(f"Expected failure: {e}")
        
        time.sleep(1.1)
        print(f"Post-timeout: {await cb.call(ok)}")

    asyncio.run(test())
