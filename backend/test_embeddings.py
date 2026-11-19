import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import numpy as np

from app.nlp.embeddings import EmbeddingEngine, MODEL_MIN_AVAILABLE_MEMORY_BYTES


class StubSentenceTransformer:
    def __init__(self):
        self.batch_lengths = []

    def encode(self, texts, **kwargs):
        self.batch_lengths.append(len(texts))
        return np.ones((len(texts), 384), dtype=np.float32)


class EmbeddingEngineTests(unittest.TestCase):
    def test_engine_does_not_load_transformer_during_initialization(self):
        with patch.object(EmbeddingEngine, "_create_sentence_transformer") as create_model:
            engine = EmbeddingEngine()

        create_model.assert_not_called()
        self.assertFalse(engine.model_loading)
        self.assertFalse(engine._model_load_attempted)

    def test_low_memory_uses_lsa_without_importing_transformer(self):
        engine = EmbeddingEngine()
        engine._available_container_memory_bytes = lambda: 512 * 1024 * 1024

        with patch.object(engine, "_create_sentence_transformer") as create_model:
            embeddings = engine.get_embeddings(
                ["neural network MRI imaging", "transformer MRI analysis"]
            )

        create_model.assert_not_called()
        self.assertEqual(embeddings.shape[0], 2)
        self.assertTrue(np.isfinite(embeddings).all())
        self.assertFalse(engine._st_available)

    def test_concurrent_requests_initialize_only_one_model(self):
        engine = EmbeddingEngine()
        engine._available_container_memory_bytes = (
            lambda: MODEL_MIN_AVAILABLE_MEMORY_BYTES * 2
        )
        model = StubSentenceTransformer()

        def create_model():
            time.sleep(0.02)
            return model

        with patch.object(
            engine, "_create_sentence_transformer", side_effect=create_model
        ) as create:
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(lambda _: engine._ensure_sentence_transformer(), range(4)))

        self.assertEqual(create.call_count, 1)
        self.assertTrue(all(results))
        self.assertIs(engine._st_model, model)

    def test_transformer_encoding_uses_bounded_batches(self):
        engine = EmbeddingEngine()
        engine._available_container_memory_bytes = (
            lambda: MODEL_MIN_AVAILABLE_MEMORY_BYTES * 2
        )
        model = StubSentenceTransformer()

        with patch.object(engine, "_create_sentence_transformer", return_value=model):
            embeddings = engine.get_embeddings([f"research paper {i}" for i in range(19)])

        self.assertEqual(model.batch_lengths, [8, 8, 3])
        self.assertEqual(embeddings.shape, (19, 384))
        self.assertEqual(embeddings.dtype, np.float32)

    def test_model_load_failure_falls_back_and_is_not_retried(self):
        engine = EmbeddingEngine()
        engine._available_container_memory_bytes = (
            lambda: MODEL_MIN_AVAILABLE_MEMORY_BYTES * 2
        )

        with patch.object(
            engine,
            "_create_sentence_transformer",
            side_effect=ImportError("model unavailable"),
        ) as create_model:
            first = engine.get_embeddings(
                ["neural network MRI imaging", "transformer MRI analysis"]
            )
            second = engine.get_embeddings(
                ["neural network MRI imaging", "transformer MRI analysis"]
            )

        self.assertEqual(create_model.call_count, 1)
        self.assertEqual(first.shape[0], 2)
        self.assertEqual(second.shape[0], 2)
        self.assertFalse(engine._st_available)


if __name__ == "__main__":
    unittest.main()
