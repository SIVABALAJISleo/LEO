"""
backend/intelligence/composer_engine.py
Knowledge Composition Engine

Fetches known fragments for sub-components and combines them using templates.
"""
import logging
from typing import Dict, Any, List, Optional
from backend.rag.embedding_model import search as rag_search

logger = logging.getLogger(__name__)

class ComposerEngine:
    def __init__(self):
        self.templates = {
            "definition": "The concept of {entity} involves {context}. It operates by leveraging related elements like {related}.",
            "how_to": "To utilize {entity}, consider the following steps based on typical patterns:\n1. Understand {related}\n2. Integrate {entity} into the workflow.\n3. Monitor and optimize.",
            "reasoning": "The primary advantage of {entity} is its impact on {related}, enhancing overall efficiency.",
            "example": "A classic use case for {entity} involves combining it with {related} to achieve better results.",
        }
        # entity_type -> {category -> fragment}
        self.manual_fragments: Dict[str, Dict[str, str]] = {}

    def register_fragment(self, entity: str, category: str, content: str):
        """Manually registers a knowledge fragment for composition."""
        if entity not in self.manual_fragments:
            self.manual_fragments[entity] = {}
        self.manual_fragments[entity][category] = content
        logger.info(f"composer_engine: Registered manual fragment for '{entity}' ({category})")

    def compose(self, decomposed: Dict[str, Any]) -> Optional[str]:
        """
        Attempts to build an answer purely by composing fragments of known entities.
        """
        entities = decomposed.get("entities", [])
        # 'intent' might be 'steps', 'definition', etc. from the specialized keys
        # or from the 'intent' field.
        intent = decomposed.get("intent", "information")
        
        if not entities:
            # Check if specialized key is present
            for key in ["definition", "steps", "advantages", "examples"]:
                 if key in decomposed:
                      entities = [decomposed[key]]
                      intent = key
                      break
            if not entities:
                 return None

        primary_entity = entities[0]
        
        # 1. TRY MANUAL FRAGMENTS (Phase 29)
        category_map = {"definition": "Definition", "steps": "Steps", "advantages": "Advantages", "examples": "Examples"}
        category = category_map.get(intent, intent.capitalize())
        
        if primary_entity in self.manual_fragments and category in self.manual_fragments[primary_entity]:
             logger.info(f"composer_engine: Using manual fragment hit for '{primary_entity}'")
             return self.manual_fragments[primary_entity][category]

        # 2. TRY RAG COMPOSITION
        knowledge_pieces = []
        for entity in entities[:2]:
            hits = rag_search(f"definition of {entity}", k=1)
            if hits and hits[0]["score"] > 0.4:
                knowledge_pieces.append(hits[0]["content"])
            else:
                 # If we don't know the core entities, we can't reliably compose a factual answer.
                 # We might fallback to micro-compute or creative engine.
                 pass

        if not knowledge_pieces:
            return None

        primary_entity = entities[0]
        related_entities = ", ".join(entities[1:]) if len(entities) > 1 else "related concepts"
        
        # Build synthesis
        template = self.templates.get(intent, "Regarding {entity}, it closely relates to {related}. Context: {context}")
        
        base_synthesis = template.format(
            entity=primary_entity, 
            related=related_entities,
            context=" ".join(knowledge_pieces[:2])
        )
        
        logger.info(f"composer_engine: Successfully composed answer for intent={intent}")
        return base_synthesis

global_composer_engine = ComposerEngine()
