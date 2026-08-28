"""
HYPER v6 Breakthrough Engine - Contract Analyzer
Analyzes query intent, complexity, and contract constraints to determine optimal compute tier.
Supports:
  - Tier 0: SQLite Exact Cache (<1ms)
  - Tier 1: FAISS Semantic Cache (<10ms)
  - Tier 2: Tiny Model (0.5B-1.5B) iGPU Vulkan
  - Tier 3: Small Model (3B-7B) iGPU SYCL/Vulkan
  - Tier 4: Kimi K3 / K2 Local Frontier Engine (Pure Local Execution)
"""

import re
from typing import Dict, Any, List

class ContractAnalyzer:
    """
    Contract-Aware Cognitive Routing Classifier.
    Routes queries to:
      - Tier 0 (<1ms SQLite)
      - Tier 1 (<10ms FAISS)
      - Tier 2 (0.5B-1.5B iGPU Vulkan)
      - Tier 3 (3B-7B Small Model iGPU SYCL/Vulkan)
      - Tier 4 (Kimi K3 / K2 Pure Local Frontier Engine)
    """

    # Common exact-match patterns or simple greetings for Tier 0 fast-path
    EXACT_PATTERNS: List[str] = [
        r"^(hi|hello|hey|greetings|ping|test)\b",
        r"^what is 2\s*\+\s*2",
        r"^who built hyper",
        r"^what is the capital of france",
        r"^time$",
        r"^status$"
    ]

    # Simple factual or common pattern queries suited for Tier 1 FAISS semantic lookup
    SEMANTIC_PATTERNS: List[str] = [
        r"\b(define|meaning of|what is|who is|explain simply)\b",
        r"\b(how to calculate|formula for|syntax of)\b"
    ]

    # Heavy reasoning / complex generation keywords requiring Tier 3
    COMPLEX_PATTERNS: List[str] = [
        r"\b(architect|design|refactor|optimize|write a full|deep analysis|proof|theorem|multi-step|step by step)\b",
        r"\b(python script|backend service|dockerfile|kubernetes|algorithm implementation)\b"
    ]

    # Frontier / Ultra-High Complexity patterns requiring Tier 4 (Kimi Local Frontier)
    FRONTIER_PATTERNS: List[str] = [
        r"\b(kimi|2\.8t|frontier|quantum simulation|hyper-complex|formal proof|enterprise architecture|trillion)\b"
    ]

    def __init__(self):
        pass

    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Analyzes a query string and returns contract routing decision metadata.
        """
        query_clean = query.strip().lower()
        query_len = len(query_clean)

        # Calculate raw complexity score (0.0 to 1.0)
        complexity_score = self._compute_complexity(query_clean)

        # Check Tier 0 exact pattern candidate
        for pattern in self.EXACT_PATTERNS:
            if re.search(pattern, query_clean, re.IGNORECASE):
                return {
                    "tier": 0,
                    "tier_name": "Tier 0: SQLite Exact Cache",
                    "complexity": 0.05,
                    "contract_type": "EXACT_CACHE",
                    "estimated_tokens": max(10, query_len // 4),
                    "recommended_backend": "sqlite",
                    "reasoning": "Matched exact fast-path pattern."
                }

        # Check Tier 4 Frontier candidate (Kimi Local Frontier Engine)
        is_frontier_candidate = any(re.search(p, query_clean, re.IGNORECASE) for p in self.FRONTIER_PATTERNS)
        if is_frontier_candidate or complexity_score >= 0.85 or query_len > 800:
            return {
                "tier": 4,
                "tier_name": "Tier 4: Kimi K3 / K2 (Local Frontier Engine)",
                "complexity": round(complexity_score, 3),
                "contract_type": "LOCAL_FRONTIER_REASONING",
                "estimated_tokens": max(100, query_len // 2),
                "recommended_backend": "kimi_local_engine",
                "reasoning": f"Routed to Tier 4 (Kimi Local Frontier) due to complexity ({complexity_score:.2f}) or explicit keyword match."
            }

        # Check Tier 1 semantic pattern candidate
        is_semantic_candidate = any(re.search(p, query_clean, re.IGNORECASE) for p in self.SEMANTIC_PATTERNS)

        # Check Tier 3 complex pattern candidate
        is_complex_candidate = any(re.search(p, query_clean, re.IGNORECASE) for p in self.COMPLEX_PATTERNS)

        if is_complex_candidate or complexity_score > 0.60 or query_len > 300:
            target_tier = 3
            tier_name = "Tier 3: Small Model (3B-7B) iGPU SYCL/Vulkan"
            contract_type = "REASONING_HEAVY"
            backend = "vulkan_3b"
        elif is_semantic_candidate or complexity_score < 0.35 or query_len < 100:
            target_tier = 1
            tier_name = "Tier 1: FAISS Semantic Cache"
            contract_type = "SEMANTIC_RETRIEVAL"
            backend = "faiss_minilm"
        else:
            target_tier = 2
            tier_name = "Tier 2: Tiny Model (0.5B-1.5B) iGPU Vulkan"
            contract_type = "FAST_GENERATION"
            backend = "vulkan_1.5b"

        return {
            "tier": target_tier,
            "tier_name": tier_name,
            "complexity": round(complexity_score, 3),
            "contract_type": contract_type,
            "estimated_tokens": max(20, query_len // 3),
            "recommended_backend": backend,
            "reasoning": f"Query length {query_len} chars, complexity {complexity_score:.2f}."
        }

    def _compute_complexity(self, query: str) -> float:
        """
        Heuristic complexity formula based on sentence structure, code markers, and length.
        """
        score = 0.2
        if len(query) > 100:
            score += 0.2
        if len(query) > 250:
            score += 0.2
        if len(query) > 500:
            score += 0.2
        if re.search(r"[{};=<>\+\-\*\/\[\]]", query):
            score += 0.15
        if re.search(r"\b(why|how|explain|compare|contrast|difference|theorem|proof|architecture)\b", query):
            score += 0.15
        if "\n" in query:
            score += 0.1
        return min(1.0, score)

if __name__ == "__main__":
    analyzer = ContractAnalyzer()
    test_queries = [
        "hi",
        "what is the capital of France?",
        "Define quantum entanglement.",
        "Write a full Python script to implement binary search with logging and error handling.",
        "Run quantum simulation on local Kimi K3 model for hyper-complex theorem proof."
    ]
    for q in test_queries:
        res = analyzer.analyze(q)
        print(f"Query: '{q}' -> Tier {res['tier']} ({res['tier_name']})")
