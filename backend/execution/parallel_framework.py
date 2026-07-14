import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, List, Any

logger = logging.getLogger(__name__)

class ParallelExecutionFramework:
    """
    Subsystem 15: Parallel Execution Framework.
    Maximizes Core i5-12450H multithreading.
    Executes independent systems (Memory Search, Retrieval, Embeddings) concurrently.
    """
    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        
    async def _run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Wraps a synchronous blocking function in an asyncio future to run on a thread."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.thread_pool, lambda: func(*args, **kwargs))

    async def execute_concurrent_pipeline(self, query: str, 
                                          retrieval_func: Callable, 
                                          embedding_func: Callable,
                                          graph_search_func: Callable) -> dict:
        """
        Executes a 3-pronged parallel pipeline:
        1. Dense Vector Embeddings
        2. LSH / Keyword Retrieval
        3. Knowledge Graph Search
        All executing at the exact same time across different CPU threads.
        """
        logger.info(f"Dispatching concurrent execution pipeline for query: '{query}'")
        
        # Schedule tasks on the event loop
        t1 = self._run_in_thread(retrieval_func, query)
        t2 = self._run_in_thread(embedding_func, query)
        t3 = self._run_in_thread(graph_search_func, query)
        
        # Await all futures concurrently
        results = await asyncio.gather(t1, t2, t3, return_exceptions=True)
        
        # Collect Results
        payload = {
            "retrieval_results": results[0] if not isinstance(results[0], Exception) else [],
            "query_embedding": results[1] if not isinstance(results[1], Exception) else None,
            "graph_results": results[2] if not isinstance(results[2], Exception) else []
        }
        
        # Log failures
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Concurrent task {i} failed: {res}")
                
        return payload

    def shutdown(self):
        """Cleanly spin down threadpool."""
        self.thread_pool.shutdown(wait=True)
        logger.info("Parallel Execution Framework shutdown complete.")
