from __future__ import annotations

import re

from rp5.config import RP5Config
from rp5.domain import Abstention, FindingCard
from rp5.evaluation.metrics import citation_coverage
from rp5.evaluation.readability import flesch_kincaid
from rp5.generation.llm_backend import LLMBackend
from rp5.generation.prompts import make_selfcheck_messages

_CATEGORY_RECOMMENDATION = {
    0: "additional imaging",
    1: "routine screening",
    2: "routine screening",
    3: "short-interval follow-up",
    4: "biopsy",
    5: "biopsy",
    6: "known malignancy",
}
_BENIGN_PATHOLOGY = {"benign", "negative for malignancy", "fibroadenoma", "cyst", "normal"}


class GuardAgent:
    def __init__(self, cfg: RP5Config, backend: LLMBackend | None = None):
        self.cfg = cfg
        self.backend = backend

    @staticmethod
    def _recommendation_aligned(category: int, recommendation: str | None) -> bool:
        if category == 0:
            return recommendation is None or "additional" in recommendation.lower()
        if not recommendation:
            return category in (1, 2, 6)
        expected = _CATEGORY_RECOMMENDATION[category]
        return expected in recommendation.lower()

    @staticmethod
    def _descriptor_supported(descriptor: str, passages) -> bool:
        needle = descriptor.strip().lower()
        return bool(needle) and any(
            p.chunk.stratum == "S1" and needle in p.chunk.text.lower() for p in passages
        )

    def evaluate(
        self,
        draft: dict,
        card: FindingCard,
        passages,
        attribution_map: dict,
        patient_text: str,
        patient_fk_grade: float,
        retrieval_scores: list[float],
        confidence: float,
    ) -> Abstention | None:

        # ------------------------------------------------------------
        # Basic structural validation
        # ------------------------------------------------------------
        if "final_assessment" not in draft:
            return Abstention(
                card.case_id,
                "parse_failure",
                ["final_assessment missing"],
            )

        try:
            category = int(draft["final_assessment"])
        except Exception:
            return Abstention(
                card.case_id,
                "category_conflict",
                ["final_assessment is not an integer"],
            )

        if category < 0 or category > 6:
            return Abstention(
                card.case_id,
                "category_conflict",
                [f"invalid category {category}"],
            )

        # Collect ALL violations instead of returning on the first one.
        violations = []

        # ------------------------------------------------------------
        # Detect internally inconsistent finding cards (F2 audit)
        # ------------------------------------------------------------
        if (
            card.pathology
            and card.pathology.strip().lower() in _BENIGN_PATHOLOGY
            and card.birads in (4, 5)
        ):
            violations.append(
                f"finding card is internally inconsistent: "
                f"benign pathology with BI-RADS {card.birads}"
            )

        # ------------------------------------------------------------
        # 1. Descriptor support
        # ------------------------------------------------------------
        for lesion in draft.get("lesions", []):
            for descriptor in lesion.get("descriptors", []) or []:
                if not self._descriptor_supported(descriptor, passages):
                    violations.append(
                        f"unsupported descriptor: {descriptor}"
                    )

        # ------------------------------------------------------------
        # 2. Pathology vs BI-RADS consistency
        # ------------------------------------------------------------
        if (
            card.pathology
            and card.pathology.strip().lower() in _BENIGN_PATHOLOGY
            and category in (4, 5)
        ):
            violations.append(
                "benign pathology conflicts with category 4/5"
            )

        # ------------------------------------------------------------
        # 3. Recorded BI-RADS vs generated BI-RADS
        # ------------------------------------------------------------
        if (
            self.cfg.enforce_reference_label_guard
            and card.birads is not None
            and category not in (0, card.birads)
        ):
            violations.append(
                f"reference BI-RADS {card.birads} vs draft {category}"
            )

        # ------------------------------------------------------------
        # 4. Recommendation vs category
        # ------------------------------------------------------------
        if not self._recommendation_aligned(
            category,
            draft.get("recommendation"),
        ):
            violations.append(
                "recommendation is inconsistent with category"
            )

        # ------------------------------------------------------------
        # 5. Citation coverage
        # ------------------------------------------------------------
        cov = citation_coverage(attribution_map)

        if cov < self.cfg.coverage_threshold:
            violations.append(
                f"coverage {cov:.2f} < "
                f"{self.cfg.coverage_threshold:.2f}"
            )

        # ------------------------------------------------------------
        # 6. Internal contradiction self-check
        # ------------------------------------------------------------
        if self.backend is not None:
            self_check, _ = self.backend.generate(
                make_selfcheck_messages(draft),
                temperature=0.0,
                max_tokens=8,
            )

            if "CONTRADICTION" in self_check.upper():
                violations.append(
                    "internal findings/impression contradiction"
                )

        # ------------------------------------------------------------
        # 7. Patient readability
        # ------------------------------------------------------------
        if patient_fk_grade > self.cfg.fk_grade_target:
            violations.append(
                "patient explanation exceeds readability target "
                "after regeneration"
            )

        # ------------------------------------------------------------
        # 8. Confidence
        # ------------------------------------------------------------
        top_retrieval = (
            max(retrieval_scores)
            if retrieval_scores
            else 0.0
        )

        rho = (
            0.6 * confidence
            + 0.4 * max(
                0.0,
                min(1.0, top_retrieval)
            )
        )

        if rho < self.cfg.confidence_threshold:
            violations.append(
                f"confidence score {rho:.2f} below tau "
                f"{self.cfg.confidence_threshold:.2f}"
            )

        # ------------------------------------------------------------
        # Return a single abstention containing ALL violations
        # ------------------------------------------------------------
        if violations:

            if any(
                v.startswith("unsupported descriptor:")
                for v in violations
            ):
                reason = "unsupported_descriptor"

            elif any(
                (
                    "finding card is internally inconsistent" in v
                    or "conflicts with category" in v
                    or "reference BI-RADS" in v
                    or "recommendation is inconsistent" in v
                )
                for v in violations
            ):
                reason = "category_conflict"

            elif any(
                v.startswith("coverage ")
                for v in violations
            ):
                reason = "low_coverage"

            elif any(
                v.startswith("internal findings/impression")
                for v in violations
            ):
                reason = "contradiction"

            elif any(
                v.startswith("patient explanation")
                for v in violations
            ):
                reason = "low_coverage"

            elif any(
                v.startswith("confidence score")
                for v in violations
            ):
                reason = "low_confidence"

            else:
                reason = "category_conflict"

            return Abstention(
                card.case_id,
                reason,
                violations,
            )

        return None