"""
backend/predictive/speculative_executor.py

Speculative Execution Engine (AIS++ Module 6)
==============================================
Predicts queries DURING TYPING (prefix-based completion),
executes likely full queries in parallel before request arrives,
and caches the results — so by the time the user submits, the
answer is already computed.

Rules:
  - Operates on partial queries (≥ 3 chars)
  - Generates top-5 candidate completions per prefix
  - Launches parallel background tasks for each candidate
  - Results stored with `speculative` flag
  - Never blocks the main request path
  - If speculative hit matches confirmed query → instant return
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger(__name__)

MIN_PREFIX_LEN    = 3    # characters before speculation activates
MAX_CANDIDATES    = 5    # parallel candidates per prefix
MATCH_THRESHOLD   = 0.85  # min string similarity to accept a speculative hit

# Known completions from historical patterns
COMPLETION_PATTERNS: Dict[str, List[str]] = {
    "what is": [
        "What is RAG?", "What is an LLM?", "What is AI?",
        "What is machine learning?", "What is an API?"
    ],
    "how to": [
        "How to use RAG?", "How to implement caching?", "How to reduce latency?",
        "How to scale Python?", "How to fine-tune an LLM?"
    ],
    "how do": [
        "How does attention work?", "How does RAG work?",
        "How does caching improve performance?",
    ],
    "define": [
        "Define neural network", "Define embedding", "Define inference",
        "Define latency", "Define throughput"
    ],
    "explain": [
        "Explain transformers", "Explain RAG architecture",
        "Explain vector search", "Explain caching layers",
    ],
    "compare": [
        "Compare RAG vs fine-tuning", "Compare SQL vs NoSQL",
        "Compare CPU vs GPU inference",
    ],
    "benefit": [
        "Benefits of RAG", "Benefits of caching", "Benefits of quantization",
    ],
    "rag": [
        "What is RAG?", "How does RAG work?", "RAG vs fine-tuning",
        "How to implement RAG?", "RAG performance benchmarks",
    ],
    "llm": [
        "What is an LLM?", "How to fine-tune an LLM?", "LLM inference cost",
        "Quantize an LLM", "How to deploy an LLM?",
    ],
    "cache": [
        "How does caching work?", "Types of cache", "Cache eviction strategies",
        "How to implement caching in Python?",
    ],
    "vector": [
        "What is a vector embedding?", "How to build a vector index?",
        "Vector search vs keyword search",
    ],
}


def _string_similarity(a: str, b: str) -> float:
    """Levenshtein-free similarity: longest common subsequence ratio."""
    a, b = a.lower(), b.lower()
    if not a or not b:
        return 0.0
    _m, _n = len(a), len(b)
    # Use a simple character overlap ratio for speed
    a_chars = set(a.split())
    b_chars = set(b.split())
    if not a_chars:
        return 0.0
    overlap = len(a_chars & b_chars) / len(a_chars | b_chars)
    return overlap


class SpeculativeExecutor:
    """
    Predicts and precomputes likely full queries from incomplete prefixes.
    """

    def __init__(self):
        self._speculative_cache: Dict[str, Dict[str, Any]] = {}
        # Track which prefixes we've already speculated on
        self._speculated_prefixes: Set[str] = set()
        self._hits: int = 0
        self._misses: int = 0
        self._launched: int = 0

    # ── Prediction ────────────────────────────────────────────────────────── #

    def predict_completions(self, prefix: str) -> List[str]:
        """
        Returns up to MAX_CANDIDATES likely full queries for the given prefix.
        Matches against known completion patterns.
        """
        prefix_lower = prefix.lower().strip()
        if len(prefix_lower) < MIN_PREFIX_LEN:
            return []

        candidates: List[str] = []
        seen: Set[str] = set()

        # 1. Prefix pattern match
        for pattern, completions in COMPLETION_PATTERNS.items():
            if prefix_lower.startswith(pattern) or pattern.startswith(prefix_lower[:4]):
                for comp in completions:
                    if comp not in seen:
                        candidates.append(comp)
                        seen.add(comp)
            if len(candidates) >= MAX_CANDIDATES:
                break

        # 2. Substring match fallback
        if len(candidates) < MAX_CANDIDATES:
            for pattern, completions in COMPLETION_PATTERNS.items():
                if any(word in prefix_lower for word in pattern.split()):
                    for comp in completions:
                        if comp not in seen:
                            candidates.append(comp)
                            seen.add(comp)
                if len(candidates) >= MAX_CANDIDATES:
                    break

        return candidates[:MAX_CANDIDATES]

    # ── Speculative Launch ─────────────────────────────────────────────────── #

    async def speculate(
        self,
        prefix: str,
        session_id: str,
        tenant_id: str,
        bg_compute,
    ) -> None:
        """
        Called when new characters are typed (streaming input).
        Launches background precompute for predicted completions.
        Non-blocking — returns immediately.
        """
        if len(prefix) < MIN_PREFIX_LEN:
            return

        prefix_key = prefix.lower().strip()
        if prefix_key in self._speculated_prefixes:
            return   # Already speculated for this prefix

        self._speculated_prefixes.add(prefix_key)
        candidates = self.predict_completions(prefix)

        if not candidates:
            return

        for candidate in candidates:
            try:
                asyncio.create_task(
                    bg_compute.enqueue(
                        candidate,
                        tenant_id,
                        "SPECULATIVE_EXECUTOR",
                        session_id,
                        priority="speculative",
                    )
                )
                self._launched += 1
            except Exception as exc:
                logger.warning(f"speculative.launch_error: {exc}")

        logger.debug(
            f"speculative.launched: prefix='{prefix}' "
            f"candidates={len(candidates)} total_launched={self._launched}"
        )

    # ── Hit Check ─────────────────────────────────────────────────────────── #

    def check_speculative_hit(
        self,
        confirmed_query: str,
        global_memory,
    ) -> Optional[Dict[str, Any]]:
        """
        After the user confirms a query, checks if our speculation hit.
        Returns the cached speculative answer if similarity >= threshold.
        """
        candidates = self.predict_completions(confirmed_query[:20])
        for candidate in candidates:
            sim = _string_similarity(confirmed_query, candidate)
            if sim >= MATCH_THRESHOLD:
                hit = global_memory.lookup(candidate)
                if hit and hit.get("confidence", 0) >= 0.90:
                    self._hits += 1
                    logger.info(
                        f"speculative.hit: confirmed='{confirmed_query}' "
                        f"matched='{candidate}' sim={sim:.3f}"
                    )
                    return {**hit, "mode": "speculative_hit", "matched_candidate": candidate}

        self._misses += 1
        return None

    def stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        return {
            "speculative_hits":     self._hits,
            "speculative_misses":   self._misses,
            "hit_rate":             f"{self._hits/total:.2%}" if total else "N/A",
            "total_launched":       self._launched,
            "speculated_prefixes":  len(self._speculated_prefixes),
        }


global_speculative_executor = SpeculativeExecutor()
