"""
phoenix/context_manager.py
Hierarchical Context Manager — 4 levels of context hierarchy.
L1: Current turn (1K tokens, fully processed)
L2: Session summary (256 tokens, compressed history)
L3: RAG retrieval (512 tokens, semantic search)
L4: Long-term semantic memory (embedding database)
"""

import logging
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ContextLevel:
    name:    str
    content: str = ""
    tokens:  int = 0
    max_tokens: int = 1024


class HierarchicalContextManager:
    """
    Manages 4 context tiers. Automatically compresses and promotes
    old content up the hierarchy when the current window overflows.
    """

    def __init__(self, l1_max: int = 1024, l2_max: int = 256,
                 l3_max: int = 512, l4_max: int = 2048):
        self.levels = {
            "L1": ContextLevel("L1 (Current Turn)",    max_tokens=l1_max),
            "L2": ContextLevel("L2 (Session Summary)", max_tokens=l2_max),
            "L3": ContextLevel("L3 (RAG Retrieval)",   max_tokens=l3_max),
            "L4": ContextLevel("L4 (Long-Term Memory)",max_tokens=l4_max),
        }
        self.turn_history: List[Dict[str, str]] = []
        self._word_count_ratio = 0.75  # words ≈ tokens * 0.75

    def _word_count(self, text: str) -> int:
        return len(text.split())

    def _estimate_tokens(self, text: str) -> int:
        return int(self._word_count(text) / self._word_count_ratio)

    def _simple_summarize(self, text: str, max_words: int) -> str:
        """
        Extractive summarization: keep the first + last sentences
        plus any sentence containing key signal words.
        (Replace with a tiny neural summarizer for production.)
        """
        sentences = re.split(r'(?<=[.!?]) +', text.strip())
        if not sentences:
            return text[:max_words * 6]   # ~6 chars/word

        signal_words = ["because", "therefore", "result", "conclusion",
                        "important", "critical", "key", "answer", "final"]
        selected = [sentences[0]]   # Always keep first
        for s in sentences[1:-1]:
            if any(w in s.lower() for w in signal_words):
                selected.append(s)
        if len(sentences) > 1:
            selected.append(sentences[-1])  # Always keep last

        summary = " ".join(selected)
        words = summary.split()
        return " ".join(words[:max_words])

    def add_turn(self, role: str, content: str):
        """Adds a new user/assistant turn to L1. Overflows → compress to L2."""
        turn_text = f"{role.upper()}: {content}"
        self.turn_history.append({"role": role, "content": content})

        current_l1 = self.levels["L1"].content
        new_l1 = (current_l1 + "\n" + turn_text).strip()
        new_token_est = self._estimate_tokens(new_l1)

        if new_token_est > self.levels["L1"].max_tokens:
            # Compress overflow into L2 summary
            overflow = current_l1
            max_l2_words = int(self.levels["L2"].max_tokens * self._word_count_ratio)
            summary = self._simple_summarize(overflow, max_words=max_l2_words)

            existing_l2 = self.levels["L2"].content
            self.levels["L2"].content = (existing_l2 + " " + summary).strip()
            self.levels["L2"].tokens  = self._estimate_tokens(self.levels["L2"].content)
            logger.info(f"[ContextManager] L1 overflow compressed to L2 summary.")

            # Reset L1 to just the latest turn
            self.levels["L1"].content = turn_text
        else:
            self.levels["L1"].content = new_l1

        self.levels["L1"].tokens = self._estimate_tokens(self.levels["L1"].content)

    def inject_retrieval(self, retrieved_chunks: List[str]):
        """Populates L3 with RAG retrieved context chunks."""
        combined = " ".join(retrieved_chunks)
        max_words = int(self.levels["L3"].max_tokens * self._word_count_ratio)
        self.levels["L3"].content = " ".join(combined.split()[:max_words])
        self.levels["L3"].tokens  = self._estimate_tokens(self.levels["L3"].content)

    def inject_long_term_memory(self, memories: List[str]):
        """Populates L4 with long-term semantic memories."""
        combined = "\n".join(memories)
        max_words = int(self.levels["L4"].max_tokens * self._word_count_ratio)
        self.levels["L4"].content = " ".join(combined.split()[:max_words])
        self.levels["L4"].tokens  = self._estimate_tokens(self.levels["L4"].content)

    def build_prompt(self) -> str:
        """
        Assembles the full prompt from all levels (most distant first).
        L4 → L3 → L2 → L1 (current turn is the last thing the model sees).
        """
        parts = []
        for level_name in ["L4", "L3", "L2", "L1"]:
            lvl = self.levels[level_name]
            if lvl.content.strip():
                parts.append(f"[{lvl.name}]\n{lvl.content}")
        return "\n\n".join(parts)

    def get_stats(self) -> Dict[str, Any]:
        return {
            level: {"tokens": lvl.tokens, "max": lvl.max_tokens,
                    "utilization_pct": round(lvl.tokens / lvl.max_tokens * 100, 1)}
            for level, lvl in self.levels.items()
        }
