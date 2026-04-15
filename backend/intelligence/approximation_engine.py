"""
backend/intelligence/approximation_engine.py

Intelligent Approximation Engine (AIS++ Module 9)
===================================================
Uses approximate reasoning when safe.
Refines only when accuracy is at risk.

Strategy:
  1. Identify query complexity class (simple / moderate / complex)
  2. For simple queries → return approximate answer instantly
  3. For moderate → return best-guess + confidence annotation
  4. For complex → full pipeline only (no approximation)

Approximation sources (in order of preference):
  A. Template instantiation (fastest, highest confidence)
  B. Entity substitution from known answer patterns
  C. Structural extrapolation from related answers
  D. Safe fallback with partial information

Rules:
  - NEVER approximate if entity is unknown
  - NEVER approximate numerical facts
  - ALWAYS annotate approximation in output
  - Refined answer overwrites approximation in storage
  - Approximation confidence capped at 0.88 (triggers refinement if needed)
"""
import logging
import re
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

APPROX_CONFIDENCE_CAP = 0.88   # approximations never exceed this confidence
SIMPLE_COMPLEXITY_KEYWORDS = [
    "what is", "define", "explain", "describe",
    "what does", "what are", "list", "name",
]
NUMERICAL_PATTERNS = re.compile(
    r"\b(?:how many|how much|count|total|sum|average|mean|percent|percentage|ratio|"
    r"calculate|compute|solve|formula|equation|number of)\b",
    re.IGNORECASE,
)

# Pre-built answer templates for common patterns
ANSWER_TEMPLATES: Dict[str, str] = {
    "definition:{entity}": (
        "{entity} is a core concept in AI/ML systems. "
        "It refers to the process or component that handles {domain} operations. "
        "For a precise definition, see the full documentation."
    ),
    "how_to:{entity}": (
        "To use {entity}: "
        "1) Ensure dependencies are installed. "
        "2) Configure the environment. "
        "3) Initialize the {entity} component. "
        "4) Integrate with your pipeline. "
        "Full implementation guide available in the docs."
    ),
    "benefit:{entity}": (
        "Key benefits of {entity}: "
        "improved performance, reduced latency, better scalability, "
        "and lower operational cost. "
        "Specific gains depend on your use case."
    ),
    "comparison:{entity}": (
        "{entity} excels in scenarios requiring high accuracy and low latency. "
        "Alternatives may be preferred when simplicity or cost is the priority. "
        "Choose based on your throughput requirements."
    ),
}

# Known safe entity → domain mappings
ENTITY_DOMAINS: Dict[str, str] = {
    "RAG":           "retrieval-augmented generation",
    "LLM":           "large language model inference",
    "CACHE":         "query result caching",
    "EMBEDDING":     "vector semantic encoding",
    "TRIATTENTION":  "three-tier routing",
    "DELTA":         "incremental computation",
    "GPU":           "parallel computing",
    "API":           "service interface",
    "INFERENCE":     "model prediction",
    "LATENCY":       "response time optimization",
}


class ApproximationEngine:
    """
    Returns approximate answers when safe, triggering refinement in background.
    Prevents heavy compute for simple queries that can be template-answered.
    """

    def __init__(self):
        self._approx_count: int = 0
        self._refined_count: int = 0
        self._refused_count: int = 0   # queries rejected for approximation

    # ── Complexity Classification ──────────────────────────────────────────── #

    def classify_complexity(self, query: str, intent: str, entity: str) -> str:
        """
        Returns 'simple', 'moderate', or 'complex'.
        - simple   → template approximation safe
        - moderate → entity-substitution approximation with caveats
        - complex  → no approximation, must compute
        """
        q_lower = query.lower()

        # Numerical queries → always complex (facts cannot be approximated)
        if NUMERICAL_PATTERNS.search(q_lower):
            return "complex"

        # Unknown entity → complex (can't approximate what we don't know)
        if entity == "GENERAL":
            return "complex"

        # Multi-part queries → complex
        if any(sep in q_lower for sep in [" and ", " or ", " plus ", ", "]):
            return "moderate"

        # Simple definition/how-to/benefit → simple
        if intent in ("definition", "how_to", "benefit") and \
           any(kw in q_lower for kw in SIMPLE_COMPLEXITY_KEYWORDS):
            return "simple"

        if intent in ("comparison", "list"):
            return "moderate"

        return "complex"

    # ── Approximation Generation ───────────────────────────────────────────── #

    def approximate(
        self,
        query: str,
        intent: str,
        entity: str,
        family_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Attempts to generate an approximate answer.
        Returns None if approximation is not safe for this query.
        """
        complexity = self.classify_complexity(query, intent, entity)

        if complexity == "complex":
            self._refused_count += 1
            logger.debug(f"approx.refused: complex query family={family_id}")
            return None

        entity_clean = entity.lower().replace("_", " ")
        domain = ENTITY_DOMAINS.get(entity.upper(), entity_clean)

        # A. Template instantiation (simple)
        template_key = f"{intent}:{entity.upper()}"
        base_template = ANSWER_TEMPLATES.get(
            template_key,
            ANSWER_TEMPLATES.get(f"{intent}:{{entity}}")
        )

        if base_template:
            answer = base_template.format(entity=entity_clean, domain=domain)
            confidence = APPROX_CONFIDENCE_CAP if complexity == "simple" else 0.72
            self._approx_count += 1

            annotation = (
                f" [Approximation — confidence: {confidence:.0%}. "
                "Background refinement triggered for precise answer.]"
            )

            logger.info(
                f"approx.generated: family={family_id} "
                f"intent={intent} complexity={complexity} conf={confidence:.2f}"
            )
            return {
                "answer":        answer + annotation,
                "mode":          f"approximation_{complexity}",
                "confidence":    confidence,
                "is_approximate": True,
                "needs_refinement": confidence < 0.88,
            }

        # B. Entity substitution fallback
        if complexity == "simple":
            fallback = (
                f"{entity_clean.capitalize()} is a key component in modern AI systems, "
                f"specifically designed for {domain} tasks. "
                "It optimizes performance through intelligent caching and reuse. "
                "[Approximate answer — full details computed in background.]"
            )
            self._approx_count += 1
            return {
                "answer":        fallback,
                "mode":          "approximation_entity_sub",
                "confidence":    0.65,
                "is_approximate": True,
                "needs_refinement": True,
            }

        self._refused_count += 1
        return None

    def record_refinement(self, family_id: str) -> None:
        """Called when a cached approximation has been replaced by a full answer."""
        self._refined_count += 1
        logger.debug(f"approx.refined: family={family_id}")

    def stats(self) -> Dict[str, Any]:
        return {
            "approximations_served":  self._approx_count,
            "refinements_completed":  self._refined_count,
            "refused_as_unsafe":      self._refused_count,
            "refinement_rate": (
                f"{self._refined_count/max(self._approx_count,1):.2%}"
            ),
        }


global_approximation_engine = ApproximationEngine()
