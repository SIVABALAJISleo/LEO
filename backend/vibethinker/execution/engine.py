import abc
import asyncio
import logging
from typing import Dict, Any, List

from backend.vibethinker.ir.models import ReasoningGraph
from backend.vibethinker.execution.validator import GraphValidator, GraphValidationError
from backend.vibethinker.execution.registry import ActionRegistry

logger = logging.getLogger(__name__)

class ExecutionEngine(abc.ABC):
    """
    Base class for the VibeThinker Execution Engine.
    Executes a ReasoningGraph DAG, coordinating tools, Python sandboxes, and verification.
    """
    
    @abc.abstractmethod
    async def execute(self, graph: ReasoningGraph) -> Dict[str, Any]:
        """
        Executes the reasoning graph asynchronously and returns the final execution state or result.
        """
        pass

class LocalSandboxEngine(ExecutionEngine):
    """
    Executes reasoning IR strictly on local CPU/iGPU environments asynchronously.
    """
    async def execute(self, graph: ReasoningGraph) -> Dict[str, Any]:
        logger.info(f"Starting execution of graph. Intent: {graph.intent}")
        
        # 1. Validate the graph and sort topologically
        GraphValidator.validate(graph)
        execution_tiers = GraphValidator.topological_sort(graph)
        
        # 2. Context maintains outputs of all executed nodes mapping node_id -> output
        context: Dict[str, Any] = {}
        
        # Create a lookup for nodes by ID
        node_map = {node.id: node for node in graph.nodes}
        
        # 3. Execute tier by tier (tiers are sequential, nodes within a tier are concurrent)
        for tier_idx, tier in enumerate(execution_tiers):
            logger.debug(f"Executing Tier {tier_idx + 1}/{len(execution_tiers)}: {tier}")
            
            # Prepare concurrent tasks for this tier
            tasks = []
            for node_id in tier:
                node = node_map[node_id]
                handler = ActionRegistry.get_handler(node.action)
                
                # Gather upstream dependency results to pass into this node's context
                node_context = {dep_id: context[dep_id] for dep_id in node.dependencies if dep_id in context}
                
                # Create coroutine
                coro = self._execute_node(node.id, handler, node.parameters, node_context)
                tasks.append(coro)
                
            # Run all nodes in the current tier concurrently
            tier_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and update context
            for node_id, result in zip(tier, tier_results):
                if isinstance(result, Exception):
                    logger.error(f"Execution failed at node {node_id}: {str(result)}")
                    # If one node fails, we can choose to fail the whole graph or handle it.
                    # For now, fail the whole execution to maintain strict determinism.
                    raise RuntimeError(f"Node {node_id} failed: {str(result)}") from result
                    
                context[node_id] = result
                
        logger.info("Graph execution completed successfully.")
        return {"status": "success", "context": context}
        
    async def _execute_node(
        self, 
        node_id: str, 
        handler: Any, 
        parameters: Dict[str, Any], 
        node_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Helper to execute a single node and log its progress.
        """
        logger.debug(f"Executing node {node_id}...")
        result = await handler(parameters, node_context)
        logger.debug(f"Node {node_id} completed.")
        return result
