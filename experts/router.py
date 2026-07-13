"""
experts/router.py
Production-grade cache-aware Mixture-of-Experts Router with TF-IDF cosine similarity routing.
Provides confidence scoring and automatic low-confidence fallback.
"""

import logging
import numpy as np
import re
from typing import Dict, Any, List

from experts.domain_experts import (
    ReasoningExpert,
    MathematicsExpert,
    CodingExpert,
    CybersecurityExpert,
    CreativeWritingExpert,
    SummarizationExpert,
    TranslationExpert,
    ConversationExpert,
    PlanningExpert,
    DocumentUnderstandingExpert
)

logger = logging.getLogger(__name__)

class MoERouter:
    def __init__(self, fallback_threshold: float = 0.35):
        self.fallback_threshold = fallback_threshold
        self.experts = {
            "reasoning": ReasoningExpert(),
            "mathematics": MathematicsExpert(),
            "coding": CodingExpert(),
            "cybersecurity": CybersecurityExpert(),
            "creative": CreativeWritingExpert(),
            "summarization": SummarizationExpert(),
            "translation": TranslationExpert(),
            "conversation": ConversationExpert(),
            "planning": PlanningExpert(),
            "document": DocumentUnderstandingExpert()
        }
        
        # Reference phrases for TF-IDF vector routing
        self.domain_vocab = [
            # reasoning
            "prove", "verify", "deduce", "logic", "premise", "conclusion", "if then", "implies", "therefore",
            # mathematics
            "plus", "minus", "sum", "multiply", "divide", "sqrt", "equation", "calculate", "solve", "math",
            # coding
            "def ", "class ", "function", "import ", "const ", "let ", "return ", "compile", "refactor", "loop",
            # cybersecurity
            "sql injection", "xss", "cross site", "vulnerability", "audit", "security", "exploit", "owasp", "cve",
            # creative
            "story", "poem", "metaphor", "write a creative", "novel", "narrative", "melancholy", "creative",
            # summarization
            "summarize", "synopsis", "compaction", "extractive", "shorten", "gist", "brief", "summary",
            # translation
            "translate", "kannada", "telugu", "malayalam", "spanish", "french", "dictionary", "language",
            # conversation
            "hello", "hi", "how are you", "greetings", "chat", "talk", "status", "weather",
            # planning
            "depends on", "schedule", "gantt", "critical path", "milestone", "plan", "roadmap", "tasks",
            # document
            "pdf", "docx", "csv", "xml", "json", "paragraphs", "table cell", "metadata", "layout"
        ]
        
        # Define domain profiles (binary vectors of keywords)
        self.domain_vectors = self._build_domain_vectors()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 200

    def _build_domain_vectors(self) -> Dict[str, np.ndarray]:
        vectors = {}
        # Map each domain to vocab indices
        domain_keywords = {
            "reasoning": ["prove", "verify", "deduce", "logic", "premise", "conclusion", "if then", "implies", "therefore"],
            "mathematics": ["plus", "minus", "sum", "multiply", "divide", "sqrt", "equation", "calculate", "solve", "math"],
            "coding": ["def ", "class ", "function", "import ", "const ", "let ", "return ", "compile", "refactor", "loop"],
            "cybersecurity": ["sql injection", "xss", "cross site", "vulnerability", "audit", "security", "exploit", "owasp", "cve"],
            "creative": ["story", "poem", "metaphor", "write a creative", "novel", "narrative", "melancholy", "creative"],
            "summarization": ["summarize", "synopsis", "compaction", "extractive", "shorten", "gist", "brief", "summary"],
            "translation": ["translate", "kannada", "telugu", "malayalam", "spanish", "french", "dictionary", "language"],
            "conversation": ["hello", "hi", "how are you", "greetings", "chat", "talk", "status", "weather"],
            "planning": ["depends on", "schedule", "gantt", "critical path", "milestone", "plan", "roadmap", "tasks"],
            "document": ["pdf", "docx", "csv", "xml", "json", "paragraphs", "table cell", "metadata", "layout"]
        }
        
        for dom, keywords in domain_keywords.items():
            vec = np.zeros(len(self.domain_vocab), dtype=np.float32)
            for kw in keywords:
                if kw in self.domain_vocab:
                    vec[self.domain_vocab.index(kw)] = 1.0
            # Normalize profile
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            vectors[dom] = vec
        return vectors

    def _vectorize_query(self, query: str) -> np.ndarray:
        q_lower = query.lower()
        vec = np.zeros(len(self.domain_vocab), dtype=np.float32)
        for idx, kw in enumerate(self.domain_vocab):
            # Use regex word boundaries or substring search for key sequences
            if kw.endswith(" "):
                # Starts with code patterns
                pattern = r"\b" + re.escape(kw.strip()) + r"\b"
            else:
                pattern = re.escape(kw)
            matches = len(re.findall(pattern, q_lower))
            vec[idx] = float(matches)
        
        # Apply term-frequency smoothing
        vec = np.log1p(vec)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def route(self, query: str) -> Dict[str, Any]:
        query_norm = " ".join(query.lower().split())
        
        # 1. Semantic Cache Check
        if query_norm in self.cache:
            logger.info(f"[MoERouter] Cache hit for query: '{query_norm[:40]}'")
            return self.cache[query_norm]

        # 2. Vectorize and Compute Cosine Similarity
        q_vec = self._vectorize_query(query)
        scores = {}
        for dom, dom_vec in self.domain_vectors.items():
            scores[dom] = float(np.dot(q_vec, dom_vec))

        # Determine chosen expert based on max score
        chosen_expert = max(scores, key=scores.get)
        confidence = scores[chosen_expert]

        # 3. Fallback when confidence is low
        if confidence < self.fallback_threshold:
            logger.warning(f"[MoERouter] Low routing confidence ({confidence:.3f}). Falling back to 'conversation' generalist expert.")
            chosen_expert = "conversation"

        # Execute expert logic
        expert_res = self.experts[chosen_expert].run(query)

        result = {
            "query": query,
            "chosen_expert": chosen_expert,
            "confidence": round(confidence, 4),
            "scores": {k: round(v, 4) for k, v in scores.items()},
            "result": expert_res
        }

        # Cache management with FIFO eviction
        if len(self.cache) >= self.max_cache_size:
            first_key = next(iter(self.cache))
            self.cache.pop(first_key)

        self.cache[query_norm] = result
        return result
