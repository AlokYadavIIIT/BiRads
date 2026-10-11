from __future__ import annotations

import json
import re
import time
from typing import Optional

from rp5.domain import FindingCard, Lesion


REC_BY_CATEGORY = {
    0: "Additional imaging evaluation is needed.",
    1: "Routine screening.",
    2: "Routine screening.",
    3: "Short-interval follow-up.",
    4: "Biopsy should be considered.",
    5: "Biopsy is strongly advised.",
    6: "Management of known malignancy.",
}


class LLMBackend:
    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
        seed: int = 0,
    ) -> tuple[str, Optional[list[float]]]:
        raise NotImplementedError


class LlamaCppBackend(LLMBackend):
    def __init__(self, model_path: str, n_ctx: int = 4096):
        from llama_cpp import Llama

        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=0,
            logits_all=True,
            verbose=False,
        )

    def generate(self, messages, temperature=0.2, max_tokens=512, seed=0):
        result = self.llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            seed=seed,
            logprobs=True,
            top_logprobs=5,
        )

        choice = result["choices"][0]
        text = choice["message"]["content"]

        logprobs = None

        lp = choice.get("logprobs")

        if isinstance(lp, dict):
            content = lp.get("content")

            if content:
                logprobs = [
                    float(item["logprob"])
                    for item in content
                    if item.get("logprob") is not None
                ]

        return text, logprobs


class DummyBackend(LLMBackend):
    """Deterministic smoke-test backend; never use it for reported experiments."""

    def generate(self, messages, temperature=0.2, max_tokens=512, seed=0):
        joined = "\n".join(m.get("content", "") for m in messages)
        if "Return exactly one token: CONSISTENT or CONTRADICTION" in joined:
            return self._self_check(joined), [0.0]
        if "patient-communication assistant" in joined.lower():
            draft = self._extract_json(joined)
            return self._patient(draft), None
        card = self._extract_card(joined)
        return self._clinician(card), None

    @staticmethod
    def _extract_json(text: str) -> dict:
        matches = re.findall(r"\{.*\}", text, re.S)
        for candidate in reversed(matches):
            try:
                obj = json.loads(candidate)
                if "final_assessment" in obj:
                    return obj
            except Exception:
                continue
        return {}

    @staticmethod
    def _extract_card(text: str) -> FindingCard:
        marker = "FINDING CARD:\n"
        payload = text.split(marker, 1)[1].split("\n\nRETRIEVED EVIDENCE:", 1)[0] if marker in text else text
        card = FindingCard(case_id="dummy", modality="MG")
        for line in payload.split(" | "):
            line = line.strip()
            if line.startswith("Modality:"):
                card.modality = line.split(":", 1)[1].strip()
            elif line.startswith("Laterality:"):
                card.laterality = line.split(":", 1)[1].strip()
            elif line.startswith("Breast density:"):
                card.breast_density = line.split(":", 1)[1].strip()
            elif line.startswith("Lesion ") and ":" in line and " at " in line:
                left, rest = line.split(" at ", 1)
                kind = left.split(":", 1)[1].strip()
                loc = rest.split(";", 1)[0].strip()
                desc = []
                if "descriptors:" in rest:
                    desc = [x.strip() for x in rest.split("descriptors:", 1)[1].split(",") if x.strip()]
                card.lesions.append(Lesion(kind=kind, location=loc, descriptors=desc or []))
            elif line.startswith("Pathology annotation:"):
                card.pathology = line.split(":", 1)[1].strip()
        return card

    @staticmethod
    def _clinician(card: FindingCard) -> str:
        # Conservative demo behavior: do not manufacture a BI-RADS category when none is supplied.
        category = card.birads if card.birads is not None else 0
        findings = "No assessment category is inferred by the smoke-test backend."
        if card.lesions:
            findings = "; ".join(f"{x.kind} at {x.location}" for x in card.lesions) + "."
        payload = {
            "view": "not available",
            "breast_density": card.breast_density,
            "lesions": [
                {
                    "kind": x.kind,
                    "location": x.location,
                    "size_mm": x.size_mm,
                    "descriptors": x.descriptors,
                }
                for x in card.lesions
            ],
            "findings": findings,
            "final_assessment": category,
            "recommendation": REC_BY_CATEGORY.get(category),
        }
        return json.dumps(payload)

    @staticmethod
    def _patient(draft: dict) -> str:
        cat = draft.get("final_assessment")
        if cat == 0:
            return "Your report needs more imaging information."
        if cat in (1, 2):
            return "Your report describes a finding that is negative or benign."
        if cat == 3:
            return "Your report describes a finding that is probably benign."
        if cat in (4, 5):
            return "Your report describes a finding that needs further evaluation."
        if cat == 6:
            return "Your report describes a known biopsy-proven malignancy."
        return "Your report could not be explained from the available draft."

    @staticmethod
    def _self_check(text: str) -> str:
        # Very small deterministic check for the smoke suite only.
        return "CONSISTENT"
