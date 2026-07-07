"""
backend/optimization/batcher.py
Query Micro-Batching for Zero Runtime Compute.

Groups nearly simultaneous similar queries to avoid redundant processing.
"""
import asyncio
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class QueryBatcher:
    def __init__(self, window_ms: int = 20):
        self.window_ms = window_ms
        self.pending_queries: Dict[str, asyncio.Future] = {}

    async def get_batched_result(self, query: str, processor_func):
        """
        If a similar query is already being processed, wait for its result.
        Otherwise, start processing and allow others to join.
        """
        # Canonicalize slightly for matching
        key = query.strip().lower()
        
        if key in self.pending_queries:
            logger.info(f"batcher: Joining existing task for '{query}'")
            return await self.pending_queries[key]
            
        # Create a new future for others to await
        future = asyncio.Future()
        self.pending_queries[key] = future
        
        try:
            # Short window for others to join (optional, but 20ms is tiny)
            # await asyncio.sleep(self.window_ms / 1000.0)
            
            result = await processor_func(query)
            future.set_result(result)
            return result
        except Exception as e:
            future.set_exception(e)
            raise e
        finally:
            # Clean up after a short delay to allow late joiners
            await asyncio.sleep(0.1)
            if key in self.pending_queries:
                del self.pending_queries[key]

global_query_batcher = QueryBatcher()
