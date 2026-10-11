from __future__ import annotations

import hashlib
import numpy as np

from rp5.config import RP5Config


class Embedder:
    """Sentence-transformers embeddings with a deterministic fallback for tests."""

    def __init__(self, cfg: RP5Config):
        self.cfg = cfg
        self._model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.cfg.embedding_model)

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.cfg.embedding_dim), dtype=np.float32)
        try:
            self._load()
            arr = self._model.encode(
                texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            ).astype(np.float32)
            return arr
        except Exception:
            return DummyEmbedder(self.cfg).encode(texts)


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
