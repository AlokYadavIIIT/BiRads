from __future__ import annotations

import hashlib
import numpy as np

from rp5.config import RP5Config


class Embedder:
    """Sentence-transformers embeddings with a deterministic fallback for tests."""

    def __init__(self, cfg: RP5Config):
        self.cfg = cfg
        self._model = None
        self._cache: dict[str, np.ndarray] = {}

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.cfg.embedding_model)

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.cfg.embedding_dim), dtype=np.float32)

        results: list[np.ndarray | None] = [None] * len(texts)
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        for i, text in enumerate(texts):
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if h in self._cache:
                results[i] = self._cache[h]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        if uncached_texts:
            try:
                self._load()
                computed = self._model.encode(
                    uncached_texts,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                ).astype(np.float32)
            except Exception:
                computed = DummyEmbedder(self.cfg).encode(uncached_texts)

            for idx, text, vec in zip(uncached_indices, uncached_texts, computed):
                h = hashlib.sha256(text.encode("utf-8")).hexdigest()
                self._cache[h] = vec
                results[idx] = vec

        return np.vstack([r for r in results if r is not None]).astype(np.float32)


class DummyEmbedder:
    def __init__(self, cfg: RP5Config):
        self.cfg = cfg

    def encode(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.cfg.embedding_dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for token in text.lower().split():
                h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
                out[i, h % self.cfg.embedding_dim] += 1.0
            norm = np.linalg.norm(out[i])
            if norm:
                out[i] /= norm
        return out
