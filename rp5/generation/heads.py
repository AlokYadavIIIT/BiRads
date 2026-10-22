from __future__ import annotations

import json
import math
import re
import time
from typing import Any

from rp5.config import RP5Config
from rp5.domain import FindingCard, Passage
from rp5.evaluation.readability import flesch_kincaid
from rp5.generation.llm_backend import LLMBackend
from rp5.generation.prompts import CLINICIAN_SCHEMA, make_clinician_messages, make_patient_messages

_JSON_RE = re.compile(r"\{.*\}", re.S)


class ClinicianHead:
    def __init__(self, backend: LLMBackend, cfg: RP5Config):
        self.backend = backend
        self.cfg = cfg

    def generate(
        self,
        card: FindingCard,
        passages: list[Passage],
        examples: list[Passage] | None,
        temperature: float,
        seed: int,
    ) -> tuple[dict[str, Any] | None, float, float]:
        t0 = time.perf_counter()
        messages = make_clinician_messages(
            card,
            passages,
            examples=examples,
            include_reference_label=self.cfg.reference_label_in_prompt,
        )
        text, logprobs = self.backend.generate(
            messages,
            temperature=temperature,
            max_tokens=self.cfg.max_tokens_clin,
            seed=seed,
        )
        draft = self._parse_and_validate(text)
        if draft is None:
            repair = messages + [
                {
                    "role": "user",
                    "content": "Return ONLY one valid JSON object. No markdown, no explanation.",
                }
            ]
            text, logprobs = self.backend.generate(
                repair,
                temperature=temperature,
                max_tokens=self.cfg.max_tokens_clin,
                seed=seed + 1,
            )
            draft = self._parse_and_validate(text)
        elapsed = time.perf_counter() - t0
        confidence = self._token_confidence(logprobs)
        return draft, confidence, elapsed

    @staticmethod
    def _parse_and_validate(text: str) -> dict[str, Any] | None:
        match = _JSON_RE.search(text or "")
        if not match:
            return None
        try:
            obj = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        required = {"view", "lesions", "findings", "final_assessment"}
        if not required.issubset(obj):
            return None
        try:
            category = int(obj["final_assessment"])
        except Exception:
            return None
        if not 0 <= category <= 6:
            return None
        if not isinstance(obj["lesions"], list) or not isinstance(obj["findings"], str):
            return None
        for lesion in obj["lesions"]:
            if not isinstance(lesion, dict) or "kind" not in lesion or "location" not in lesion:
                return None
            lesion.setdefault("size_mm", None)
            lesion.setdefault("descriptors", [])
        obj.setdefault("breast_density", None)
        obj.setdefault("recommendation", None)
        return obj

    @staticmethod
    def _token_confidence(logprobs: list[float] | None) -> float:
        if not logprobs:
            return 0.5

        mean_lp = sum(logprobs) / len(logprobs)

        # Convert mean log-probability back to probability.
        # exp(mean(log p)) is the geometric mean token probability.
        mean_lp = max(-30.0, min(0.0, mean_lp))

        return float(math.exp(mean_lp))


import logging

logger = logging.getLogger("rp5.generation.heads")

FALLBACK_ERROR_MESSAGE = (
    "Explanation unavailable: We could not generate a patient explanation from the available report draft."
)


class PatientHead:
    def __init__(self, backend: LLMBackend, cfg: RP5Config):
        self.backend = backend
        self.cfg = cfg

    def generate(
        self,
        draft: dict[str, Any],
        passages: list[Passage],
        temperature: float,
        seed: int,
    ) -> tuple[str, Optional[float], bool]:
        # Stage 1: Input validation
        if not draft or not isinstance(draft, dict) or "final_assessment" not in draft:
            logger.error(
                "Patient explanation generation failed: missing or malformed clinician draft",
                extra={"stage": "input_validation", "error_category": "missing_or_malformed_draft"},
            )
            return FALLBACK_ERROR_MESSAGE, None, False

        messages = make_patient_messages(draft, passages)

        # Stage 2: Initial generation with safe exception handling
        try:
            text, _ = self.backend.generate(
                messages,
                temperature=temperature,
                max_tokens=self.cfg.max_tokens_pat,
                seed=seed,
            )
        except Exception as exc:
            logger.error(
                "Patient explanation LLM generation failed: %s",
                type(exc).__name__,
                extra={"stage": "llm_generation", "exception_type": type(exc).__name__},
            )
            return FALLBACK_ERROR_MESSAGE, None, False

        # Stage 3: Schema validation on generated text
        if not self._is_valid_patient_text(text):
            logger.error(
                "Patient explanation output validation failed: empty or malformed output",
                extra={"stage": "output_validation", "error_category": "malformed_or_empty_output"},
            )
            return FALLBACK_ERROR_MESSAGE, None, False

        # Stage 4: Readability calculation on valid explanation
        grade = flesch_kincaid(text)
        regenerated = False

        for retry in range(self.cfg.readability_max_regens):
            if grade <= self.cfg.fk_grade_target:
                break
            regenerated = True
            retry_messages = [m.copy() for m in messages]
            retry_messages[-1]["content"] += (
                f"\nRewrite more simply. Target Flesch-Kincaid <= {self.cfg.fk_grade_target:.0f}."
            )
            try:
                regen_text, _ = self.backend.generate(
                    retry_messages,
                    temperature=temperature,
                    max_tokens=self.cfg.max_tokens_pat,
                    seed=seed + 10 + retry,
                )
                if self._is_valid_patient_text(regen_text):
                    text = regen_text
                    grade = flesch_kincaid(text)
            except Exception as exc:
                logger.warning(
                    "Patient explanation readability regeneration failed: %s",
                    type(exc).__name__,
                    extra={"stage": "readability_regeneration", "exception_type": type(exc).__name__},
                )
                break

        return text, grade, regenerated

    @staticmethod
    def _is_valid_patient_text(text: Any) -> bool:
        if not text or not isinstance(text, str):
            return False
        cleaned = text.strip()
        if len(cleaned) < 15:
            return False
        # Reject raw JSON, schema outputs, or known generic fallback messages
        if cleaned.startswith("{") and cleaned.endswith("}"):
            return False
        if cleaned == "Your report could not be explained from the available draft.":
            return False
        if cleaned == FALLBACK_ERROR_MESSAGE:
            return False
        return True
