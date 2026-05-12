from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MiniSpec(BaseModel):
    task: str
    inputs: List[Dict[str, str]] # [{"name": "n", "type": "int"}]
    output_type: str
    invariants: List[str]
    examples: List[Dict[str, Any]]
    edge_cases: List[Dict[str, Any]]

class SpecGuard:
    """
    1. SPEC GUARD
    - Extract {intent, constraints}
    - Build mini-spec {inputs, outputs, examples, edge_cases}
    """
    
    async def build_spec(self, user_input: str, constraints: str = "") -> MiniSpec:
        # In a production system, this would use a structured LLM call (e.g. JSON mode)
        # to parse the user's natural language into a formal MiniSpec.
        # For this demo, we'll provide a framework for the parsing logic.
        
        # Simulated extraction
        spec = MiniSpec(
            task=user_input,
            inputs=[{"name": "data", "type": "List[int]"}],
            output_type="int",
            invariants=["Output must be >= 0 if inputs are >= 0"],
            examples=[{"input": [1, 2, 3], "output": 6}],
            edge_cases=[{"input": [], "output": 0}]
        )
        return spec

    def format_for_prompt(self, spec: MiniSpec) -> str:
        return f"""
FORMAL SPECIFICATION:
Task: {spec.task}
Inputs: {spec.inputs}
Output Type: {spec.output_type}
Invariants: {spec.invariants}
Examples: {spec.examples}
Edge Cases: {spec.edge_cases}
"""
