import logging
import re
from typing import List, Dict, Any, Optional
from backend.data_efficiency.graph import global_graph

logger = logging.getLogger(__name__)

class DigitalTwinEngine:
    """
    Simulates AI reasoning by composing facts from the Knowledge Graph 
    and RAG context. Acts as Layer 9 in the 12-layer stack.
    """
    def __init__(self):
        pass

    def extract_entities(self, query: str) -> List[str]:
        return re.findall(r'\b[A-Z][a-z]+\b', query)

    def resolve_facts(self, entities: List[str], tenant_id: str) -> List[str]:
        facts = []
        for entity in entities:
            relations = global_graph.query_relations(entity, tenant_id)
            for r in relations:
                target = r.get('target', r.get('source'))
                facts.append(f"{entity} is {r['relation']} to {target}.")
        return facts

    def compose_answer(self, facts: List[str], context: List[str]) -> str:
        if not facts and not context:
            return ""
            
        fact_str = " ".join(facts)
        # Simple composition: combine facts with a summary heuristic
        return f"Based on internal knowledge: {fact_str} Related context indicates further details in the provided documents."

    async def reason(self, query: str, context: List[str] = [], tenant_id: str = "default") -> Optional[Dict[str, Any]]:
        """
        Main entry point for Digital Twin reasoning.
        """
        # 1. ENTITY EXTRACTION
        entities = self.extract_entities(query)
        
        # 2. FACT RESOLUTION
        facts = self.resolve_facts(entities, tenant_id)
        
        # 3. ANSWER COMPOSITION
        answer = self.compose_answer(facts, context)
        
        if not answer or len(facts) == 0:
            return None
            
        # 4. CONFIDENCE EVALUATION
        # In this architecture, Digital Twin confidence is based on fact density
        confidence = min(0.95, 0.6 + (len(facts) * 0.1))
        
        logger.info(f"twin_reasoning_complete: confidence={confidence}")
        
        return {
            "answer": answer,
            "confidence": confidence,
            "strategy": "digital_twin_reasoning"
        }

global_twin_engine = DigitalTwinEngine()
