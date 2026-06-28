from backend.vibethinker.ir.models import ReasoningGraph, ReasonNode

class TreeSearchPlanner:
    """
    Layer 7: Planning Engine
    Uses heuristics and tree search to generate executable Reasoning IR.
    """
    def generate_plan(self, intent: str, query: str) -> ReasoningGraph:
        # Dummy planner output
        node1 = ReasonNode(
            id="step_1",
            action="retrieve",
            parameters={"query": query}
        )
        node2 = ReasonNode(
            id="step_2",
            action="execute_python",
            parameters={"code": "print('Analyzed: ' + data)"},
            dependencies=["step_1"]
        )
        
        return ReasoningGraph(
            intent=intent,
            nodes=[node1, node2],
            target_hardware="CPU"
        )
