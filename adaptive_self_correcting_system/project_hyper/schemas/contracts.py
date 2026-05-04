from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class ComplexityLevel(str, Enum):
    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None
    latency_budget_ms: Optional[int] = 500

class QueryResponse(BaseModel):
    answer: str
    complexity: ComplexityLevel
    confidence: float
    latency_ms: float
    path: str
    cache_hit: bool

