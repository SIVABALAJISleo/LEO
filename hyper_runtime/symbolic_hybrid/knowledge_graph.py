import logging
from typing import List, Dict, Optional

logger = logging.getLogger("HyperCore.KnowledgeGraph")

class LocalKnowledgeGraph:
    """
    A lightweight, deterministic in-memory Knowledge Graph.
    Used by the Symbolic Fast Path to bypass neural computation for factual queries.
    """
    def __init__(self):
        # Format: { "subject": { "relation": ["object1", "object2"] } }
        self.triplets: Dict[str, Dict[str, List[str]]] = {}
        
    def add_fact(self, subject: str, relation: str, obj: str):
        subject = subject.lower()
        relation = relation.lower()
        
        if subject not in self.triplets:
            self.triplets[subject] = {}
        if relation not in self.triplets[subject]:
            self.triplets[subject][relation] = []
            
        if obj not in self.triplets[subject][relation]:
            self.triplets[subject][relation].append(obj)
            
    def query(self, subject: str, relation: str) -> Optional[List[str]]:
        subject = subject.lower()
        relation = relation.lower()
        
        if subject in self.triplets and relation in self.triplets[subject]:
            return self.triplets[subject][relation]
        return None
        
    def populate_enterprise_priors(self):
        """Loads some mock enterprise knowledge."""
        self.add_fact("france", "capital", "Paris")
        self.add_fact("paris", "country", "France")
        self.add_fact("python", "creator", "Guido van Rossum")
        self.add_fact("leo_runtime", "architecture", "CPU-First Sparse Intelligence")
