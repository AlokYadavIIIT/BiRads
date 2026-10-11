from __future__ import annotations

import json
from typing import Any

from rp5.domain import FindingCard, Passage


CLINICIAN_SCHEMA = {
    "type": "object",
    "required": ["view", "lesions", "findings", "final_assessment"],
    "properties": {
        "view": {"type": "string"},
        "breast_density": {"type": ["string", "null"]},
        "lesions": {"type": "array"},
        "findings": {"type": "string"},
        "final_assessment": {"type": "integer", "minimum": 0, "maximum": 6},
        "recommendation": {"type": ["string", "null"]},
    },
}

BI_RADS_MEANING = {
    0: "Incomplete",
    1: "Negative",
    2: "Benign",
    3: "Probably benign",
    4: "Suspicious",
    5: "Highly suggestive of malignancy",
    6: "Known biopsy-proven malignancy",
}

CLINICIAN_SYSTEM = """You are a breast-imaging report drafting assistant.

Produce a BI-RADS-structured clinician draft from the finding card and retrieved passages.
The output is a draft for clinician review, not an autonomous diagnosis.

Hard grounding rules:
1. Use only information in the finding card and retrieved passages.
2. Never invent lesion size, laterality, descriptors, views, pathology, or recommendations.
3. Every descriptor in a lesion must be directly supported by the supplied BI-RADS lexicon passages.
4. If the retrieved context does not support a safe assessment, use BI-RADS 0 and explain that support is incomplete.
5. Return EXACTLY ONE JSON OBJECT containing these keys:
   - view
   - breast_density
   - lesions
   - findings
   - final_assessment
   - recommendation
6. Each item in "lesions" must contain:
   - kind
   - location
   - size_mm
   - descriptors
7. "final_assessment" must be an integer from 0 to 6.
8. "breast_density" may be a string or null.
9. "size_mm" may be a number or null.
10. "descriptors" must be an array of strings.
11. "recommendation" may be a string or null.
12. Do NOT output a JSON Schema.
13. Do NOT output the keys "type", "properties", "required", "minimum", or "maximum" as schema definitions.
14. Do NOT output markdown fences such as ```json.
15. Do NOT include explanations before or after the JSON object.
16. The JSON object must contain the actual report data, not a description of the schema.

BI-RADS meanings:
0 = Incomplete
1 = Negative
2 = Benign
3 = Probably benign
4 = Suspicious
5 = Highly suggestive of malignancy
6 = Known biopsy-proven malignancy

Output format example:

{
  "view": "MG",
  "breast_density": "C",
  "lesions": [
    {
      "kind": "mass",
      "location": "central breast",
      "size_mm": 15.0,
      "descriptors": ["spiculated"]
    }
  ],
  "findings": "A mass is present in the central breast with spiculated margins.",
  "final_assessment": 5,
  "recommendation": "Biopsy strongly advised."
}

Important:
- "findings" MUST be one plain string, never an array or list.
- "size_mm" MUST be a number such as 15.0, or null.
- "lesions" MUST be an array of lesion objects.
- "descriptors" MUST be an array of strings.
- The example is only a formatting example. Do not copy its clinical facts unless supported by the finding card or retrieved evidence.
"""

PATIENT_SYSTEM = """You are a patient-communication assistant.
Rewrite only the clinician draft into plain language.
Do not add any new clinical fact, interpretation, diagnosis, or advice.
Define BI-RADS terms in simple words when they appear.
Use short sentences. Target Flesch-Kincaid grade level <= 8.
Use a friendly, neutral tone and second person.
"""

SELFCHECK_SYSTEM = """Audit a radiology draft.
Compare the findings text with the final assessment and recommendation.
Return exactly one token: CONSISTENT or CONTRADICTION.
Choose CONTRADICTION when the impression introduces a claim absent from findings.
"""


def serialize_card(card: FindingCard, include_reference_label: bool = False) -> str:
    return card.serialize(include_reference_label=include_reference_label)


def _ctx(passages: list[Passage]) -> str:
    return "\n\n".join(
        f"[{p.chunk.chunk_id} | {p.chunk.stratum} | score={p.score:.3f}]\n{p.chunk.text}"
        for p in passages
    )


def make_clinician_messages(
    card: FindingCard,
    passages: list[Passage],
    examples: list[Passage] | None = None,
    include_reference_label: bool = False,
) -> list[dict[str, str]]:
    card_text = serialize_card(card, include_reference_label)
    example_block = ""
    if examples:
        example_block = "\n\nEXPERT-REVIEWED EXAMPLES (style only; do not copy unsupported facts):\n" + _ctx(examples)
    user = f"FINDING CARD:\n{card_text}\n\nRETRIEVED EVIDENCE:\n{_ctx(passages)}{example_block}"
    return [{"role": "system", "content": CLINICIAN_SYSTEM}, {"role": "user", "content": user}]


def make_patient_messages(draft: dict[str, Any], passages: list[Passage]) -> list[dict[str, str]]:
    user = f"CLINICIAN DRAFT:\n{json.dumps(draft, indent=2)}\n\nSUPPORTING EVIDENCE:\n{_ctx(passages)}"
    return [{"role": "system", "content": PATIENT_SYSTEM}, {"role": "user", "content": user}]


def make_selfcheck_messages(draft: dict[str, Any]) -> list[dict[str, str]]:
    user = (
        f"FINDINGS: {draft.get('findings', '')}\n"
        f"FINAL ASSESSMENT: BI-RADS {draft.get('final_assessment')}\n"
        f"RECOMMENDATION: {draft.get('recommendation') or ''}"
    )
    return [{"role": "system", "content": SELFCHECK_SYSTEM}, {"role": "user", "content": user}]
