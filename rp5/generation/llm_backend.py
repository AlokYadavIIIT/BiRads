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
        search_start = text.find("CLINICIAN DRAFT:")
        if search_start == -1:
            search_start = 0

        start = text.find("{", search_start)
        while start != -1:
            depth = 0
            in_str = False
            escape = False
            for i in range(start, len(text)):
                c = text[i]
                if escape:
                    escape = False
                    continue
                if c == "\\":
                    escape = True
                    continue
                if c == '"':
                    in_str = not in_str
                    continue
                if not in_str:
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            candidate = text[start : i + 1]
                            try:
                                obj = json.loads(candidate)
                                if isinstance(obj, dict) and "final_assessment" in obj:
                                    return obj
                            except json.JSONDecodeError:
                                pass
                            break
            start = text.find("{", start + 1)
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
                from rp5.normalization import clean_location_text
                clean_loc, extracted_size, _ = clean_location_text(loc)
                card.lesions.append(
                    Lesion(
                        kind=kind,
                        location=clean_loc,
                        size_mm=extracted_size,
                        descriptors=desc or [],
                    )
                )
            elif line.startswith("Pathology annotation:"):
                card.pathology = line.split(":", 1)[1].strip()
            elif line.startswith("Recorded BI-RADS assessment:"):
                try:
                    card.birads = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
        from rp5.normalization import normalize_finding_card
        card, _ = normalize_finding_card(card)
        return card

    @staticmethod
    def _clinician(card: FindingCard) -> str:
        category = card.birads
        if category is None:
            all_desc = []
            for l in card.lesions:
                all_desc.extend(d.lower() for d in (l.descriptors or []))
            if any("spiculat" in d for d in all_desc):
                category = 5
            elif any("circumscrib" in d for d in all_desc):
                category = 2
            elif any("calc" in l.kind.lower() for l in card.lesions):
                category = 4
            elif card.lesions:
                category = 0
            else:
                category = 1

        findings = "No abnormalities detected."
        if card.lesions:
            findings_parts = []
            for x in card.lesions:
                size_str = f", {x.size_mm:.1f} mm" if x.size_mm is not None else ""
                findings_parts.append(f"{x.kind} at {x.location}{size_str}")
            findings = "; ".join(findings_parts) + "."

        view = "MG" if card.modality == "MG" else None
        density = card.breast_density if card.breast_density in {"A", "B", "C", "D"} else None
        payload = {
            "view": view,
            "breast_density": density,
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
        if cat is None:
            raise ValueError("Clinician draft missing final_assessment")
        findings = draft.get("findings", "").strip()
        desc_text = "a finding"
        if findings and findings != "No abnormalities detected.":
            desc_text = findings.rstrip(".")

        if cat == 0:
            return f"Your mammogram shows {desc_text}. Your doctor needs additional imaging before completing the final review. Please schedule your follow-up imaging."
        if cat in (1, 2):
            return f"Your mammogram shows {desc_text}. This is benign, meaning non-cancerous. You should continue with your regular routine screening."
        if cat == 3:
            return f"Your mammogram shows {desc_text}. This finding is probably benign. A short-interval follow-up exam is recommended to monitor for changes."
        if cat == 4:
            return f"Your mammogram shows {desc_text}. This finding is suspicious for cancer. Your doctor recommends a biopsy to test the tissue."
        if cat == 5:
            return f"Your mammogram shows {desc_text}. This finding is highly suspicious for cancer. Your doctor strongly advises a biopsy to test the tissue."
        if cat == 6:
            return f"Your report describes a known biopsy-proven cancer (malignancy). Please follow up with your oncology care team."
        raise ValueError(f"Unrecognized BI-RADS category {cat}")

    @staticmethod
    def _self_check(text: str) -> str:
        # Very small deterministic check for the smoke suite only.
        return "CONSISTENT"
