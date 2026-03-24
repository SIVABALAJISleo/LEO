import logging
from typing import List
import re

logger = logging.getLogger(__name__)

class ContextCompressor:
    """
    Compresses retrieved document context to reduce model token usage.
    Removes redundant info and prioritizes high-density sentences.
    """
    def compress(self, context_list: List[str], max_tokens: int = 1000) -> str:
        """
        Reduces the size of retrieved documents while preserving semantic value.
        """
        logger.info(f"context_compression_start: docs={len(context_list)}")
        
        # 1. Deduplicate sentences across all docs
        all_text = " ".join(context_list)
        sentences = re.split(r'(?<=[.!?]) +', all_text)
        unique_sentences = list(dict.fromkeys(sentences)) # Preserves order
        
        # 2. Importance Scoring (Simplified: length and keyword density)
        # In a real system, we'd use a small cross-encoder or LLM
        scored_sentences = []
        for s in unique_sentences:
            score = len(s.split()) # Basic length priority
            # Could add query-relevance scoring here
            scored_sentences.append((s, score))
            
        # 3. Sort and truncate
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        compressed_text = ""
        token_count = 0
        for s, score in scored_sentences:
            s_tokens = len(s.split())
            if token_count + s_tokens < max_tokens:
                compressed_text += s + " "
                token_count += s_tokens
            else:
                break
                
        reduction = 1.0 - (len(compressed_text)/len(all_text)) if all_text else 0.0
        logger.info(f"context_compression_complete: reduction={reduction:.2%}")
        return compressed_text.strip()

global_compressor = ContextCompressor()
