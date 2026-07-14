import logging
import re
from typing import List

logger = logging.getLogger(__name__)

class IntelligentPromptCompressor:
    """
    Subsystem 16: Intelligent Prompt Compression.
    Information-theoretic approach to stripping redundant tokens and whitespace
    from the prompt and retrieved context *before* invoking the transformer.
    Reduces KV cache load and attention computation bounds.
    """
    def __init__(self):
        # Common stop words that hold low semantic value in a strict logic context
        self.stop_words = set([
            "a", "an", "the", "and", "but", "if", "or", "because", "as", "what",
            "which", "who", "whom", "this", "that", "these", "those", "am", "is",
            "are", "was", "were", "be", "been", "being", "have", "has", "had", 
            "having", "do", "does", "did", "doing", "would", "should", "could", 
            "ought", "i", "we", "you", "he", "she", "it", "they"
        ])
        
    def _strip_whitespace(self, text: str) -> str:
        """Removes multi-line gaps, excessive tabs, and spaces."""
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
        
    def _remove_duplicate_sentences(self, text: str) -> str:
        """Removes exact duplicate sentences which often appear in RAG contexts."""
        sentences = re.split(r'(?<=[.!?]) +', text)
        seen = set()
        unique_sentences = []
        for s in sentences:
            s_clean = s.strip()
            if s_clean.lower() not in seen:
                seen.add(s_clean.lower())
                unique_sentences.append(s_clean)
        return " ".join(unique_sentences)
        
    def _lexical_token_elimination(self, text: str) -> str:
        """Removes low-value stop words. (Used only aggressively)."""
        words = text.split()
        compressed = [w for w in words if w.lower() not in self.stop_words]
        return " ".join(compressed)

    def compress_context(self, context_list: List[str], max_tokens: int = 500, aggressive: bool = False) -> str:
        """
        Compresses an array of retrieved context strings into a highly dense block.
        """
        raw_text = "\n".join(context_list)
        
        # 1. Clean whitespace
        compressed = self._strip_whitespace(raw_text)
        
        # 2. Semantic deduplication
        compressed = self._remove_duplicate_sentences(compressed)
        
        # 3. Aggressive stop-word elimination (if forced)
        if aggressive:
            compressed = self._lexical_token_elimination(compressed)
            
        # 4. Truncation to max bounds (rough token estimate: 1 word ≈ 1.3 tokens)
        words = compressed.split()
        estimated_word_limit = int(max_tokens / 1.3)
        if len(words) > estimated_word_limit:
            compressed = " ".join(words[:estimated_word_limit])
            logger.info(f"Context truncated to {max_tokens} estimated tokens.")
            
        compression_ratio = len(compressed) / (len(raw_text) + 1e-9)
        logger.debug(f"Prompt compression complete. Size reduced to {compression_ratio*100:.1f}% of original.")
        
        return compressed
