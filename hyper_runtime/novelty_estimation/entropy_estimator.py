import math
import zlib
import numpy as np

class EntropyEstimator:
    """
    Estimates the information density (entropy) of text and token sequences.
    High entropy implies highly dense/novel information.
    """
    
    @staticmethod
    def shannon_entropy(text: str) -> float:
        """
        Calculates the Shannon entropy of a string based on character frequencies.
        Returns a normalized value (typically between 0 and 1 for English text if normalized by max entropy,
        but here we return the raw bits per character, scaled to [0,1] roughly using a max of 5.0 for typical text).
        """
        if not text:
            return 0.0
            
        counts = {}
        for char in text:
            counts[char] = counts.get(char, 0) + 1
            
        length = len(text)
        entropy = 0.0
        for count in counts.values():
            p = count / length
            entropy -= p * math.log2(p)
            
        # Normalize roughly (assuming max entropy of typical char set is ~5.0 bits/char)
        return min(1.0, entropy / 5.0)
        
    @staticmethod
    def compression_ratio(text: str) -> float:
        """
        Uses zlib compression ratio as a proxy for algorithmic complexity (Kolmogorov complexity).
        High compression ratio (compressed / original is small) means low novelty (highly repetitive).
        Returns a value in [0, 1] where 1.0 means highly incompressible (high novelty).
        """
        if not text:
            return 0.0
            
        raw_bytes = text.encode('utf-8')
        compressed_bytes = zlib.compress(raw_bytes)
        
        ratio = len(compressed_bytes) / max(1, len(raw_bytes))
        # zlib on short texts can be > 1.0 due to overhead
        return min(1.0, ratio)
        
    @staticmethod
    def token_novelty(tokens: list) -> float:
        """
        Estimates novelty based on the uniqueness of tokens (Type-Token Ratio).
        """
        if not tokens:
            return 0.0
        unique_tokens = set(tokens)
        ttr = len(unique_tokens) / len(tokens)
        return ttr

    def estimate(self, text: str) -> float:
        """
        Combines entropy metrics into a single entropy score in [0, 1].
        """
        shannon = self.shannon_entropy(text)
        comp = self.compression_ratio(text)
        ttr = self.token_novelty(text.split())
        
        # Weighted combination
        combined = (0.4 * shannon) + (0.4 * comp) + (0.2 * ttr)
        return np.clip(combined, 0.0, 1.0)
