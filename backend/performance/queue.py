import asyncio
import time
from typing import Callable

class BatchProcessor:
    """Processes requests in batches to reduce CPU context switching."""
    def __init__(self, batch_size: int = 5, timeout_ms: int = 100):
        self.queue = []
        self.batch_size = batch_size
        self.timeout_ms = timeout_ms

    async def add_task(self, task: Callable, *args):
        self.queue.append((task, args))
        if len(self.queue) >= self.batch_size:
            return await self.flush()

    async def flush(self):
        results = []
        current_batch = self.queue[:]
        self.queue = []
        for task, args in current_batch:
            results.append(await task(*args))
        return results

class AdaptiveRateLimiter:
    """Slowing down requests based on system load (Mocked)."""
    def __init__(self, max_rps: int = 10):
        self.max_rps = max_rps
        self.request_timestamps = []

    async def wait_if_needed(self):
        now = time.time()
        self.request_timestamps = [t for t in self.request_timestamps if now - t < 1.0]
        
        if len(self.request_timestamps) >= self.max_rps:
            wait_time = 1.0 - (now - self.request_timestamps[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.request_timestamps.append(time.time())
