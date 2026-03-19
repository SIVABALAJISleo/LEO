"""
Enhancer Module
The core engine that transforms raw text through a cleaning, formatting,
and structurally adaptive expansion pipeline.
"""
from typing import List, Optional
from . import Formatter, ContextExpander, Templates

class AnswerEnhancer:
    """
    Applies the actual textual transformations to reconstruct a better answer.
    """

    def __init__(self):
        self.formatter = Formatter()
        self.expander = ContextExpander()
        self.templates = Templates()

    def enhance(self, answer: str, query: str, context_docs: Optional[List[str]] = None, intent: str = "general") -> dict:
        """
        Executes the multi-stage enhancement sequence.
         RAW -> CLEAN -> STRUCTURE/TEMPLATE -> EXPAND -> FORMAT -> FINAL
        """
        if not answer:
            return {"enhanced": False, "answer": "", "quality_score": 0.0}

        # 1. Clean
        text = self.clean(answer)

        # 2. Template / Structure (Adaptive Enhancement)
        text = self.structure(text, query, intent)

        # 3. Context Expansion (Context-Aware Expansion)
        text = self.expand(text, query, context_docs)

        # 4. Final Format
        final_text = self.format(text)

        return {
            "enhanced": True,
            "answer": final_text,
            "quality_score": 0.92  # Default success score
        }

    def clean(self, text: str) -> str:
        """Basic garbage removal."""
        return str(text).strip()

    def structure(self, text: str, query: str, intent: str) -> str:
        """Applies adaptive intent-based structural templates."""
        return self.templates.apply_template(text, query, intent)

    def expand(self, text: str, query: str, context_docs: Optional[List[str]] = None) -> str:
        """Injects contextual elaboration if the answer is too short."""
        return self.expander.expand(text, query, context_docs)

    def format(self, text: str) -> str:
        """Applies professional typography formatting."""
        return self.formatter.format(text)

global_enhancer = AnswerEnhancer()
