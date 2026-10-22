from __future__ import annotations

import logging
import re
from typing import Optional

from rp5.config import RP5Config
from rp5.domain import Abstention, FindingCard
from rp5.evaluation.metrics import citation_coverage
from rp5.generation.llm_backend import LLMBackend
from rp5.generation.prompts import make_selfcheck_messages
from rp5.normalization import MIN_PLAUSIBLE_SIZE_MM, MAX_PLAUSIBLE_SIZE_MM, extract_measurement

logger = logging.getLogger("rp5.guard")

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
        self.last_warnings: list[str] = []
        self.requires_review: bool = False

    @staticmethod
    def _recommendation_aligned(category: int, recommendation: str | None) -> bool:
        if category == 0:
            if not recommendation:
                return True
            rec_lower = recommendation.lower()
            return "additional" in rec_lower or "further" in rec_lower or "imaging" in rec_lower
        if not recommendation:
            return category in (1, 2, 6)
        expected = _CATEGORY_RECOMMENDATION.get(category, "")
        rec_lower = recommendation.lower()
        if expected in rec_lower:
            return True
        # Contradictions
        if category in (1, 2) and ("biopsy" in rec_lower or "malignan" in rec_lower):
            return False
        if category in (4, 5) and "routine" in rec_lower:
            return False
        return expected in rec_lower

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
        patient_fk_grade: Optional[float],
        retrieval_scores: list[float],
        confidence: float,
    ) -> Abstention | None:
        self.last_warnings = []
        self.requires_review = False
        fatal_violations: list[str] = []

        # ------------------------------------------------------------
        # 1. Structural schema validation
        # ------------------------------------------------------------
        if not isinstance(draft, dict):
            return Abstention(card.case_id, "parse_failure", ["draft is not a dictionary"])

        if "final_assessment" not in draft:
            return Abstention(card.case_id, "parse_failure", ["final_assessment missing"])

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

        if not isinstance(draft.get("findings"), str) or not draft.get("findings", "").strip():
            fatal_violations.append("findings text is missing or empty")

        if not isinstance(draft.get("lesions"), list):
            fatal_violations.append("lesions must be an array")

        # ------------------------------------------------------------
        # 2. Lesion measurement and consistency validation
        # ------------------------------------------------------------
        for lesion in draft.get("lesions", []):
            if not isinstance(lesion, dict):
                fatal_violations.append("malformed lesion object in draft")
                continue
            s_mm = lesion.get("size_mm")
            if s_mm is not None:
                try:
                    s_val = float(s_mm)
                    if s_val < MIN_PLAUSIBLE_SIZE_MM or s_val > MAX_PLAUSIBLE_SIZE_MM:
                        fatal_violations.append(
                            f"lesion measurement {s_val} mm is outside plausible clinical range"
                        )
                except (ValueError, TypeError):
                    fatal_violations.append(f"malformed lesion measurement '{s_mm}'")

            # Check measurement conflict between findings text and structured size
            findings_text = draft.get("findings", "")
            meas_in_text, _ = extract_measurement(findings_text)
            if meas_in_text is not None and s_mm is not None:
                try:
                    if abs(float(s_mm) - meas_in_text) > 0.5:
                        self.last_warnings.append(
                            f"Discrepancy: findings text states {meas_in_text:.1f} mm but structured lesion has {float(s_mm):.1f} mm."
                        )
                        self.requires_review = True
                except (ValueError, TypeError):
                    pass

        # ------------------------------------------------------------
        # 3. Detect internally inconsistent finding cards (F2 audit)
        # ------------------------------------------------------------
        if (
            card.pathology
            and card.pathology.strip().lower() in _BENIGN_PATHOLOGY
            and card.birads in (4, 5)
        ):
            fatal_violations.append(
                f"finding card is internally inconsistent: benign pathology with BI-RADS {card.birads}"
            )

        # ------------------------------------------------------------
        # 4. Descriptor support in S1 lexicon
        # ------------------------------------------------------------
        for lesion in draft.get("lesions", []):
            for descriptor in lesion.get("descriptors", []) or []:
                if not self._descriptor_supported(descriptor, passages):
                    fatal_violations.append(f"unsupported descriptor: {descriptor}")

        # ------------------------------------------------------------
        # 5. Pathology vs BI-RADS consistency
        # ------------------------------------------------------------
        if (
            card.pathology
            and card.pathology.strip().lower() in _BENIGN_PATHOLOGY
            and category in (4, 5)
        ):
            fatal_violations.append("benign pathology conflicts with category 4/5")

        # ------------------------------------------------------------
        # 6. Recorded BI-RADS vs generated BI-RADS
        # ------------------------------------------------------------
        if (
            self.cfg.enforce_reference_label_guard
            and card.birads is not None
            and category not in (0, card.birads)
        ):
            fatal_violations.append(f"reference BI-RADS {card.birads} vs draft {category}")

        # ------------------------------------------------------------
        # 7. Recommendation vs category alignment
        # ------------------------------------------------------------
        if not self._recommendation_aligned(category, draft.get("recommendation")):
            fatal_violations.append("recommendation is inconsistent with category")

        # ------------------------------------------------------------
        # 8. Citation coverage check
        # ------------------------------------------------------------
        cov = citation_coverage(attribution_map)
        if cov < self.cfg.coverage_threshold:
            fatal_violations.append(
                f"coverage {cov:.2f} < {self.cfg.coverage_threshold:.2f}"
            )

        # ------------------------------------------------------------
        # 9. Internal contradiction self-check
        # ------------------------------------------------------------
        if self.backend is not None:
            try:
                self_check, _ = self.backend.generate(
                    make_selfcheck_messages(draft),
                    temperature=0.0,
                    max_tokens=8,
                )
                if "CONTRADICTION" in self_check.upper():
                    fatal_violations.append("internal findings/impression contradiction")
            except Exception as exc:
                logger.warning("Guard self-check backend call failed: %s", exc)

        # ------------------------------------------------------------
        # 10. Patient explanation status & readability safe handling
        # ------------------------------------------------------------
        if patient_fk_grade is None:
            self.last_warnings.append(
                "Patient explanation could not be verified; FKGL is unavailable."
            )
            self.requires_review = True
        elif patient_fk_grade > self.cfg.fk_grade_target:
            self.last_warnings.append(
                f"Patient explanation readability ({patient_fk_grade:.2f}) exceeds target ({self.cfg.fk_grade_target:.1f})."
            )
            self.requires_review = True

        # ------------------------------------------------------------
        # 11. Confidence threshold check
        # ------------------------------------------------------------
        top_retrieval = max(retrieval_scores) if retrieval_scores else 0.0
        rho = 0.6 * confidence + 0.4 * max(0.0, min(1.0, top_retrieval))

        if rho < self.cfg.confidence_threshold:
            fatal_violations.append(
                f"confidence score {rho:.2f} below tau {self.cfg.confidence_threshold:.2f}"
            )

        # ------------------------------------------------------------
        # Return Abstention if any fatal violations occurred
        # ------------------------------------------------------------
        if fatal_violations:
            if any(v.startswith("unsupported descriptor:") for v in fatal_violations):
                reason = "unsupported_descriptor"
            elif any(
                (
                    "finding card is internally inconsistent" in v
                    or "conflicts with category" in v
                    or "reference BI-RADS" in v
                    or "recommendation is inconsistent" in v
                )
                for v in fatal_violations
            ):
                reason = "category_conflict"
            elif any(v.startswith("coverage ") for v in fatal_violations):
                reason = "low_coverage"
            elif any(v.startswith("internal findings/impression") for v in fatal_violations):
                reason = "contradiction"
            elif any(v.startswith("confidence score") for v in fatal_violations):
                reason = "low_confidence"
            else:
                reason = "category_conflict"

            return Abstention(
                case_id=card.case_id,
                reason=reason,
                missing_information=fatal_violations,
                validation_warnings=self.last_warnings,
            )

        return None