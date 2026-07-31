import threading
import time
import logging
from typing import List

logger = logging.getLogger(__name__)

class PredictiveExecutionEngine:
    """
    Subsystem 3: Predictive Execution Engine.
    Executes in the background during idle system time.
    Pre-computes embeddings, pre-fetches documents into L3 cache, and builds search indexes.
    """
    def __init__(self, idle_threshold_sec: float = 5.0):
        self.idle_threshold = idle_threshold_sec
        self.last_activity_time = time.monotonic()
        self.running = False
        self.thread = None
        self.task_queue = []
        
    def record_activity(self):
        """Called by the orchestrator whenever a user request comes in."""
        self.last_activity_time = time.monotonic()
        
    def enqueue_background_task(self, task_name: str, task_func: callable, *args):
        """Adds a heavy indexing/embedding task to the idle queue."""
        self.task_queue.append((task_name, task_func, args))
        
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._idle_loop, daemon=True)
        self.thread.start()
        logger.info("Predictive Execution Engine started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def _idle_loop(self):
        """Continuously checks if the system is idle enough to execute background optimizations."""
        while self.running:
            time.sleep(1.0)
            
            # Check if system has been idle for the threshold
            if time.monotonic() - self.last_activity_time > self.idle_threshold:
                if self.task_queue:
                    # Pop the next background task
                    task_name, func, args = self.task_queue.pop(0)
                    logger.info(f"System idle. Executing background predictive task: {task_name}")
                    try:
                        func(*args)
                    except Exception as e:
                        logger.error(f"Predictive task {task_name} failed: {e}")
                    # Update activity time so we pause before the next heavy task
                    self.record_activity()
