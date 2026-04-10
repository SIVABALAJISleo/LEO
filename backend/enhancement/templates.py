"""
Templates Module (BONUS)
Holds structural frameworks to enforce consistent output styles based on query intent.
Used for Adaptive Enhancement.
"""

class Templates:
    """
    Provides structural templates to format and enhance raw answers
    based on the underlying query logic (definition, explanation, list, etc.).
    """

    def apply_template(self, answer: str, query: str, intent: str = "general") -> str:
        text = str(answer).strip()
        
        if intent == "definition":
            return self._apply_definition_template(text, query)
        elif intent == "explanation":
            return self._apply_explanation_template(text, query)
        elif intent == "list":
            return self._apply_list_template(text, query)
        
        # General enhancement fallback
        return text

    def _apply_definition_template(self, text: str, query: str) -> str:
        """Forces a clean structural definition format."""
        if not text.startswith("**"):
            # A very simplistic heuristic to try and highlight the subject
            # In a real deployed version, query_shaper entity extraction would feed the subject here.
            subject = [w for w in query.split() if w.lower() not in ["what", "is", "define", "a", "an", "the"]][-1:]
            if subject:
                s = subject[0].capitalize()
                prefix = f"**{s}**"
                if not text.lower().startswith(s.lower()):
                    text = f"{prefix}: {text}"

        return text

    def _apply_explanation_template(self, text: str, query: str) -> str:
        """Ensures explanations are broken into readable chunks."""
        sentences = text.split(". ")
        if len(sentences) > 3:
            # Inject a structural pivot to make it flow better
            pivot = len(sentences) // 2
            sentences.insert(pivot, "\n\nAdditionally,")
            return ". ".join(sentences).replace(",.", ",")
        return text

    def _apply_list_template(self, text: str, query: str) -> str:
        """Ensures lists actually look like lists."""
        if ":" in text and "\n" not in text:
            parts = text.split(":", 1)
            intro = parts[0].strip() + ":"
            items = parts[1].split(",")
            formatted_items = "\n".join([f"• {item.strip()}" for item in items if item.strip()])
            return f"{intro}\n{formatted_items}"
        return text
