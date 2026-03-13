import asyncio
from typing import List, Callable, Dict, Any
from hyper_saas.backend.observability.telemetry import logger

class PrecomputationScheduler:
    """
    Schedules background jobs to pre-calculate high-probability results.
    Prevents spikes by smoothing out compute over time.
    """
    def __init__(self):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running = False

    async def schedule(self, task_id: str, coro_func: Callable, *args, **kwargs):
        """Add a compute task to the background queue."""
        await self.queue.put((task_id, coro_func, args, kwargs))
        logger.info(f"Scheduled precomputation: {task_id}")

    async def start(self):
        if self.running: return
        self.running = True
        while self.running:
            task_id, coro_func, args, kwargs = await self.queue.get()
            try:
                # low-priority background execution
                await asyncio.sleep(0.1) # Yield to main thread
                await coro_func(*args, **kwargs)
                logger.info(f"Precomputation complete: {task_id}")
            except Exception as e:
                logger.error(f"Precomputation failed: {task_id}", {"error": str(e)})
            finally:
                self.queue.task_done()

    def stop(self):
        self.running = False

scheduler = PrecomputationScheduler()
