"""
phoenix/task_graph.py
Directed Acyclic Graph (DAG) Execution Engine.
Handles complex topological execution of parallel sub-tasks (retrieval, reasoning, etc).
"""

import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class TaskNode:
    def __init__(self, name: str, func: Callable, deps: List[str] = None):
        self.name = name
        self.func = func
        self.deps = deps or []
        self.result = None
        self.event = asyncio.Event()

class DAGExecutor:
    """
    Executes a graph of tasks asynchronously, respecting dependencies.
    """
    def __init__(self):
        self.nodes: Dict[str, TaskNode] = {}

    def add_node(self, name: str, func: Callable, deps: List[str] = None):
        self.nodes[name] = TaskNode(name, func, deps)

    async def _run_node(self, node: TaskNode, context: Dict[str, Any]):
        # Wait for all dependencies to complete
        for dep in node.deps:
            if dep in self.nodes:
                await self.nodes[dep].event.wait()
        
        try:
            # Pass context containing previous results if needed
            if asyncio.iscoroutinefunction(node.func):
                node.result = await node.func(context)
            else:
                node.result = node.func(context)
        except Exception as e:
            logger.error(f"[DAG] Error in node {node.name}: {e}")
            node.result = {"error": str(e)}
        finally:
            # Broadcast completion
            context[node.name] = node.result
            node.event.set()

    async def execute(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Runs the entire DAG."""
        context = initial_context or {}
        tasks = []
        for node in self.nodes.values():
            node.event.clear()
            node.result = None
            tasks.append(asyncio.create_task(self._run_node(node, context)))
            
        await asyncio.gather(*tasks)
        return context
