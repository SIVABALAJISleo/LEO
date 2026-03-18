"""
Context Expander Module (BONUS)
Injects retrieved docs or conversation context into the answer dynamically
without relying on an LLM to weave them together.
"""

class ContextExpander:
    def expand(self, text: str, query: str, context_docs: list = None) -> str:
        """
        Expands the base text with contextual information based on intent length.
        """
        words = text.split()
        
        # If the answer is already quite long, don't force expansion
        if len(words) > 75:
            return text

        expansion = text
        
        # Standard elaboration for short definitions
        if len(words) < 25:
            expansion += f"\n\n**Additional Context for '{query}':**\n"
            expansion += "This concept is critical for optimizing AI inference pipelines and ensuring system scalability."

        # Bonus: Integrate provided context literally 
        if context_docs and isinstance(context_docs, list):
            expansion += "\n\n**Related Evidence:**\n"
            for doc in context_docs[:2]:  # Only top 2 docs
                clean_doc = str(doc).strip()
                if clean_doc:
                    expansion += f"• {clean_doc[:100]}...\n"

        return expansion.strip()
