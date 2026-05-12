"""
Domain Constraint Engine
Enforces domain scope — restricts queries to defined domains (AI/ML/computing/SaaS).
Out-of-domain queries are simplified, redirected, or rejected before entering the pipeline.
This is the FIRST gate — prevents junk from consuming compute.
"""
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# --- Domain Configuration ---
ALLOWED_DOMAINS = {
    "ai":         ["artificial intelligence", "machine learning", "deep learning", "neural network",
                   "transformer", "llm", "language model", "inference", "embedding", "vector",
                   "rag", "retrieval", "fine-tuning", "prompt", "token", "attention"],
    "computing":  ["cpu", "gpu", "memory", "cache", "latency", "throughput", "compute",
                   "processor", "optimization", "performance", "benchmark", "distributed",
                   "cloud", "kubernetes", "docker", "api", "server", "database", "sql"],
    "saas":       ["saas", "subscription", "tenant", "workspace", "billing", "usage",
                   "dashboard", "analytics", "monitoring", "telemetry", "metrics"],
    "software":   ["python", "fastapi", "redis", "postgresql", "celery", "onnx",
                   "algorithm", "function", "class", "module", "library", "framework",
                   "code", "debug", "error", "exception", "test", "deploy"],
}

# Flat set of all known domain terms
ALL_DOMAIN_TERMS = {term for terms in ALLOWED_DOMAINS.values() for term in terms}

# Queries that are always safe regardless
ALWAYS_ALLOW_PATTERNS = [
    r"^what is \w+",
    r"^define \w+",
    r"^explain \w+",
    r"^how (to|does) \w+",
]

# Out-of-domain redirect topics
OOD_REDIRECTS = {
    "weather":  "I specialize in AI/computing topics. For weather, use a weather service.",
    "sports":   "I specialize in AI/computing topics. For sports updates, use a sports platform.",
    "cooking":  "I specialize in AI/computing topics. For recipes, try a cooking app.",
    "finance":  "I can discuss AI in finance, but not specific stock tips. Refine your question.",
}


class DomainGuard:
    """
    Gate 0: Domain enforcement.
    Prevents out-of-scope queries from consuming any pipeline compute.
    """

    def enforce(self, query: str) -> Dict[str, Any]:
        """
        Returns {allowed: bool, reason: str, simplified_query: Optional[str]}
        """
        q_lower = query.lower().strip()

        # Always-allow patterns (structural matches)
        for pattern in ALWAYS_ALLOW_PATTERNS:
            if re.search(pattern, q_lower):
                return {"allowed": True, "reason": "pattern_match", "simplified_query": query}

        # Domain term matching
        matched_terms = [t for t in ALL_DOMAIN_TERMS if t in q_lower]
        if matched_terms:
            logger.debug(f"domain_allowed: terms={matched_terms[:3]}")
            return {"allowed": True, "reason": "domain_match", "simplified_query": query}

        # Out-of-domain redirect
        for ood_key, redirect_msg in OOD_REDIRECTS.items():
            if ood_key in q_lower:
                logger.info(f"domain_redirect: topic={ood_key}")
                return {
                    "allowed": False,
                    "reason": "out_of_domain",
                    "simplified_query": None,
                    "redirect": redirect_msg,
                }

        # General queries — simplify and allow with low complexity
        logger.info(f"domain_simplify: query='{query[:50]}'")
        return {
            "allowed": True,
            "reason": "general_allowed",
            "simplified_query": self._simplify(query),
        }

    def _simplify(self, query: str) -> str:
        """Strip filler and reduce to core question."""
        q = re.sub(r"\b(please|kindly|can you|could you|i want to know)\b", "", query, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", q).strip()

    def get_domain(self, query: str) -> str:
        """Returns the matched domain name."""
        q_lower = query.lower()
        for domain, terms in ALLOWED_DOMAINS.items():
            if any(t in q_lower for t in terms):
                return domain
        return "general"


global_domain_guard = DomainGuard()
