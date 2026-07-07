import logging
import re
from typing import List
from backend.data_efficiency.graph import global_graph

logger = logging.getLogger(__name__)

class ShadowPredictor:
    """
    Predicts the next potential queries in an active conversation.
    Uses context-aware expansion and knowledge graph neighbor traversal.
    """
    def predict_next(self, query: str, context: List[str] = []) -> List[str]:
        predictions = []
        
        # 1. HEURISTIC NEXT STEPS
        q = query.lower()
        if "how" in q:
            predictions.append(f"Can you give an example of {query}?")
            predictions.append("What are the prerequisites for this?")
        elif "calculate" in q:
            predictions.append("Can you double check those numbers?")
        
        # 2. KNOWLEDGE GRAPH NEIGHBORS (Layer 6 integration)
        entities = re.findall(r'\b[A-Z][a-z]+\b', query)
        for entity in entities:
            # We assume tenant_id="default" for shadow pre-inference
            relations = global_graph.query_relations(entity)
            for r in relations:
                target = r.get('target', r.get('source'))
                predictions.append(f"What is the relationship between {entity} and {target}?")
        
        return list(set(predictions))[:3] # Limit to top 3 predictions

global_shadow_predictor = ShadowPredictor()
