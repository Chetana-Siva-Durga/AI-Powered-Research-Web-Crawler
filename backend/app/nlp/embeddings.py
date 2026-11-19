import logging
import threading
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

logger = logging.getLogger("research_scope.nlp.embeddings")


class EmbeddingEngine:
    """
    Computes dense semantic embeddings for research ideas and scholarly papers.
    Pre-warms SentenceTransformer at startup in a background thread so requests
    are served without delay. Uses local_files_only=True to skip HuggingFace
    network check calls (model is already cached after first install).
    Falls back to Latent Semantic Analysis if the model is not yet ready.
    """

    def __init__(self):
        self._st_model = None
        self._st_available = False
        self._loading = False
        self._load_lock = threading.Lock()
        # Start background pre-warm immediately on module load
        self._prewarm_thread = threading.Thread(target=self._prewarm_model, daemon=True)
        self._prewarm_thread.start()

    def _prewarm_model(self):
        """Loads SentenceTransformer model in a background thread at startup."""
        with self._load_lock:
            if self._st_available or self._loading:
                return
            self._loading = True
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Pre-warming SentenceTransformer ('all-MiniLM-L6-v2')...")
            # Use local_files_only=True to avoid HuggingFace network HEAD requests
            try:
                model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            except Exception:
                # First time download (model not yet in cache)
                logger.info("Model not in local cache — downloading from HuggingFace...")
                model = SentenceTransformer("all-MiniLM-L6-v2")
            self._st_model = model
            self._st_available = True
            logger.info("SentenceTransformer pre-warmed and ready.")
        except Exception as e:
            logger.warning("SentenceTransformer unavailable (%s). Will use LSA fallback.", e)
            self._st_available = False
        finally:
            self._loading = False

    def wait_for_model(self, timeout: float = 25.0):
        """Waits up to `timeout` seconds for the model to finish loading."""
        if self._prewarm_thread.is_alive():
            self._prewarm_thread.join(timeout=timeout)

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generates dense vector embeddings for a list of text strings.
        Output shape: (N, D) where vectors are L2-normalized.
        """
        if not texts:
            return np.zeros((0, 64), dtype=np.float32)

        # Use SentenceTransformer if available (wait briefly if still loading)
        if self._loading:
            self._prewarm_thread.join(timeout=20.0)

        if self._st_available and self._st_model is not None:
            try:
                embeddings = self._st_model.encode(
                    texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
                )
                return embeddings.astype(np.float32)
            except Exception as e:
                logger.warning("SentenceTransformer encoding failed (%s). Falling back to LSA.", e)

        # LSA fallback
        clean_texts = [t.strip() if t and len(t.strip()) > 0 else "research" for t in texts]
        n_samples = len(clean_texts)
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=2000,
            sublinear_tf=True,
        )
        tfidf = vectorizer.fit_transform(clean_texts)
        vocab_size = tfidf.shape[1]

        n_components = min(64, vocab_size - 1 if vocab_size > 1 else 1, n_samples)
        if n_components > 1:
            svd = TruncatedSVD(n_components=n_components, random_state=42)
            dense_vecs = svd.fit_transform(tfidf)
        else:
            dense_vecs = tfidf.toarray()

        norm_vecs = normalize(dense_vecs, norm="l2")
        return norm_vecs.astype(np.float32)

    def get_single_embedding(self, text: str) -> np.ndarray:
        """Generates embedding for a single text string."""
        return self.get_embeddings([text])[0]


# Global singleton — pre-warm starts immediately on import
embedding_engine = EmbeddingEngine()
