import re
import logging


logger = logging.getLogger(__name__)

class MicroRefiner:
    """
    CPU-based micro-refinement.
    Polishes composed text for better flow and formatting without LLMs.
    """
    def refine(self, text: str) -> str:
        # 1. Deduplicate sentences (common in fragment composition)
        sentences = re.split(r'(?<=[.!?]) +', text)
        unique_sentences = []
        seen = set()
        for s in sentences:
            if s.lower().strip() not in seen:
                unique_sentences.append(s)
                seen.add(s.lower().strip())
        
        refined = " ".join(unique_sentences)
        
        # 2. Fix spacing and transitions
        refined = refined.replace(" .", ".").replace(" ,", ",")
        refined = re.sub(r'\n{3,}', '\n\n', refined)
        
        # 3. Add stylized markers if text is a list
        if refined.count('\n-') > 2 or refined.count('\n*') > 2:
            refined = "### Analysis Summary\n\n" + refined
            
        return refined.strip()

global_refiner = MicroRefiner()
