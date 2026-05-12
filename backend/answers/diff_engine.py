"""
Answer Differential Engine
Reuses previous answers via `base answer + delta modification`.
Avoids full regeneration for queries that are slight variations of answered ones.
"""
import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class DiffEngine:
    """
    Given a base canonical answer and a query variation,
    produces a modified answer without model calls.

    Strategy: identify the variation dimension (more detail / shorter / different entity)
    and apply a targeted transformation.
    """

    def apply_diff(
        self,
        base_answer: str,
        original_query: str,
        shaped_query: Dict[str, Any],
        base_entity: str,
        target_entity: str,
    ) -> Optional[str]:
        """
        Attempt to produce a modified answer for target_entity from a base answer for base_entity.
        Returns None if diff is not applicable.
        """
        if base_entity == target_entity:
            return base_answer  # No diff needed

        # Substitution diff: replace entity name in the answer
        if base_entity.upper() in base_answer.upper():
            modified = re.sub(
                re.escape(base_entity),
                target_entity,
                base_answer,
                flags=re.IGNORECASE,
                count=2,
            )
            if modified != base_answer:
                logger.info(f"diff_applied: {base_entity} → {target_entity}")
                return modified

        return None

    def shorten(self, answer: str, target_words: int = 30) -> str:
        """Produce a shorter version of an answer."""
        words = answer.split()
        if len(words) <= target_words:
            return answer
        # Take first N words, end at last sentence boundary
        truncated = " ".join(words[:target_words])
        last_period = max(truncated.rfind("."), truncated.rfind("!"), truncated.rfind("?"))
        if last_period > 0:
            return truncated[:last_period + 1]
        return truncated + "."

    def elaborate(self, answer: str, additional_context: str) -> str:
        """Expand an answer with additional context without model calls."""
        if not additional_context or additional_context in answer:
            return answer
        return f"{answer.rstrip('.')}. {additional_context.strip()}"


global_diff_engine = DiffEngine()
