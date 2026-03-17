"""
Answer Refiner
Fixes grammar, structure, and clarity issues in generated answers.
No model calls — uses rule-based text transformations.
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class AnswerRefiner:
    """
    Rule-based answer refinement: text normalization, deduplication, capitalization.
    Designed to be a micro-cost post-processing step that improves quality.
    """

    def refine(self, answer: str, issues: List[str]) -> str:
        """Applies targeted fixes based on identified quality issues."""
        if not answer:
            return answer

        refined = answer

        # Fix 1: Normalize whitespace
        refined = re.sub(r"\s+", " ", refined).strip()

        # Fix 2: Ensure sentence ends with punctuation
        if refined and refined[-1] not in ".!?":
            refined += "."

        # Fix 3: Capitalize first letter
        if refined:
            refined = refined[0].upper() + refined[1:]

        # Fix 4: Remove duplicate consecutive sentences
        if "repetitive" in issues:
            refined = self._deduplicate_sentences(refined)

        # Fix 5: Expand common abbreviations for clarity
        abbreviations = {
            r"\bRAG\b": "Retrieval-Augmented Generation (RAG)",
            r"\bLLM\b": "Large Language Model (LLM)",
            r"\bAPI\b": "Application Programming Interface (API)",
        }
        # Only expand on first occurrence
        for abbr, full in abbreviations.items():
            if re.search(abbr, refined):
                refined = re.sub(abbr, full, refined, count=1)
                break  # Only expand one per response

        logger.debug(f"answer_refined: len_before={len(answer)} len_after={len(refined)}")
        return refined

    def _deduplicate_sentences(self, text: str) -> str:
        """Remove duplicate adjacent sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        seen = set()
        unique = []
        for s in sentences:
            norm = s.strip().lower()
            if norm not in seen:
                seen.add(norm)
                unique.append(s.strip())
        return " ".join(unique)


global_refiner = AnswerRefiner()
