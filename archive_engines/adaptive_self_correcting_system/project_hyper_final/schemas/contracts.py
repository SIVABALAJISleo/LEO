from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ComplexityLevel(str, Enum):
    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    EXTREME = "EXTREME"

class ExecutionMode(str, Enum):
    NORMAL = "NORMAL"
    FALLBACK = "FALLBACK"

class QueryRequest(BaseModel):
    query: str
    latency_budget_ms: Optional[int] = 500

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    mode: ExecutionMode
    refinement_available: bool
    complexity: ComplexityLevel
    latency_ms: float
    path: str

