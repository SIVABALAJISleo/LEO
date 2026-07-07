from typing import Tuple, Optional

class OntologyEngine:
    """
    3. ONTOLOGY + DISAMBIGUATION
    - Map input to predefined ontology
    - Trigger clarification on multiple mappings
    """
    def __init__(self):
        self.concepts = ["SYSTEM_QUERY", "DATA_TRANSFORM", "SECURITY_AUDIT"]

    def map_concept(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        # Mock ontology mapping
        matches = [c for c in self.concepts if c in user_input.upper()]
        
        if len(matches) > 1:
            return None, f"AMBIGUITY: Input matches multiple concepts ({', '.join(matches)}). Please specify intent."
        
        if not matches:
            return "GENERAL_TASK", None
            
        return matches[0], None

