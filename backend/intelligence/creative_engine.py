"""
backend/intelligence/creative_engine.py
Creative Simulation Engine

Simulates creativity using recombination, mutation, and template-driven variations
without heavy model inference.
"""
import logging
import random
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CreativeSimulationEngine:
    def __init__(self):
        self.creative_templates = [
            "Imagine a synergy between {e1} and {e2}. This hybrid approach creates a unique dynamic where {context} is completely reimagined.",
            "By fusing the principles of {e1} with the mechanics of {e2}, we unlock new potentials. Consider how {context} could evolve under this paradigm.",
            "What if {e1} was driven by {e2}? This novel concept suggests a future where {context} becomes highly optimized and interconnected.",
        ]
        
    def simulate(self, decomposed: Dict[str, Any], context_fragments: list) -> str:
        """
        Generates a creative response by recombining entities and context.
        """
        entities = decomposed.get("entities", [])
        if len(entities) >= 2:
            e1, e2 = entities[0], entities[1]
        elif len(entities) == 1:
            e1 = entities[0]
            e2 = "advanced technologies"
        else:
            e1 = "emerging ideas"
            e2 = "existing paradigms"
            
        context = " ".join(context_fragments[:1]) if context_fragments else "traditional methods are scaled exponentially"
        
        template = random.choice(self.creative_templates) # nosec B311
        
        simulation = template.format(e1=e1, e2=e2, context=context)
        
        # Simple mutation
        mutations = [
            ("reimagined", "transformed"),
            ("evolve", "accelerate"),
            ("potentials", "capabilities"),
            ("optimized", "streamlined")
        ]
        
        for old, new in mutations:
            if random.random() > 0.5: # nosec B311
                simulation = simulation.replace(old, new)
                
        logger.info("creative_engine: Generated simulated creative response.")
        return simulation

global_creative_engine = CreativeSimulationEngine()
