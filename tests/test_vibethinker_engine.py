import pytest
import asyncio
from backend.vibethinker.ir.models import ReasoningGraph, ReasonNode
from backend.vibethinker.execution.validator import GraphValidator, GraphValidationError
from backend.vibethinker.execution.engine import LocalSandboxEngine

def test_graph_validator_missing_dependency():
    nodes = [
        ReasonNode(id="step_1", action="retrieve", dependencies=["step_2"]),
    ]
    graph = ReasoningGraph(intent="Test missing dep", nodes=nodes)
    with pytest.raises(GraphValidationError, match="depends on non-existent node 'step_2'"):
        GraphValidator.validate(graph)

def test_graph_validator_cycle():
    nodes = [
        ReasonNode(id="step_1", action="retrieve", dependencies=["step_2"]),
        ReasonNode(id="step_2", action="execute_python", dependencies=["step_1"]),
    ]
    graph = ReasoningGraph(intent="Test cycle", nodes=nodes)
    with pytest.raises(GraphValidationError, match="Cyclic dependency detected"):
        GraphValidator.validate(graph)

def test_topological_sort():
    nodes = [
        ReasonNode(id="A", action="retrieve", dependencies=[]),
        ReasonNode(id="B", action="retrieve", dependencies=[]),
        ReasonNode(id="C", action="execute_python", dependencies=["A", "B"]),
        ReasonNode(id="D", action="llm_generate", dependencies=["C"]),
    ]
    graph = ReasoningGraph(intent="Test sort", nodes=nodes)
    GraphValidator.validate(graph)
    tiers = GraphValidator.topological_sort(graph)
    assert len(tiers) == 3
    assert set(tiers[0]) == {"A", "B"}
    assert set(tiers[1]) == {"C"}
    assert set(tiers[2]) == {"D"}

@pytest.mark.asyncio
async def test_execution_engine():
    nodes = [
        ReasonNode(id="fetch_data", action="retrieve", parameters={"query": "test query"}, dependencies=[]),
        ReasonNode(id="process_data", action="execute_python", parameters={"code": "print('hello')"}, dependencies=["fetch_data"]),
        ReasonNode(id="summarize", action="llm_generate", parameters={"prompt": "summarize results"}, dependencies=["process_data"]),
    ]
    graph = ReasoningGraph(intent="Test execution", nodes=nodes)
    
    # Import action handlers explicitly for test registration
    import backend.vibethinker.execution.actions  # noqa
    
    engine = LocalSandboxEngine()
    result = await engine.execute(graph)
    
    assert result["status"] == "success"
    context = result["context"]
    assert "fetch_data" in context
    assert "process_data" in context
    assert "summarize" in context
    assert context["fetch_data"]["action"] == "retrieve"
    assert context["process_data"]["action"] == "execute_python"
    assert context["summarize"]["action"] == "llm_generate"
