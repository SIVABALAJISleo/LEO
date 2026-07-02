from typing import List, Dict, Set
from backend.vibethinker.ir.models import ReasoningGraph

class GraphValidationError(Exception):
    """Exception raised for errors in the validation of a ReasoningGraph DAG."""
    pass

class GraphValidator:
    """
    Validates a ReasoningGraph to ensure it is a valid Directed Acyclic Graph (DAG)
    and that all node dependencies resolve correctly.
    """
    
    @staticmethod
    def validate(graph: ReasoningGraph) -> None:
        """
        Validates the graph for missing dependencies and cycles.
        Raises GraphValidationError if validation fails.
        """
        node_ids = {node.id for node in graph.nodes}
        
        # 1. Check for missing dependencies
        for node in graph.nodes:
            for dep in node.dependencies:
                if dep not in node_ids:
                    raise GraphValidationError(f"Node '{node.id}' depends on non-existent node '{dep}'.")
                    
        # 2. Check for cycles using DFS
        # 0 = unvisited, 1 = visiting, 2 = visited
        visited: Dict[str, int] = {node_id: 0 for node_id in node_ids}
        adj_list = {node.id: node.dependencies for node in graph.nodes}
        
        def has_cycle(node_id: str) -> bool:
            if visited[node_id] == 1:
                return True # Cycle detected
            if visited[node_id] == 2:
                return False
                
            visited[node_id] = 1
            for neighbor in adj_list[node_id]:
                if has_cycle(neighbor):
                    return True
            visited[node_id] = 2
            return False

        for node_id in node_ids:
            if visited[node_id] == 0:
                if has_cycle(node_id):
                    raise GraphValidationError("Cyclic dependency detected in the reasoning graph.")
                    
    @staticmethod
    def topological_sort(graph: ReasoningGraph) -> List[List[str]]:
        """
        Sorts the graph topologically into execution tiers.
        Each tier contains a list of node IDs that can be executed concurrently.
        Assumes the graph has been validated and contains no cycles.
        """
        # Create a mapping of node to its dependencies and dependents
        in_degree = {node.id: 0 for node in graph.nodes}
        dependents = {node.id: [] for node in graph.nodes}
        
        for node in graph.nodes:
            in_degree[node.id] = len(node.dependencies)
            for dep in node.dependencies:
                dependents[dep].append(node.id)
                
        # Nodes with 0 in-degree can be executed immediately
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        
        tiers = []
        
        while queue:
            tiers.append(queue)
            next_queue = []
            for node_id in queue:
                for dependent in dependents[node_id]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)
            queue = next_queue
            
        return tiers
