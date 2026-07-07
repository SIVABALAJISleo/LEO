import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """
    Structured relationship reasoning layer.
    Maps identities and associations between entities found in RAG documents.
    """
    def __init__(self):
        # In a real system, this would use Neo4j or a specialized graph library.
        # Here we use a persistent dictionary-based adjacency list for demonstration.
        self.nodes = {} # Entity -> Type
        self.edges = {} # (Entity1, Entity2) -> Relation

    def add_relation(self, e1: str, e2: str, relation: str, tenant_id: str = "default"):
        """Adds a relationship between two entities."""
        key1 = f"{tenant_id}:{e1}"
        key2 = f"{tenant_id}:{e2}"
        self.nodes[key1] = "Entity"
        self.nodes[key2] = "Entity"
        self.edges[(key1, key2)] = relation
        logger.debug(f"graph_relation_added: {e1} --({relation})--> {e2} [tenant={tenant_id}]")

    def query_relations(self, entity: str, tenant_id: str = "default") -> List[Dict[str, str]]:
        """Queries relationships for a given entity."""
        key = f"{tenant_id}:{entity}"
        results = []
        for (e1, e2), rel in self.edges.items():
            if e1 == key:
                results.append({"target": e2.split(":")[1], "relation": rel})
            elif e2 == key:
                results.append({"source": e1.split(":")[1], "relation": rel})
        return results

# Global instance
global_graph = KnowledgeGraph()
