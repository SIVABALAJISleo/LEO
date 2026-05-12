import asyncio
import logging
from typing import Callable, Awaitable, Any

logger = logging.getLogger(__name__)

class RequestQueue:
    def __init__(self, max_workers: int = 3, max_queue_size: int = 100):
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.max_workers = max_workers
        self.workers = []

    async def add(self, task_func: Callable[[], Awaitable[Any]], request_id: str):
        """Adds a task to the queue. Blocks if queue is full."""
        try:
            logger.debug(f"queue_add: id={request_id} current_size={self.queue.qsize()}")
            # Create a future to capture the result
            future = asyncio.get_event_loop().create_future()
            await self.queue.put((task_func, future))
            return await future
        except asyncio.QueueFull:
            logger.warning(f"queue_full: id={request_id}")
            raise Exception("Server is busy. Please try again later.")

    async def start(self):
        """Starts the worker pool."""
        logger.info(f"starting_request_queue_workers: count={self.max_workers}")
        self.workers = [asyncio.create_task(self._worker(i)) for i in range(self.max_workers)]

    async def _worker(self, worker_id: int):
        while True:
            task_func, future = await self.queue.get()
            try:
                logger.debug(f"worker_{worker_id}_processing_task")
                result = await task_func()
                if not future.done():
                    future.set_result(result)
            except Exception as e:
                logger.error(f"worker_{worker_id}_task_failed: {e}")
                if not future.done():
                    future.set_exception(e)
            finally:
                self.queue.task_done()

# Global instance
global_request_queue = RequestQueue()
