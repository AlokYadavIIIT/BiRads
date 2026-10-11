from __future__ import annotations

import time
from typing import Any

from rp5.attribution.aligner import Aligner, coverage, split_sentences
from rp5.config import RP5Config
from rp5.domain import Abstention, DraftResult, FindingCard, Passage
from rp5.generation.heads import ClinicianHead, PatientHead
from rp5.generation.llm_backend import DummyBackend, LLMBackend, LlamaCppBackend
from rp5.guard.guard_agent import GuardAgent
from rp5.retrieval.index import Retriever, load_chunks


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
        temperature = self.cfg.temperature if temperature is None else temperature
        seed = self.cfg.seed if seed is None else seed
        started = time.perf_counter()

        query = card.serialize(self.cfg.reference_label_in_prompt)
        retrieval_start = time.perf_counter()
        passages = self.retriever.retrieve(query, self.cfg.top_k)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        examples = self.retriever.metadata_retrieve(query, "S4", self.cfg.few_shot_k)
        self.last_examples = examples

        if perturb and passages:
            # F3: keep a relevant passage, but move distractors ahead of it.

            # Retrieve a larger candidate set using the ORIGINAL query.
            candidate_passages = self.retriever.retrieve(
                query,
                self.cfg.top_k * 3,
            )

            # Collect descriptors from the finding card.
            descriptors = []
            for lesion in card.lesions:
                descriptors.extend(lesion.descriptors or [])

            # Find a relevant S1 lexicon passage.
            correct_passage = None

            for p in candidate_passages:
                text = p.chunk.text.lower()

                if p.chunk.stratum == "S1" and any(
                    descriptor.lower() in text
                    for descriptor in descriptors
                ):
                    correct_passage = p
                    break

            # If the correct evidence cannot be found, F3 cannot be performed.
            if correct_passage is None:
                return Abstention(
                    card.case_id,
                    "low_confidence",
                    ["F3 correct evidence passage not found"],
                )

            # Select competing passages, excluding the correct evidence.
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
                )

            # Distractors first, correct evidence last.
            passages = distractors + [correct_passage]

        self.last_passages = passages
        if not passages:
            return Abstention(card.case_id, "low_confidence", ["no retrieval passages found"])

        draft, model_confidence, clinician_ms = self.clinician.generate(
            card, passages, examples, temperature, seed
        )
        if draft is None:
            return Abstention(card.case_id, "parse_failure", ["clinician head did not return valid JSON"])

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
            return guard

        clinician_text = self._render_clinician_text(draft)
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
            confidence=round(0.6 * model_confidence + 0.4 * max(p.score for p in passages), 4),
            retrieval_scores=[p.score for p in passages],
            latency_ms={
                "retrieval_ms": retrieval_ms,
                "clinician_ms": clinician_ms * 1000,
                "patient_ms": patient_ms,
                "attribution_ms": attribution_ms,
                "guard_ms": guard_ms,
                "total_ms": (time.perf_counter() - started) * 1000,
            },
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
        # stable de-duplication
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
