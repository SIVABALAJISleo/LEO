import json
from backend.vibethinker.ir.models import ReasoningGraph, ReasonNode

class IRParser:
    """
    Parses natural JSON plans from LLMs into the strongly-typed Reasoning IR (DAG).
    """
    @staticmethod
    def parse(json_str: str) -> ReasoningGraph:
        data = json.loads(json_str)
        nodes = []
        for i, step in enumerate(data.get("steps", [])):
            nodes.append(
                ReasonNode(
                    id=f"step_{i}",
                    action=step.get("action", "unknown"),
                    parameters=step.get("parameters", {}),
                    dependencies=[f"step_{j}" for j in range(i)] if i > 0 else []
                )
            )
            
        return ReasoningGraph(
            intent=data.get("goal", "unknown"),
            nodes=nodes,
            target_hardware="CPU"
        )
