"""
Text processing utilities shared across all IRA pillars.
"""
import re
from typing import List, Set, Tuple
from collections import Counter

class TextNormalizer:
    """Normalizes text for consistent hashing and comparison."""

    # Comprehensive stop words list
    STOP_WORDS: Set[str] = {
        "a", "an", "the", "and", "or", "but", "if", "then", "else",
        "when", "where", "how", "what", "which", "who", "whom",
        "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did",
        "will", "would", "shall", "should", "may", "might",
        "can", "could", "must", "need", "dare", "ought",
        "to", "of", "in", "for", "on", "with", "at", "by",
        "from", "as", "into", "through", "during", "before",
        "after", "above", "below", "between", "under", "over",
        "out", "off", "up", "down", "about", "against",
        "me", "my", "myself", "we", "our", "ours", "ourselves",
        "you", "your", "yours", "yourself", "yourselves",
        "he", "him", "his", "himself", "she", "her", "hers",
        "herself", "it", "its", "itself", "they", "them",
        "their", "theirs", "themselves",
        "this", "that", "these", "those",
        "not", "no", "nor", "very", "just", "also", "only",
        "own", "same", "so", "than", "too", "quite", "rather",
        "tell", "give", "please", "thank", "thanks", "hello",
        "hi", "hey", "ok", "okay", "yes", "yeah", "nope",
        "know", "think", "want", "like", "get", "got", "go",
        "going", "come", "came", "make", "made", "take", "took",
        "see", "saw", "say", "said", "use", "used", "find",
        "found", "let", "put", "keep", "kept"
    }

    # Punctuation to remove
    PUNCTUATION = re.compile(r'[^\w\s\-\']')

    # Extra whitespace
    MULTI_SPACE = re.compile(r'\s+')

    @classmethod
    def normalize(cls, text: str) -> str:
        """Full normalization pipeline."""
        text = text.lower().strip()
        text = cls.PUNCTUATION.sub(' ', text)
        text = cls.MULTI_SPACE.sub(' ', text)
        text = text.strip()
        return text

    @classmethod
    def normalize_for_hash(cls, text: str) -> str:
        """Aggressive normalization for hashing (removes stop words)."""
        text = cls.normalize(text)
        words = text.split()
        words = [w for w in words if w not in cls.STOP_WORDS and len(w) > 1]
        return ' '.join(words)

    @classmethod
    def extract_pattern(cls, text: str) -> str:
        """
        Extract query pattern by replacing entities with placeholders.
        'What is the population of Tokyo' → 'what is the population of [ENTITY]'
        'Calculate 45 * 32' → 'calculate [NUM] * [NUM]'
        """
        pattern = text.lower()
        # Replace numbers safely without catastrophic backtracking
        pattern = re.sub(r'\b\d+(?:\.\d+)?\b', '[NUM]', pattern)
        # Replace proper nouns (capitalized words)
        pattern = re.sub(r'\b[A-Z][a-z]+\b', '[ENTITY]', pattern)
        # Replace quoted strings
        pattern = re.sub(r'["\'][^"\']+["\']', '[QUOTE]', pattern)
        return pattern

class TopicExtractor:
    """Extracts key topics/nouns from text."""

    # Common suffixes that indicate nouns
    NOUN_SUFFIXES = (
        'tion', 'sion', 'ment', 'ness', 'ity', 'ism', 'ist',
        'ance', 'ence', 'er', 'or', 'ar', 'ee', 'ure',
        'age', 'dom', 'ship', 'hood', 'ing', 'ence'
    )

    @classmethod
    def extract_topics(cls, text: str,
                       min_length: int = 3,
                       max_topics: int = 10) -> List[str]:
        """
        Extract key topics from text using simple heuristics.
        Returns list of topic strings, most important first.
        """
        normalized = TextNormalizer.normalize(text)
        words = normalized.split()

        # Score each word
        word_scores = Counter()
        for word in words:
            if word in TextNormalizer.STOP_WORDS:
                continue
            if len(word) < min_length:
                continue
            score = 1.0
            # Bonus for noun-like suffixes
            if any(word.endswith(suffix) for suffix in cls.NOUN_SUFFIXES):
                score += 2.0
            # Bonus for longer words (more specific)
            score += min(len(word) / 5.0, 2.0)
            # Penalty for very common words
            if word in ('also', 'however', 'therefore', 'because',
                        'although', 'while', 'since', 'unless'):
                score -= 5.0
            word_scores[word] += max(score, 0.1)

        # Return top topics
        return [word for word, _ in word_scores.most_common(max_topics)]

    @classmethod
    def extract_key_phrases(cls, text: str,
                            max_phrases: int = 5) -> List[str]:
        """Extract 2-3 word key phrases from text."""
        normalized = TextNormalizer.normalize(text)
        words = normalized.split()
        phrases = []

        # Bigrams
        for i in range(len(words) - 1):
            if (words[i] not in TextNormalizer.STOP_WORDS and
                words[i+1] not in TextNormalizer.STOP_WORDS):
                phrases.append(f"{words[i]} {words[i+1]}")

        # Trigrams
        for i in range(len(words) - 2):
            if (words[i] not in TextNormalizer.STOP_WORDS and
                words[i+1] not in TextNormalizer.STOP_WORDS and
                words[i+2] not in TextNormalizer.STOP_WORDS):
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")

        # Deduplicate and return most common
        phrase_counts = Counter(phrases)
        return [p for p, _ in phrase_counts.most_common(max_phrases)]
