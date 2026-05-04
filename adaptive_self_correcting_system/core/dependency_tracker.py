from enum import Enum
from typing import List, Dict, Set

class SourceRelationship(str, Enum):
    INDEPENDENT = "INDEPENDENT"
    PARTIAL = "PARTIAL"
    CORRELATED = "CORRELATED"

class DependencyTracker:
    """
    4) DEPENDENCY CHECK (NO ASSUMPTIONS)
    - Track source relationships: independent, partial, correlated cluster
    """
    def __init__(self):
        # Maps source_id -> relationship type with other sources
        self.registry: Dict[str, Dict[str, SourceRelationship]] = {}

    def get_relationship(self, source_a: str, source_b: str) -> SourceRelationship:
        # Default logic for mock
        if source_a == source_b: return SourceRelationship.CORRELATED
        
        # Check if they share the same base model or dataset
        if "llama" in source_a.lower() and "llama" in source_b.lower():
            return SourceRelationship.CORRELATED
            
        return SourceRelationship.INDEPENDENT

    def classify_cluster(self, sources: List[str]) -> SourceRelationship:
        if not sources: return SourceRelationship.INDEPENDENT
        
        relationships = []
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                relationships.append(self.get_relationship(sources[i], sources[j]))
        
        if SourceRelationship.CORRELATED in relationships:
            return SourceRelationship.CORRELATED
        if SourceRelationship.PARTIAL in relationships:
            return SourceRelationship.PARTIAL
            
        return SourceRelationship.INDEPENDENT
吐
