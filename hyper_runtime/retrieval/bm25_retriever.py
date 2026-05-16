import re
import math
import logging
from collections import defaultdict
from typing import List, Dict, Tuple

logger = logging.getLogger("HyperCore.BM25")

class BM25Retriever:
    """
    BM25 (Best Match 25) keyword retrieval engine.
    Industry-standard sparse lexical search for hybrid retrieval.
    k1=1.5, b=0.75 are standard Okapi BM25 parameters.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[str] = []
        self.doc_ids: List[str] = []
        self.tf: List[Dict[str, int]] = []          # term frequencies per doc
        self.idf: Dict[str, float] = {}             # inverse document frequencies
        self.avgdl: float = 0.0
        self.N: int = 0

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())

    def add_documents(self, texts: List[str], doc_ids: List[str]):
        self.corpus = texts
        self.doc_ids = doc_ids
        self.N = len(texts)

        # Build term frequencies per document
        self.tf = []
        doc_lengths = []
        df: Dict[str, int] = defaultdict(int)  # document frequency

        for text in texts:
            tokens = self._tokenize(text)
            doc_lengths.append(len(tokens))
            freq: Dict[str, int] = defaultdict(int)
            seen_terms = set()
            for token in tokens:
                freq[token] += 1
                if token not in seen_terms:
                    df[token] += 1
                    seen_terms.add(token)
            self.tf.append(dict(freq))

        self.avgdl = sum(doc_lengths) / max(1, self.N)

        # Compute IDF with Okapi BM25 formula
        for term, freq in df.items():
            self.idf[term] = math.log(1 + (self.N - freq + 0.5) / (freq + 0.5))

    def score(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Returns list of (doc_index, bm25_score) sorted descending."""
        if not self.corpus:
            return []

        query_tokens = self._tokenize(query)
        scores = []

        for doc_idx, tf_dict in enumerate(self.tf):
            doc_len = sum(tf_dict.values())
            score = 0.0
            for token in query_tokens:
                if token not in self.idf:
                    continue
                tf_val = tf_dict.get(token, 0)
                idf_val = self.idf[token]
                numerator = tf_val * (self.k1 + 1)
                denominator = tf_val + self.k1 * (1 - self.b + self.b * doc_len / max(1, self.avgdl))
                score += idf_val * (numerator / max(1e-9, denominator))
            scores.append((doc_idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
