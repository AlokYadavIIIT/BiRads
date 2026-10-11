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
    ) -> tuple[str, float, bool]:
        messages = make_patient_messages(draft, passages)
        text, _ = self.backend.generate(
            messages,
            temperature=temperature,
            max_tokens=self.cfg.max_tokens_pat,
            seed=seed,
        )
        grade = flesch_kincaid(text)
        regenerated = False
        for retry in range(self.cfg.readability_max_regens):
            if grade <= self.cfg.fk_grade_target:
                break
            regenerated = True
            messages[-1]["content"] += (
                f"\nRewrite more simply. Target Flesch-Kincaid <= {self.cfg.fk_grade_target:.0f}."
            )
            text, _ = self.backend.generate(
                messages,
                temperature=temperature,
                max_tokens=self.cfg.max_tokens_pat,
                seed=seed + 10 + retry,
            )
            grade = flesch_kincaid(text)
        return text, grade, regenerated
