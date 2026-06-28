from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ReasonNode(BaseModel):
    id: str = Field(..., description="Unique identifier for the step")
    action: str = Field(..., description="The action to execute (e.g., 'retrieve', 'execute_python', 'z3_solve')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action")
    dependencies: List[str] = Field(default_factory=list, description="IDs of steps that must complete before this one")

class ReasoningGraph(BaseModel):
    intent: str = Field(..., description="The high-level intent classified by the neural router")
    nodes: List[ReasonNode] = Field(..., description="The DAG of execution steps")
    target_hardware: Optional[str] = Field("CPU", description="Preferred hardware target (e.g., CPU, iGPU, NPU)")
