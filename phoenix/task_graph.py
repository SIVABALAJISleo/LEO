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
            # Anomaly bypass check
            # For this paradigm, we use a simple hash of context to represent state
            current_state_hash = str(hash(frozenset([(k, str(v)) for k, v in context.items()])))
            bypass = False
            
            # Simulated anomaly driven bypass check
            if hasattr(self, 'anomaly_processor') and node.name in getattr(self, 'anomaly_processor_states', {}):
                if getattr(self, 'anomaly_processor_states')[node.name] == current_state_hash:
                    bypass = True
            
            if bypass:
                logger.debug(f"[DAG] Anomaly Bypass: Skipping {node.name} (zero compute)")
                node.result = getattr(self, 'anomaly_processor_results')[node.name]
            else:
                # Pass context containing previous results if needed
                if asyncio.iscoroutinefunction(node.func):
                    node.result = await node.func(context)
                else:
                    node.result = node.func(context)
                    
                # Store state and result for future bypass
                if not hasattr(self, 'anomaly_processor_states'):
                    setattr(self, 'anomaly_processor_states', {})
                    setattr(self, 'anomaly_processor_results', {})
                getattr(self, 'anomaly_processor_states')[node.name] = current_state_hash
                getattr(self, 'anomaly_processor_results')[node.name] = node.result
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
