"""
Token Optimizer
Reduces prompt token count before sending to expensive models.
Applies deduplication, compression, and truncation without loss of meaning.
"""
import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Common filler phrases that add no information
FILLER_PHRASES = [
    r"\bplease\b", r"\bkindly\b", r"\bcould you\b", r"\bwould you\b",
    r"\bcan you\b", r"\bi (want|need|would like) (to|you to)\b",
    r"\btell me\b", r"\bexplain to me\b", r"\bhelp me understand\b",
]


class TokenOptimizer:
    """
    Reduces token count for prompts before model inference.
    Applies: filler removal → deduplication → sentence compaction → truncation.
    Target: reduce average prompt by 20-40% without accuracy loss.
    """

    def optimize(self, query: str, context_docs: Optional[List[str]] = None, max_context_tokens: int = 2000) -> dict:
        """
        Returns optimized query and context.
        """
        optimized_query = self._clean_query(query)
        optimized_context = ""

        if context_docs:
            optimized_context = self._compress_context(context_docs, max_context_tokens)

        reduction = 1.0 - (len(optimized_query) / max(len(query), 1))
        logger.debug(f"token_optimized: reduction={reduction:.1%}")

        return {
            "query": optimized_query,
            "context": optimized_context,
            "token_reduction": round(reduction, 3),
        }

    def _clean_query(self, query: str) -> str:
        """Remove filler phrases and normalize whitespace."""
        q = query.strip()
        for pattern in FILLER_PHRASES:
            q = re.sub(pattern, "", q, flags=re.IGNORECASE)
        # Normalize whitespace
        q = re.sub(r"\s+", " ", q).strip()
        # Capitalize first letter
        return q[0].upper() + q[1:] if q else query

    def _compress_context(self, docs: List[str], max_tokens: int) -> str:
        """
        Deduplicates and truncates context to fit within token limit.
        Approximation: 1 token ≈ 4 chars.
        """
        max_chars = max_tokens * 4
        seen_sentences = set()
        result_parts = []
        current_len = 0

        for doc in docs:
            sentences = re.split(r"(?<=[.!?])\s+", doc)
            for sentence in sentences:
                s_normalized = sentence.strip().lower()
                if s_normalized in seen_sentences or len(s_normalized) < 10:
                    continue
                seen_sentences.add(s_normalized)
                if current_len + len(sentence) > max_chars:
                    break
                result_parts.append(sentence.strip())
                current_len += len(sentence)

        return " ".join(result_parts)


global_token_optimizer = TokenOptimizer()
