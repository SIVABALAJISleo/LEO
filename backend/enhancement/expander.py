"""
Answer Expander
Expands short/thin answers with additional context from retrieval.
No large model calls — uses RAG context to pad answers.
"""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class AnswerExpander:
    """
    Expands incomplete answers by appending relevant retrieved context.
    Priority: coherent addition > sentence padding > no-op
    """

    def expand(self, answer: str, context_docs: List[str], issues: List[str]) -> str:
        """
        Expands answer if quality issues indicate it's too short or thin.
        """
        if "too_short" not in issues and "vague" not in issues:
            return answer  # No expansion needed

        expansion = self._build_expansion(answer, context_docs)
        if expansion:
            expanded = f"{answer.rstrip('.')}. {expansion}"
            logger.info(f"answer_expanded: added={len(expansion)} chars")
            return expanded

        return answer

    def _build_expansion(self, answer: str, context_docs: List[str]) -> Optional[str]:
        """
        Picks the best non-redundant sentence from context to append.
        """
        if not context_docs:
            return None

        answer_lower = answer.lower()
        candidates = []

        for doc in context_docs:
            # Split into sentences
            import re
            sentences = re.split(r"(?<=[.!?])\s+", doc)
            for sentence in sentences:
                s = sentence.strip()
                if len(s) < 20:
                    continue
                # Skip if already in the answer (avoid redundancy)
                if s[:30].lower() in answer_lower:
                    continue
                candidates.append(s)

        if not candidates:
            return None

        # Return the most relevant-looking candidate (longest non-redundant sentence)
        candidates.sort(key=len, reverse=True)
        return candidates[0] if candidates else None


global_expander = AnswerExpander()
