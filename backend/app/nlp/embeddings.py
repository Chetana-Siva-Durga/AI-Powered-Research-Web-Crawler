from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger("research_scope.nlp.embeddings")

MODEL_MIN_AVAILABLE_MEMORY_BYTES = 1024 * 1024 * 1024
ENCODE_BATCH_SIZE = 8
_CGROUP_MEMORY_FILES = (
    ("/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory.current"),
    (
        "/sys/fs/cgroup/memory/memory.limit_in_bytes",
        "/sys/fs/cgroup/memory/memory.usage_in_bytes",
    ),
)


class EmbeddingEngine:
    """Lazily loads one local SentenceTransformer, with an LSA fallback."""

    def __init__(self):
        self._st_model = None
        self._st_available = False
        self._loading = False
        self._model_load_attempted = False
        self._load_lock = threading.Lock()
        self._inference_lock = threading.Lock()

    @property
    def is_ready(self) -> bool:
        # The TF-IDF/LSA path is available even before a transformer is loaded.
        return self._st_available or not self._loading

    @property
    def model_loading(self) -> bool:
        return self._loading

    @staticmethod
    def _available_container_memory_bytes() -> Optional[int]:
        for limit_path, usage_path in _CGROUP_MEMORY_FILES:
            try:
                limit_text = Path(limit_path).read_text(encoding="ascii").strip()
                if limit_text == "max":
                    continue
                limit = int(limit_text)
                usage = int(Path(usage_path).read_text(encoding="ascii").strip())
            except (OSError, ValueError):
                continue

            # Cgroup v1 can report a very large sentinel for "unlimited".
            if 0 < limit < 2**60:
                return max(0, limit - usage)

        return None

    @staticmethod
    def _create_sentence_transformer():
        from sentence_transformers import SentenceTransformer

        try:
            return SentenceTransformer(
                "all-MiniLM-L6-v2",
                device="cpu",
                local_files_only=True,
            )
        except Exception as exc:
            logger.info("Cached SentenceTransformer unavailable (%s); trying model download.", exc)
            return SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    def _ensure_sentence_transformer(self) -> bool:
        if self._st_model is not None:
            return True

        with self._load_lock:
            if self._st_model is not None:
                return True
            if self._model_load_attempted:
                return False

            self._model_load_attempted = True
            self._loading = True
            try:
                available_memory = self._available_container_memory_bytes()
                if (
                    available_memory is not None
                    and available_memory < MODEL_MIN_AVAILABLE_MEMORY_BYTES
                ):
                    logger.info(
                        "Skipping SentenceTransformer: only %d bytes of container memory remain; "
                        "using TF-IDF/LSA.",
                        available_memory,
                    )
                    return False

                self._st_model = self._create_sentence_transformer()
                self._st_available = True
                logger.info("SentenceTransformer loaded on demand.")
            except Exception as exc:
                self._st_model = None
                self._st_available = False
                logger.warning(
                    "SentenceTransformer unavailable (%s). Using TF-IDF/LSA fallback.",
                    exc,
                )
            finally:
                self._loading = False

        return self._st_model is not None

    def _encode_in_batches(self, texts: List[str]) -> np.ndarray:
        import numpy as np

        model = self._st_model
        if model is None:
            raise RuntimeError("SentenceTransformer is not loaded.")

        output = None
        for start in range(0, len(texts), ENCODE_BATCH_SIZE):
            batch = texts[start : start + ENCODE_BATCH_SIZE]
            encoded = model.encode(
                batch,
                batch_size=ENCODE_BATCH_SIZE,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            encoded = np.asarray(encoded, dtype=np.float32)
            if output is None:
                output = np.empty((len(texts), encoded.shape[1]), dtype=np.float32)
            output[start : start + len(batch)] = encoded
            del encoded

        if output is None:
            return np.zeros((0, 64), dtype=np.float32)
        return output

    @staticmethod
    def _fallback_embeddings(texts: List[str]) -> np.ndarray:
        import numpy as np
        from sklearn.decomposition import TruncatedSVD
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import normalize

        clean_texts = [text.strip() if text and text.strip() else "research" for text in texts]
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

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Return L2-normalized embeddings, using bounded batches when possible."""
        import numpy as np

        if not texts:
            return np.zeros((0, 64), dtype=np.float32)

        # Serialize inference to bound peak memory under concurrent API requests.
        with self._inference_lock:
            if self._ensure_sentence_transformer():
                try:
                    return self._encode_in_batches(texts)
                except Exception as exc:
                    logger.warning(
                        "SentenceTransformer encoding failed (%s). Releasing it and using TF-IDF/LSA.",
                        exc,
                    )
                    self._st_model = None
                    self._st_available = False

            return self._fallback_embeddings(texts)

    def get_single_embedding(self, text: str) -> np.ndarray:
        """Generate an embedding for one text string."""
        return self.get_embeddings([text])[0]


# The shared engine is intentionally lightweight until the first analysis request.
embedding_engine = EmbeddingEngine()
