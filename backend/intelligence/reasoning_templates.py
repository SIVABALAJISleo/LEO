import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class ReasoningTemplateSystem:
    """
    Structured template-based generation to bypass LLM inference.
    Fills pre-defined templates with facts from RAG, Fragments, or Graph.
    """
    
    TEMPLATES = {
        "definition": "A {entity} is {fact}. In the context of {context}, it primarily serves as {role}.",
        "comparison": "{entity1} focuses on {fact1}, whereas {entity2} is characterized by {fact2}.",
        "instruction": "To {action} {entity}, follow these steps: {steps}.",
        "benefit": "Using {entity} provides several benefits, most notably: {benefits}."
    }

    def fill(self, intent: str, entity: str, facts: List[str], metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Attempts to fill a template for the given intent and entity."""
        if not intent or not entity or not facts:
            return None
            
        template = self.TEMPLATES.get(intent)
        if not template:
            return None
            
        try:
            if intent == "definition":
                return template.format(
                    entity=entity,
                    fact=facts[0],
                    context=metadata.get("context", "modern AI systems") if metadata else "modern AI systems",
                    role=metadata.get("role", "a critical component") if metadata else "a critical component"
                )
            elif intent == "comparison" and len(facts) >= 2:
                entities = entity.split(" vs ") if " vs " in entity else [entity, "alternative"]
                return template.format(
                    entity1=entities[0],
                    fact1=facts[0],
                    entity2=entities[1] if len(entities) > 1 else "other technologies",
                    fact2=facts[1]
                )
            # Add more logic for instruction/benefit as needed
        except Exception as e:
            logger.warning(f"template_fill_failed: {e}")
            
        return None

global_templates = ReasoningTemplateSystem()
