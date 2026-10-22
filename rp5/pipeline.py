from __future__ import annotations

import time
from typing import Any

from rp5.attribution.aligner import Aligner, coverage, split_sentences
from rp5.config import RP5Config
from rp5.domain import Abstention, DraftResult, FindingCard, Passage
from rp5.generation.heads import ClinicianHead, PatientHead
from rp5.generation.llm_backend import DummyBackend, LLMBackend, LlamaCppBackend
from rp5.guard.guard_agent import GuardAgent
from rp5.normalization import normalize_finding_card
from rp5.retrieval.index import Retriever, load_chunks

METRICS_EXPLANATION = {
    "coverage": (
        "Claim-Support Citation Coverage: Proportion of extracted draft claims with verified evidence support "
        "(numerator: supported claims, denominator: total claims). Does not measure diagnostic completeness or cancer risk."
    ),
    "confidence": (
        "Internal Composite Confidence: Heuristic decision-support score (0.0 to 1.0) derived from generation token "
        "log-probabilities (weight 0.6) and top retrieval relevance (weight 0.4). Does not represent cancer probability."
    ),
}


class RAGPipeline:
    def __init__(self, cfg: RP5Config, backend: LLMBackend | None = None, retriever: Retriever | None = None):
        self.cfg = cfg
        self.backend = backend or DummyBackend()
        self.retriever = retriever or Retriever(cfg)
        self.clinician = ClinicianHead(self.backend, cfg)
        self.patient = PatientHead(self.backend, cfg)
        self.aligner = Aligner(cfg)
        self.guard = GuardAgent(cfg, backend=self.backend)
        self.last_passages: list[Passage] = []
        self.last_examples: list[Passage] = []

    def load_corpus(self, corpus_path=None) -> "RAGPipeline":
        path = corpus_path or self.cfg.corpus_path
        chunks = load_chunks(path)
        self.retriever.build(chunks)
        return self

    def answer(
        self,
        card: FindingCard,
        temperature: float | None = None,
        seed: int | None = None,
        perturb: bool = False,
    ) -> DraftResult | Abstention:
        total_started = time.perf_counter()
        temperature = self.cfg.temperature if temperature is None else temperature
        seed = self.cfg.seed if seed is None else seed

        # Stage 0: Finding card normalization
        card, card_warnings = normalize_finding_card(card)
        assessment_provenance = (
            "source_explicit" if card.birads is not None else "model_proposed"
        )

        query = card.serialize(self.cfg.reference_label_in_prompt)
        retrieval_start = time.perf_counter()
        passages = self.retriever.retrieve(query, self.cfg.top_k)
        examples = self.retriever.metadata_retrieve(query, "S4", self.cfg.few_shot_k)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        self.last_examples = examples

        if perturb and passages:
            # F3: keep a relevant passage, but move distractors ahead of it.
            candidate_passages = self.retriever.retrieve(
                query,
                self.cfg.top_k * 3,
            )

            descriptors = []
            for lesion in card.lesions:
                descriptors.extend(lesion.descriptors or [])

            correct_passage = None
            for p in candidate_passages:
                text = p.chunk.text.lower()
                if p.chunk.stratum == "S1" and any(
                    descriptor.lower() in text for descriptor in descriptors
                ):
                    correct_passage = p
                    break

            if correct_passage is None:
                return Abstention(
                    card.case_id,
                    "low_confidence",
                    ["F3 correct evidence passage not found"],
                    validation_warnings=card_warnings,
                )

            distractors = [
                p for p in candidate_passages
                if p.chunk.chunk_id != correct_passage.chunk.chunk_id
                and not any(
                    descriptor.lower() in p.chunk.text.lower()
                    for descriptor in descriptors
                )
            ]
            distractors = distractors[: self.cfg.top_k - 1]

            if len(distractors) < self.cfg.top_k - 1:
                return Abstention(
                    card.case_id,
                    "low_confidence",
                    ["F3 insufficient distractor passages available"],
                    validation_warnings=card_warnings,
                )

            passages = distractors + [correct_passage]

        self.last_passages = passages
        if not passages:
            return Abstention(
                card.case_id,
                "low_confidence",
                ["no retrieval passages found"],
                validation_warnings=card_warnings,
            )

        clinician_start = time.perf_counter()
        draft, model_confidence, _ = self.clinician.generate(
            card, passages, examples, temperature, seed
        )
        clinician_ms = (time.perf_counter() - clinician_start) * 1000

        if draft is None:
            return Abstention(
                card.case_id,
                "parse_failure",
                ["clinician head did not return valid JSON"],
                validation_warnings=card_warnings,
            )

        patient_start = time.perf_counter()
        patient_text, fk_grade, regenerated = self.patient.generate(draft, passages, temperature, seed)
        patient_ms = (time.perf_counter() - patient_start) * 1000

        claims = self._claim_spans(draft)
        attribution_start = time.perf_counter()
        card_text = card.serialize(include_reference_label=False)
        clinician_attr = self.aligner.align(claims, passages, card_text)
        patient_attr = self.aligner.align(split_sentences(patient_text), passages, card_text)
        attribution_ms = (time.perf_counter() - attribution_start) * 1000
        cov = coverage(clinician_attr)

        guard_start = time.perf_counter()
        guard = self.guard.evaluate(
            draft=draft,
            card=card,
            passages=passages,
            attribution_map=clinician_attr,
            patient_text=patient_text,
            patient_fk_grade=fk_grade,
            retrieval_scores=[p.score for p in passages],
            confidence=model_confidence,
        )
        guard_ms = (time.perf_counter() - guard_start) * 1000
        if guard is not None:
            guard.validation_warnings.extend(card_warnings)
            return guard

        all_warnings = list(card_warnings)
        all_warnings.extend(self.guard.last_warnings)

        requires_review = (
            assessment_provenance == "model_proposed"
            or self.guard.requires_review
            or bool(all_warnings)
            or fk_grade is None
        )

        patient_generation_status = "success" if fk_grade is not None else "failed"

        composite_confidence = (
            round(0.6 * model_confidence + 0.4 * max(p.score for p in passages), 4)
            if passages
            else None
        )

        clinician_text = self._render_clinician_text(draft)
        total_ms = (time.perf_counter() - total_started) * 1000

        return DraftResult(
            case_id=card.case_id,
            clinician_draft=draft,
            clinician_text=clinician_text,
            patient_text=patient_text,
            patient_fk_grade=fk_grade,
            patient_regen=regenerated,
            attribution_map=clinician_attr,
            patient_attribution_map=patient_attr,
            coverage=cov,
            confidence=composite_confidence,
            retrieval_scores=[p.score for p in passages],
            latency_ms={
                "retrieval_ms": retrieval_ms,
                "clinician_ms": clinician_ms,
                "patient_ms": patient_ms,
                "attribution_ms": attribution_ms,
                "guard_ms": guard_ms,
                "total_ms": total_ms,
            },
            patient_generation_status=patient_generation_status,
            assessment_provenance=assessment_provenance,
            requires_clinician_review=requires_review,
            validation_warnings=all_warnings,
            metrics_explanation=METRICS_EXPLANATION,
        )

    @staticmethod
    def _claim_spans(draft: dict[str, Any]) -> list[str]:
        claims = split_sentences(draft.get("findings", ""))
        if not claims:
            claims = [f"{x.get('kind')} at {x.get('location')}" for x in draft.get("lesions", [])]
        claims.append(f"Final assessment: BI-RADS {draft.get('final_assessment')}")
        recommendation = draft.get("recommendation")
        if recommendation:
            claims.append(f"Recommendation: {recommendation}")
        for lesion in draft.get("lesions", []):
            for descriptor in lesion.get("descriptors", []) or []:
                claims.append(f"Descriptor: {descriptor}")
        return list(dict.fromkeys(c for c in claims if c and c.strip()))

    @staticmethod
    def _render_clinician_text(draft: dict[str, Any]) -> str:
        findings = draft.get("findings", "").strip()
        category = draft.get("final_assessment")
        recommendation = (draft.get("recommendation") or "").strip()
        parts = [findings, f"Final assessment: BI-RADS {category}."]
        if recommendation:
            parts.append(f"Recommendation: {recommendation}")
        return " ".join(x for x in parts if x)

    @staticmethod
    def from_gguf(cfg: RP5Config, model_path: str | None = None) -> "RAGPipeline":
        model = model_path or cfg.generator_model
        pipe = RAGPipeline(cfg, backend=LlamaCppBackend(model, n_ctx=cfg.n_ctx))
        return pipe.load_corpus()
