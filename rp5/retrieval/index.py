from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rp5.config import RP5Config
from rp5.domain import Chunk, Passage
from rp5.retrieval.embeddings import Embedder


def load_chunks(path: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                d = json.loads(line)
                chunks.append(Chunk(**d))
    return chunks


class Retriever:
    def __init__(self, cfg: RP5Config, chunks: list[Chunk] | None = None, embedder: Embedder | None = None):
        self.cfg = cfg
        self.embedder = embedder or Embedder(cfg)
        self.chunks = chunks or []
        self._index = None
        self._vectors: np.ndarray | None = None

    def build(self, chunks: list[Chunk]) -> "Retriever":
        self.chunks = chunks
        if not chunks:
            self._index = None
            self._vectors = None
            return self
        vectors = self.embedder.encode([c.text for c in chunks]).astype(np.float32)
        self._vectors = vectors
        if self.cfg.index_type == "faiss":
            try:
                import faiss
                self._index = faiss.IndexFlatIP(vectors.shape[1])
                self._index.add(vectors)
                return self
            except Exception:
                # Transparent fallback keeps the CPU prototype runnable.
                self._index = None
        return self

    def retrieve(self, query: str, k: int | None = None) -> list[Passage]:
        k = min(k or self.cfg.top_k, len(self.chunks))
        if k <= 0 or not self.chunks:
            return []
        q = self.embedder.encode([query]).astype(np.float32)
        if self._index is not None:
            scores, idx = self._index.search(q, k)
            return [Passage(self.chunks[j], float(s)) for s, j in zip(scores[0], idx[0]) if j >= 0]
        assert self._vectors is not None
        scores = (self._vectors @ q[0]).astype(float)
        idx = np.argsort(-scores)[:k]
        return [Passage(self.chunks[int(j)], float(scores[int(j)])) for j in idx]

    def metadata_retrieve(self, query: str, stratum: str, k: int | None = None) -> list[Passage]:
        filtered = [c for c in self.chunks if c.stratum == stratum]
        if not filtered:
            return []
        tmp = Retriever(self.cfg, embedder=self.embedder).build(filtered)
        return tmp.retrieve(query, k or self.cfg.top_k)
