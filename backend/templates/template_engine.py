"""
Template Compiler
Generates structured answers for common query patterns without model calls.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

DEFINITION_TEMPLATES = {
    "RAG": "Retrieval-Augmented Generation (RAG) is an AI technique that retrieves relevant documents before generating responses, improving accuracy and reducing hallucinations.",
    "LLM": "A Large Language Model (LLM) is a neural network trained on vast text datasets to understand and generate human language.",
    "AI":  "Artificial Intelligence (AI) is the simulation of human intelligence processes by computer systems, including learning, reasoning, and problem-solving.",
    "ML":  "Machine Learning (ML) is a subset of AI that enables systems to learn and improve from experience without being explicitly programmed.",
    "GPU": "A Graphics Processing Unit (GPU) is a specialized processor designed to accelerate the rendering of images and increasingly used for parallel AI computations.",
    "API": "An Application Programming Interface (API) is a set of protocols and tools that allow software applications to communicate with each other.",
    "KV":  "Key-Value (KV) cache is a caching mechanism used in transformer models to store intermediate computation states for reuse, reducing latency.",
    "PPE": "Predictive Precomputation Engine (PPE) is a system that pre-generates answers to likely user queries before they are asked.",
}


class TemplateEngine:
    """
    Generates canned or template-based answers without model calls.
    Used for simple, structured queries with predictable outputs.
    """

    def render(self, normalized_query: Dict[str, Any]) -> Optional[str]:
        """Returns a template answer if one exists, else None."""
        intent = normalized_query.get("intent")
        entity = normalized_query.get("entity", "").upper()

        if intent == "definition" and entity in DEFINITION_TEMPLATES:
            answer = DEFINITION_TEMPLATES[entity]
            logger.info(f"template_hit: entity={entity}")
            return answer

        if intent == "calculation":
            return self._eval_math(normalized_query.get("original", ""))

        return None

    def _eval_math(self, query: str) -> Optional[str]:
        """Safely evaluates simple math expressions."""
        import re
        match = re.search(r"(\d+(?:\.\d+)?)\s*([\+\-\*\/])\s*(\d+(?:\.\d+)?)", query)
        if match:
            a, op, b = float(match.group(1)), match.group(2), float(match.group(3))
            ops = {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b != 0 else None}
            result = ops.get(op)
            if result is not None:
                return f"The result of {a} {op} {b} = {result}"
        return None

    def add_definition(self, entity: str, definition: str):
        """Dynamically expand the template store at runtime."""
        DEFINITION_TEMPLATES[entity.upper()] = definition
        logger.info(f"template_added: entity={entity}")


global_template_engine = TemplateEngine()
