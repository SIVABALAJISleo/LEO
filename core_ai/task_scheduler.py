"""
core_ai/task_scheduler.py
High-Performance Work-Stealing Thread Scheduler for LEO AI v∞.
Features dynamic core affinity mapping, decentralized queues, and work-stealing heuristics.
"""

import time
import os
import psutil
import threading
import logging
from collections import deque
from typing import Callable, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class Task:
    """Wrapper encapsulating a functional compute unit (callable)."""
    def __init__(self, func: Callable[..., Any], *args: Any, **kwargs: Any):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result: Optional[Any] = None
        self.exception: Optional[Exception] = None
        self._done_event = threading.Event()

    def execute(self) -> None:
        try:
            self.result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.exception = e
            logger.error(f"[Task] Execution failed: {e}")
        finally:
            self._done_event.set()

    def wait(self) -> Any:
        self._done_event.wait()
        if self.exception:
            raise self.exception
        return self.result


class WorkStealingWorker(threading.Thread):
    def __init__(self, worker_id: int, parent_scheduler: 'WorkStealingScheduler', core_id: Optional[int] = None):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.scheduler = parent_scheduler
        self.queue = deque()
        self.lock = threading.Lock()
        self.core_id = core_id
        self.running = True

    def run(self) -> None:
        # Set core affinity if specified
        if self.core_id is not None:
            try:
                proc = psutil.Process()
                # Bind thread's process/thread affinity to specific core
                proc.cpu_affinity([self.core_id])
                logger.info(f"[Worker-{self.worker_id}] Bound CPU affinity to core {self.core_id}")
            except Exception as e:
                logger.warning(f"[Worker-{self.worker_id}] Failed setting core affinity: {e}")

        while self.running:
            task = self.pop_task()
            if task:
                task.execute()
                continue

            # Queue empty: try to steal from other workers
            task = self.steal_task()
            if task:
                task.execute()
                continue

            # Nothing to do: yield execution
            time.sleep(0.001)

    def push_task(self, task: Task) -> None:
        """Push task to own queue (LIFO for cache locality)."""
        with self.lock:
            self.queue.append(task)

    def pop_task(self) -> Optional[Task]:
        """Pop task from own queue (LIFO for cache locality)."""
        with self.lock:
            if self.queue:
                return self.queue.pop()
        return None

    def steal_task(self) -> Optional[Task]:
        """Steal a task from another worker's queue (FIFO to reduce contention)."""
        num_workers = len(self.scheduler.workers)
        if num_workers <= 1:
            return None
            
        # Select target worker round-robin or randomly
        start_idx = (self.worker_id + 1) % num_workers
        for i in range(num_workers - 1):
            target_idx = (start_idx + i) % num_workers
            if target_idx == self.worker_id:
                continue
                
            target_worker = self.scheduler.workers[target_idx]
            if len(target_worker.queue) > 0:
                with target_worker.lock:
                    if target_worker.queue:
                        # FIFO steal from bottom of target queue
                        stolen = target_worker.queue.popleft()
                        logger.debug(f"[Worker-{self.worker_id}] Stole task from Worker-{target_worker.worker_id}")
                        return stolen
        return None


class WorkStealingScheduler:
    """Decentralized work-stealing scheduler mapping execution tasks to CPU physical cores."""
    def __init__(self, num_threads: Optional[int] = None):
        self.num_threads = num_threads or os.cpu_count() or 4
        self.workers: List[WorkStealingWorker] = []
        self.next_worker_idx = 0
        
        # Detect physical core count to bind thread affinities
        total_cores = psutil.cpu_count(logical=False) or self.num_threads
        for i in range(self.num_threads):
            core_affinity = i % total_cores
            w = WorkStealingWorker(worker_id=i, parent_scheduler=self, core_id=core_affinity)
            self.workers.append(w)
            w.start()

    def submit(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Task:
        """Submit a task to the scheduler distribution queues."""
        task = Task(func, *args, **kwargs)
        
        # Round-robin dispatch to worker queues
        w = self.workers[self.next_worker_idx]
        self.next_worker_idx = (self.next_worker_idx + 1) % self.num_threads
        w.push_task(task)
        return task

    def map(self, func: Callable[[Any], Any], iterable: list) -> List[Any]:
        """Parallel map equivalent."""
        tasks = [self.submit(func, item) for item in iterable]
        return [task.wait() for task in tasks]

    def shutdown(self) -> None:
        """Terminate all worker threads."""
        for w in self.workers:
            w.running = False
        for w in self.workers:
            w.join(timeout=1.0)
