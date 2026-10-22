from __future__ import annotations

import re
from typing import Any, Iterable

from rp5.config import RP5Config
from rp5.domain import Attribution, Passage
from rp5.normalization import extract_measurement
from rp5.retrieval.embeddings import Embedder

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_STOP = {
    "the", "a", "an", "of", "in", "on", "at", "to", "and", "or", "with",
    "is", "are", "was", "were", "be", "this", "that", "for", "as", "by",
}
_NEGATION_TERMS = {
    "no", "not", "without", "absence of", "ruled out", "denies", "free of",
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
        claims = [c.strip() for c in claims if c and c.strip()]
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

                method = "lexical" if lexical > embedding else "embedding"
                if self.cfg.use_nli:
                    nli_score = self._nli_score(claim, ev)
                    if nli_score is not None and nli_score > max(lexical, embedding):
                        method = "nli"

                status, reason = self._evaluate_clinical_support(
                    claim=claim,
                    passage=ev,
                    passage_id=evidence_ids[j],
                    stratum=evidence_strata[j],
                    lexical=lexical,
                    embedding=embedding,
                )

                # Composite calibrated score
                if status == "supported":
                    calibrated_score = max(lexical, embedding)
                elif status == "uncertain":
                    calibrated_score = round(0.4 * lexical + 0.6 * embedding, 4)
                else:
                    calibrated_score = min(lexical, embedding)

                candidates.append(
                    Attribution(
                        span=claim,
                        passage_id=evidence_ids[j],
                        stratum=evidence_strata[j],
                        score=round(calibrated_score, 4),
                        method=method,
                        supported=(status == "supported"),
                        passage_text=ev[:240],
                        lexical_score=round(lexical, 4),
                        semantic_score=round(embedding, 4),
                        status=status,
                        decision_reason=reason,
                    )
                )

            # Rank: supported > uncertain > unsupported, then by score descending
            status_priority = {"supported": 2, "uncertain": 1, "unsupported": 0}
            candidates.sort(
                key=lambda x: (status_priority.get(x.status, 0), x.score),
                reverse=True,
            )
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

    def _evaluate_clinical_support(
        self,
        claim: str,
        passage: str,
        passage_id: str,
        stratum: str,
        lexical: float,
        embedding: float,
    ) -> tuple[str, str]:
        """
        Multi-signal attribution policy distinguishing lexical overlap from semantic support,
        detecting negation, laterality, and measurement conflicts.
        Returns (status: 'supported' | 'unsupported' | 'uncertain', reason: str).
        """
        claim_lower = claim.lower()
        passage_lower = passage.lower()

        # 1. Clinical Negation conflict check (absence vs presence of findings)
        clinical_neg_patterns = [
            r"\b(?:no|without|absence of|negative for|free of|ruled out)\s+(?:focal\s+)?(?:mass|lesion|calcification|asymmetry|malignancy|abnormality)",
        ]
        claim_has_clinical_neg = any(re.search(p, claim_lower) for p in clinical_neg_patterns)
        passage_has_clinical_neg = any(re.search(p, passage_lower) for p in clinical_neg_patterns)

        if claim_has_clinical_neg != passage_has_clinical_neg and (claim_has_clinical_neg or passage_has_clinical_neg):
            findings_vocab = {"mass", "calcification", "asymmetry", "distortion", "lesion", "malignancy"}
            claim_tokens = set(re.findall(r"[a-z0-9-]+", claim_lower))
            pass_tokens = set(re.findall(r"[a-z0-9-]+", passage_lower))
            if findings_vocab.intersection(claim_tokens).intersection(pass_tokens):
                return "unsupported", "negation_contradiction"

        # 2. Measurement mismatch check
        claim_meas, _ = extract_measurement(claim)
        passage_meas, _ = extract_measurement(passage)
        if claim_meas is not None and passage_meas is not None:
            if abs(claim_meas - passage_meas) > 0.5:
                return "unsupported", f"measurement_mismatch ({claim_meas:.1f}mm vs {passage_meas:.1f}mm)"

        # 3. Laterality mismatch check
        claim_has_left = bool(re.search(r"\bleft\b", claim_lower))
        claim_has_right = bool(re.search(r"\bright\b", claim_lower))
        pass_has_left = bool(re.search(r"\bleft\b", passage_lower))
        pass_has_right = bool(re.search(r"\bright\b", passage_lower))

        if (claim_has_left and not claim_has_right and pass_has_right and not pass_has_left) or (
            claim_has_right and not claim_has_left and pass_has_left and not pass_has_right
        ):
            return "unsupported", "laterality_mismatch"

        # 4. Finding card grounding (primary patient record)
        if stratum == "card" or passage_id == "<<finding_card>>":
            if "recommendation:" in claim_lower and "screening" in claim_lower and "screening" in passage_lower:
                return "supported", "finding_card_grounded"
            if lexical >= 0.60:
                return "supported", "finding_card_grounded"
            if lexical >= 0.35 and embedding >= 0.35:
                return "supported", "finding_card_partial_match"
            if lexical < 0.20:
                return "unsupported", "absent_from_finding_card"
            return "uncertain", "partial_card_match_requires_review"

        # 5. S1 Lexicon descriptor support
        if stratum == "S1" and "descriptor:" in claim_lower:
            descriptor = claim_lower.split("descriptor:", 1)[1].strip()
            if descriptor and descriptor in passage_lower:
                return "supported", "bi_rads_lexicon_descriptor_supported"

        # 6. S1 / S2 Assessment guidance support
        if "final assessment:" in claim_lower:
            if "bi-rads category" in passage_lower or "assessment" in passage_lower:
                # check matching category
                cat_match = re.search(r"bi-rads\s+(\d)", claim_lower)
                if cat_match and cat_match.group(1) in passage_lower:
                    return "supported", "bi_rads_guidance_supported"

        # Recommendation guidance support
        if "recommendation:" in claim_lower:
            rec_text = claim_lower.split("recommendation:", 1)[1].strip()
            words = [w for w in rec_text.split() if len(w) > 3 and w not in _STOP]
            if words and any(w in passage_lower for w in words):
                if lexical >= 0.30 or embedding >= 0.35:
                    return "supported", "bi_rads_recommendation_guidance_supported"

        # 7. Semantic & lexical aggregation for reference passages
        # High lexical with low semantic (e.g. superficial word overlap without semantic support)
        if lexical >= 0.70 and embedding < 0.40:
            return "uncertain", "lexical_overlap_without_semantic_support"

        # Strong agreement across both modalities
        if lexical >= 0.40 and embedding >= 0.60:
            return "supported", "strong_semantic_and_lexical_alignment"

        # Strong semantic support (paraphrase)
        if embedding >= 0.65:
            return "supported", "high_semantic_similarity"

        # Borderline / uncertain similarity
        if embedding >= self.cfg.support_threshold or (lexical >= 0.50 and embedding >= 0.35):
            return "uncertain", "borderline_support_requires_review"

        return "unsupported", "insufficient_evidence_support"


def coverage(attribution_map: dict[str, list[Attribution]]) -> float:
    """
    Claim-Support Citation Coverage.
    Measures the fraction of claims that have at least one verified supporting evidence source.
    Does NOT measure diagnostic completeness or cancer risk.
    """
    if not attribution_map:
        return 0.0
    supported_claims = sum(
        1 for attrs in attribution_map.values() if attrs and attrs[0].supported
    )
    return supported_claims / len(attribution_map)
