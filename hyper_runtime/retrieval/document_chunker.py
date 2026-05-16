import re
import hashlib
import logging
from typing import List, Dict, Any

logger = logging.getLogger("HyperCore.Chunker")

class SemanticChunker:
    """
    Splits documents into semantically coherent chunks for retrieval.
    Supports sentence-boundary splitting, overlap windowing,
    deduplication via SHA-256 fingerprinting, and metadata propagation.
    """
    def __init__(
        self,
        chunk_size: int = 256,
        chunk_overlap: int = 32,
        min_chunk_size: int = 20
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self._seen_hashes = set()

    def _split_sentences(self, text: str) -> List[str]:
        """Splits text on sentence boundaries."""
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _fingerprint(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def chunk(self, text: str, doc_id: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunks text using a sliding window over word tokens.
        Returns a list of chunk dicts with content, fingerprint, and metadata.
        """
        words = text.split()
        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)

        for i in range(0, len(words), step):
            chunk_words = words[i: i + self.chunk_size]
            if len(chunk_words) < self.min_chunk_size:
                # Attach small tail to the last chunk if possible
                if chunks:
                    prev = chunks[-1]
                    prev["content"] += " " + " ".join(chunk_words)
                    prev["fingerprint"] = self._fingerprint(prev["content"])
                continue

            content = " ".join(chunk_words)
            fp = self._fingerprint(content)

            # Skip exact duplicates within this chunking session
            if fp in self._seen_hashes:
                continue
            self._seen_hashes.add(fp)

            chunks.append({
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}::{i}",
                "content": content,
                "fingerprint": fp,
                "metadata": {**metadata, "char_offset": i, "word_count": len(chunk_words)},
            })

        return chunks

    def reset_dedup(self):
        """Clear the cross-document dedup state."""
        self._seen_hashes.clear()
