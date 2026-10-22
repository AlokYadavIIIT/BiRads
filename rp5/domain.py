from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class Lesion:
    kind: str
    location: str
    size_mm: Optional[float] = None
    descriptors: list[str] = field(default_factory=list)
    assessment_hint: Optional[int] = None


@dataclass
class FindingCard:
    case_id: str
    modality: str
    laterality: str = ""
    breast_density: Optional[str] = None
    lesions: list[Lesion] = field(default_factory=list)
    birads: Optional[int] = None  # evaluation/reference label; hidden from model by default
    pathology: Optional[str] = None
    reason_for_exam: str = ""

    def __post_init__(self):
        if self.lesions:
            from rp5.normalization import normalize_lesion
            self.lesions = [
                normalize_lesion(x)[0]
                for x in self.lesions
            ]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def serialize(self, include_reference_label: bool = False) -> str:
        """Create the retrieval query without inventing clinical facts."""
        parts = [f"Modality: {self.modality}"]
        if self.laterality:
            parts.append(f"Laterality: {self.laterality}")
        if self.breast_density:
            parts.append(f"Breast density: {self.breast_density}")
        for i, lesion in enumerate(self.lesions, 1):
            desc = ", ".join(lesion.descriptors) if lesion.descriptors else "not further characterized"
            size = f", {lesion.size_mm:.1f} mm" if lesion.size_mm is not None else ""
            parts.append(
                f"Lesion {i}: {lesion.kind} at {lesion.location}{size}; descriptors: {desc}"
            )
        if include_reference_label and self.birads is not None:
            parts.append(f"Recorded BI-RADS assessment: {self.birads}")
        if self.pathology:
            parts.append(f"Pathology annotation: {self.pathology}")
        if self.reason_for_exam:
            parts.append(f"Reason for exam: {self.reason_for_exam}")
        return " | ".join(parts)


@dataclass
class CorpusDocument:
    doc_id: str
    stratum: str  # S1 lexicon | S2 guidance | S3 template | S4 example
    source: str
    text: str
    transform_note: str = ""


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    stratum: str
    section: str
    text: str
    token_count: int


@dataclass
class Passage:
    chunk: Chunk
    score: float


@dataclass
class Attribution:
    span: str
    passage_id: str
    stratum: str
    score: float
    method: str
    supported: bool
    passage_text: str = ""
    lexical_score: float = 0.0
    semantic_score: float = 0.0
    status: str = "uncertain"  # supported | unsupported | uncertain
    decision_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Abstention:
    case_id: str
    reason: str  # category_conflict | unsupported_descriptor | low_coverage | contradiction | low_confidence | parse_failure
    missing_information: list[str] = field(default_factory=list)
    validation_warnings: list[str] = field(default_factory=list)
    abstained: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "abstained": True,
            "reason": self.reason,
            "missing_information": self.missing_information,
            "validation_warnings": self.validation_warnings,
        }


@dataclass
class DraftResult:
    case_id: str
    clinician_draft: dict[str, Any]
    clinician_text: str
    patient_text: str
    patient_fk_grade: Optional[float]
    patient_regen: bool
    attribution_map: dict[str, list[Attribution]]
    patient_attribution_map: dict[str, list[Attribution]]
    coverage: Optional[float]
    confidence: Optional[float]
    retrieval_scores: list[float]
    latency_ms: dict[str, float]
    hallucination_flag: bool = False
    patient_generation_status: str = "success"  # success | failed
    assessment_provenance: str = "model_proposed"  # source_explicit | model_proposed | undetermined
    requires_clinician_review: bool = True
    validation_warnings: list[str] = field(default_factory=list)
    metrics_explanation: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "abstained": False,
            "clinician_draft": self.clinician_draft,
            "clinician_text": self.clinician_text,
            "patient_text": self.patient_text,
            "patient_fk_grade": round(self.patient_fk_grade, 2) if self.patient_fk_grade is not None else None,
            "patient_regen": self.patient_regen,
            "patient_generation_status": self.patient_generation_status,
            "assessment_provenance": self.assessment_provenance,
            "requires_clinician_review": self.requires_clinician_review,
            "validation_warnings": self.validation_warnings,
            "metrics_explanation": self.metrics_explanation,
            "coverage": round(self.coverage, 4) if self.coverage is not None else None,
            "confidence": round(self.confidence, 4) if self.confidence is not None else None,
            "retrieval_scores": [round(x, 4) for x in self.retrieval_scores],
            "latency_ms": {k: round(v, 2) for k, v in self.latency_ms.items()},
            "hallucination_flag": self.hallucination_flag,
            "attribution": {
                k: [a.to_dict() for a in v] for k, v in self.attribution_map.items()
            },
            "patient_attribution": {
                k: [a.to_dict() for a in v] for k, v in self.patient_attribution_map.items()
            },
        }
