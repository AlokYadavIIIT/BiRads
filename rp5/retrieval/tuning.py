from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from rp5.config import RP5Config
from rp5.corpus.chunker import Chunker
from rp5.domain import CorpusDocument
from rp5.evaluation.metrics import ndcg_at_k, recall_at_k
from rp5.retrieval.embeddings import Embedder
from rp5.retrieval.index import Retriever


MODEL_DIMS = {
    "sentence-transformers/all-MiniLM-L6-v2": 384,
    "sentence-transformers/all-mpnet-base-v2": 768,
}


def load_judgments(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def tune(cfg: RP5Config, docs: list[CorpusDocument], judgments: list[dict]) -> dict:
    best = None
    for model_name in MODEL_DIMS:
        for size in (256, 512, 768, 1024):
            for overlap in (32, 64, 128):
                if overlap >= size:
                    continue
                for top_k in (4, 6, 8):
                    trial = replace(
                        cfg,
                        embedding_model=model_name,
                        embedding_dim=MODEL_DIMS[model_name],
                        chunk_size=size,
                        chunk_overlap=overlap,
                        top_k=top_k,
                        index_type="faiss",
                    )
                    chunks = Chunker(trial).chunk_all(docs)
                    retriever = Retriever(trial, embedder=Embedder(trial)).build(chunks)
                    ndcgs, recalls = [], []
                    for item in judgments:
                        ranked = retriever.retrieve(item["query"], k=top_k)
                        ids = [p.chunk.chunk_id for p in ranked]
                        rel = {x: 1 for x in item["relevant"]}
                        ndcgs.append(ndcg_at_k(ids, rel, top_k))
                        recalls.append(recall_at_k(ids, rel, top_k))
                    mean_ndcg = float(np.mean(ndcgs)) if ndcgs else 0.0
                    mean_recall = float(np.mean(recalls)) if recalls else 0.0
                    if mean_recall < cfg.recall_floor:
                        continue
                    score = mean_ndcg + 0.5 * mean_recall
                    candidate = {
                        "score": score,
                        "embedding_model": model_name,
                        "embedding_dim": MODEL_DIMS[model_name],
                        "chunk_size": size,
                        "overlap": overlap,
                        "top_k": top_k,
                        "ndcg": mean_ndcg,
                        "recall": mean_recall,
                    }
                    if best is None or candidate["score"] > best["score"]:
                        best = candidate
    return best or {"status": "no configuration met recall floor", "recall_floor": cfg.recall_floor}
