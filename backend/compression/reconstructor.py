import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AnswerReconstructor:
    """
    Rebuilds full, natural language responses dynamically from compressed knowledge structures.
    """
    
    TEMPLATES = {
        "explanation": "Here is an explanation of **{concept}**:\n\n{points}",
        "steps": "Follow these steps for **{concept}**:\n\n{points}",
        "comparison": "Comparing **{concept}**:\n\n{points}",
        "default": "Analysis of **{concept}**:\n\n{points}"
    }

    def reconstruct(self, compressed_data: Dict[str, Any]) -> str:
        """Assembles the final string from compressed components."""
        concept = compressed_data.get("concept", "the topic")
        intent = compressed_data.get("intent", "default")
        key_points = compressed_data.get("key_points", [])
        
        template = self.TEMPLATES.get(intent, self.TEMPLATES["default"])
        
        points_str = "\n".join([f"- {pt}" if not pt.startswith('-') else pt for pt in key_points])
        if not points_str:
            points_str = "No specific details available."
            
        reconstructed = template.format(concept=concept, points=points_str)
        logger.info(f"answer_reconstructed: {concept} ({intent})")
        return reconstructed

global_reconstructor = AnswerReconstructor()
