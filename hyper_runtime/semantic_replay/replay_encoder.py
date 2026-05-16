import numpy as np
import hashlib
import logging
from typing import List, Union

logger = logging.getLogger("HyperCore.SemanticEncoder")

class FallbackTFIDFSVDEncoder:
    """
    TF-IDF + SVD fallback encoder for CPU-first environments without heavy deep learning models.
    Achieves dense vector representations via TruncatedSVD over sparse TF-IDF matrices.
    """
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.is_fitted = False
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.decomposition import TruncatedSVD
            self.vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
            self.svd = TruncatedSVD(n_components=embedding_dim, random_state=42)
        except ImportError:
            logger.warning("scikit-learn not available. Fallback encoder will use random hashing projection.")
            self.vectorizer = None
            self.svd = None

        # Corpus buffer for initial warm-up fitting
        self.warmup_corpus = [
            "What is the capital of France?",
            "Explain quantum computing basics and qubits.",
            "How does artificial intelligence work?",
            "HyperCore runtime optimizes CPU execution and semantic replay.",
            "Locality sensitive hashing and approximate nearest neighbors.",
            "Fast Fourier transforms and neural operator surrogates.",
            "Asynchronous distributed training and DiLoCo parameter synchronization.",
            "Speculative decoding accelerates inference via draft models."
        ]
        self._fit_warmup()

    def _fit_warmup(self):
        if self.vectorizer and self.svd:
            try:
                tfidf_matrix = self.vectorizer.fit_transform(self.warmup_corpus)
                # Ensure n_components <= number of samples/features
                n_samples, n_features = tfidf_matrix.shape
                effective_dim = min(self.embedding_dim, n_samples - 1, n_features - 1)
                if effective_dim < self.embedding_dim:
                    self.svd.n_components = max(1, effective_dim)
                self.svd.fit(tfidf_matrix)
                self.is_fitted = True
            except Exception as e:
                logger.error(f"Error fitting TF-IDF+SVD warmup: {e}")

    def fit(self, corpus: List[str]):
        if self.vectorizer and self.svd and len(corpus) > 5:
            try:
                tfidf_matrix = self.vectorizer.fit_transform(corpus)
                n_samples, n_features = tfidf_matrix.shape
                effective_dim = min(self.embedding_dim, n_samples - 1, n_features - 1)
                self.svd.n_components = max(1, effective_dim)
                self.svd.fit(tfidf_matrix)
                self.is_fitted = True
            except Exception as e:
                logger.error(f"Error fitting TF-IDF+SVD corpus: {e}")

    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        if isinstance(text, str):
            text = [text]

        if self.vectorizer and self.svd and self.is_fitted:
            try:
                tfidf_matrix = self.vectorizer.transform(text)
                vectors = self.svd.transform(tfidf_matrix)
                # Pad if SVD components were reduced due to small warmup corpus
                if vectors.shape[1] < self.embedding_dim:
                    padding = np.zeros((vectors.shape[0], self.embedding_dim - vectors.shape[1]), dtype=np.float32)
                    vectors = np.hstack([vectors, padding])
                return vectors.astype(np.float32)
            except Exception as e:
                logger.error(f"SVD transform failed: {e}. Using fallback hashing.")

        # Fallback hashing projection if sklearn is missing or untrained
        vectors = []
        for t in text:
            np.random.seed(int(hashlib.sha256(t.encode('utf-8')).hexdigest()[:8], 16))
            v = np.random.randn(self.embedding_dim).astype(np.float32)
            norm = np.linalg.norm(v)
            vectors.append(v / norm if norm > 0 else v)
        return np.array(vectors, dtype=np.float32)


class SemanticEmbeddingEngine:
    """
    Primary embedding engine supporting sentence-transformers with automatic
    graceful degradation to TF-IDF + SVD fallback encoder.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", embedding_dim: int = 384, force_fallback: bool = False):
        self.embedding_dim = embedding_dim
        self.model_name = model_name
        self.use_fallback = force_fallback
        self.encoder = None

        if not force_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading SentenceTransformer model: {model_name}")
                self.encoder = SentenceTransformer(model_name, device="cpu")
            except Exception as e:
                logger.warning(f"SentenceTransformer failed to load ({e}). Deploying TF-IDF+SVD fallback.")
                self.use_fallback = True

        if self.use_fallback or self.encoder is None:
            self.encoder = FallbackTFIDFSVDEncoder(embedding_dim=embedding_dim)

    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        if hasattr(self.encoder, "encode") and not isinstance(self.encoder, FallbackTFIDFSVDEncoder):
            try:
                # sentence-transformers encode
                emb = self.encoder.encode(text, convert_to_numpy=True, show_progress_bar=False)
                if len(emb.shape) == 1:
                    emb = np.expand_dims(emb, axis=0)
                return emb.astype(np.float32)
            except Exception as e:
                logger.error(f"SentenceTransformer encoding error: {e}. Switching to fallback.")
                self.encoder = FallbackTFIDFSVDEncoder(embedding_dim=self.embedding_dim)

        # Fallback encode
        return self.encoder.encode(text)

    def get_fingerprint(self, text: str) -> str:
        """Generates an exact O(1) lookup fingerprint using SHA-256."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
