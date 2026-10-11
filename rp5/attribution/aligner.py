from __future__ import annotations

import re
from typing import Iterable

from rp5.config import RP5Config
from rp5.domain import Attribution, Passage
from rp5.retrieval.embeddings import Embedder

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_STOP = {
    "the", "a", "an", "of", "in", "on", "at", "to", "and", "or", "with",
    "is", "are", "was", "were", "be", "this", "that", "for", "as", "by",
}


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text or "") if len(s.strip()) > 2]


class Aligner:
    def __init__(self, cfg: RP5Config, embedder: Embedder | None = None):
        self.cfg = cfg
        self.embedder = embedder or Embedder(cfg)
        self._nli = None

    def align(
        self,
        claims: Iterable[str],
        passages: list[Passage],
        card_text: str,
    ) -> dict[str, list[Attribution]]:
        claims = list(claims)
        if not claims:
            return {}
        evidence_text = [p.chunk.text for p in passages] + [card_text]
        evidence_ids = [p.chunk.chunk_id for p in passages] + ["<<finding_card>>"]
        evidence_strata = [p.chunk.stratum for p in passages] + ["card"]
        evidence_vectors = self.embedder.encode(evidence_text)
        claim_vectors = self.embedder.encode(claims)
        sims = claim_vectors @ evidence_vectors.T if len(evidence_vectors) else None
        result: dict[str, list[Attribution]] = {}

        for i, claim in enumerate(claims):
            candidates: list[Attribution] = []
            for j, ev in enumerate(evidence_text):
                lexical = self._lexical_score(claim, ev)
                embedding = float(sims[i, j]) if sims is not None else 0.0
                score = max(lexical, embedding)
                method = "lexical" if lexical >= embedding else "embedding"
                if self.cfg.use_nli:
                    nli_score = self._nli_score(claim, ev)
                    if nli_score is not None and nli_score > score:
                        score, method = nli_score, "nli"
                candidates.append(
                    Attribution(
                        span=claim,
                        passage_id=evidence_ids[j],
                        stratum=evidence_strata[j],
                        score=score,
                        method=method,
                        supported=score >= self.cfg.support_threshold,
                    )
                )
            candidates.sort(key=lambda x: x.score, reverse=True)
            result[claim] = candidates[:3]
        return result

    @staticmethod
    def _lexical_score(claim: str, passage: str) -> float:
        tokenize = lambda text: {
            x for x in re.findall(r"[a-z0-9-]+", text.lower()) if x not in _STOP
        }
        left, right = tokenize(claim), tokenize(passage)
        if not left or not right:
            return 0.0
        return len(left & right) / len(left)

    def _nli_score(self, claim: str, passage: str) -> float | None:
        try:
            if self._nli is None:
                from transformers import pipeline
                self._nli = pipeline("text-classification", model="cross-encoder/nli-deberta-v3-xsmall")
            result = self._nli({"text": passage, "text_pair": claim})[0]
            label = str(result["label"]).lower()
            return float(result["score"]) if "entail" in label else 1.0 - float(result["score"])
        except Exception:
            return None


def coverage(attribution_map: dict[str, list[Attribution]]) -> float:
    if not attribution_map:
        return 0.0
    return sum(1 for attrs in attribution_map.values() if attrs and attrs[0].supported) / len(attribution_map)
