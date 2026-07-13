"""
Ultra-fast hashing engine for IRA.
Used by QSM for O(1) lookups.
NO external dependencies. Pure Python + numpy.
"""
import hashlib
import numpy as np
from typing import List, Optional

class FastHashEngine:
    """
    Provides multiple hashing strategies for different use cases.
    All methods are deterministic and return fixed-size outputs.
    """

    @staticmethod
    def md5_text(text: str) -> str:
        """MD5 hash of text string. Returns 32-char hex string."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    @staticmethod
    def sha256_text(text: str) -> str:
        """SHA-256 hash of text. Returns 64-char hex string."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    def sha256_short(text: str, length: int = 16) -> str:
        """Short SHA-256 hash. Returns first `length` hex chars."""
        return FastHashEngine.sha256_text(text)[:length]

    @staticmethod
    def ngram_hash_embedding(text: str, dim: int = 768) -> np.ndarray:
        """
        ZERO-MODEL embedding using character n-gram hashing.
        Returns a normalized float32 vector of shape (dim,).
        This is the CORE innovation — no model needed for embedding.
        Deterministic, instant, zero GPU/CPU inference cost.

        Algorithm:
        1. Iterate over all character n-grams (3,4,5-grams)
        2. Hash each n-gram to get an index into the vector
        3. Increment that index
        4. Also hash at word level
        5. Apply sub-linear TF scaling
        6. L2-normalize the result
        """
        embedding = np.zeros(dim, dtype=np.float32)
        text_lower = text.lower().strip()

        # Character 3-grams (most common pattern length)
        for i in range(len(text_lower) - 2):
            trigram = text_lower[i:i+3]
            h = int(hashlib.md5(trigram.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            embedding[idx] += 1.0

        # Character 4-grams (captures more context)
        for i in range(len(text_lower) - 3):
            fourgram = text_lower[i:i+4]
            h = int(hashlib.sha1(fourgram.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            embedding[idx] += 0.7

        # Character 5-grams (captures even more context)
        for i in range(len(text_lower) - 4):
            fivegram = text_lower[i:i+5]
            h = int(hashlib.sha1(fivegram.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            embedding[idx] += 0.4

        # Word-level hashing (captures semantic units)
        words = text_lower.split()
        for word in words:
            # Full word hash
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            embedding[idx] += 2.0

            # Word prefix hash (captures word roots)
            if len(word) >= 3:
                prefix = word[:3]
                h = int(hashlib.md5(prefix.encode('utf-8')).hexdigest(), 16)
                idx = h % dim
                embedding[idx] += 1.0

            # Word suffix hash (captures word endings)
            if len(word) >= 3:
                suffix = word[-3:]
                h = int(hashlib.md5(suffix.encode('utf-8')).hexdigest(), 16)
                idx = h % dim
                embedding[idx] += 0.8

        # Bigram hashing (word pairs capture word order)
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            h = int(hashlib.sha1(bigram.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            embedding[idx] += 1.5

        # Apply sub-linear TF scaling (log(1+x)) to prevent
        # high-frequency n-grams from dominating
        np.log1p(embedding, out=embedding)

        # L2 normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding /= norm

        return embedding

    @staticmethod
    def lsh_hash(embedding: np.ndarray, hyperplanes: np.ndarray) -> str:
        """
        Locality-Sensitive Hashing: project embedding onto random
        hyperplanes and convert to binary hash string.
        This is what enables O(1) bucket lookup.
        """
        projection = np.dot(embedding, hyperplanes)
        binary = ''.join(['1' if p > 0 else '0' for p in projection])
        return binary

    @staticmethod
    def generate_hyperplanes(dim: int, hash_bits: int,
                             seed: int = 42) -> np.ndarray:
        """
        Generate random hyperplane matrix for LSH.
        Returns array of shape (dim, hash_bits).
        Deterministic with seed.
        """
        rng = np.random.RandomState(seed)
        return rng.randn(dim, hash_bits).astype(np.float32)

    @staticmethod
    def simhash_embedding(embedding: np.ndarray, bits: int = 64) -> str:
        """
        SimHash alternative: divide embedding into chunks,
        sum each chunk, and create binary hash from signs.
        """
        chunk_size = max(1, len(embedding) // bits)
        result = []
        for i in range(bits):
            start = i * chunk_size
            end = min(start + chunk_size, len(embedding))
            chunk_sum = np.sum(embedding[start:end])
            result.append('1' if chunk_sum > 0 else '0')
        return ''.join(result)
