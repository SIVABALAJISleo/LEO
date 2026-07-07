import logging
from typing import Dict

logger = logging.getLogger(__name__)

class FragmentComposer:
    """
    Phase 3.5: Answer Fragment System.
    Composes full responses from reusable intelligence fragments:
    - definition
    - steps
    - examples
    - advantages (NEW)
    - edge cases
    """
    def compose(self, fragments: Dict[str, str], style: str = "standard") -> str:
        parts = []
        
        if "definition" in fragments:
            parts.append(fragments["definition"])
            
        if "steps" in fragments:
            parts.append(f"\nHere are the steps:\n{fragments['steps']}")
            
        if "examples" in fragments:
            parts.append(f"\nExamples:\n{fragments['examples']}")
            
        if "advantages" in fragments:
            parts.append(f"\nAdvantages & Benefits:\n{fragments['advantages']}")
            
        if "edge_cases" in fragments:
            parts.append(f"\nImportant Considerations:\n{fragments['edge_cases']}")
            
        full_answer = "\n".join(parts)
        logger.info(f"fragment_compose: sections={list(fragments.keys())}")
        return full_answer

global_fragment_composer = FragmentComposer()
