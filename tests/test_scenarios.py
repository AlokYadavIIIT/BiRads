from __future__ import annotations

import time
from pathlib import Path
from typing import Any
import pytest
from fastapi.testclient import TestClient

from rp5.api import app
from rp5.attribution.aligner import Aligner, coverage, split_sentences
from rp5.config import RP5Config
from rp5.domain import Chunk, FindingCard, Lesion, Passage
from rp5.generation.heads import PatientHead, FALLBACK_ERROR_MESSAGE
from rp5.generation.llm_backend import DummyBackend, LLMBackend
from rp5.guard.guard_agent import GuardAgent
from rp5.normalization import (
    clean_location_text,
    extract_measurement,
    normalize_finding_card,
    normalize_lesion,
)
from rp5.pipeline import RAGPipeline


@pytest.fixture
def test_pipeline():
    root = Path(__file__).parents[1]
    cfg = RP5Config(
        corpus_path=root / "data" / "corpus.jsonl",
        index_type="numpy",
        reference_label_in_prompt=False,
        confidence_threshold=0.35,
        coverage_threshold=0.70,
    )
    return RAGPipeline(cfg, backend=DummyBackend()).load_corpus()


# ==============================================================================
# Scenario A — Successful explanation
# ==============================================================================
def test_scenario_a_successful_explanation(test_pipeline):
    card = FindingCard(
        case_id="SCENARIO-A",
        modality="MG",
        laterality="left",
        lesions=[
            Lesion(
                kind="mass",
                location="upper outer quadrant",
                descriptors=["circumscribed"],
                size_mm=12.0,
            )
        ],
        birads=2,
    )
    result = test_pipeline.answer(card, temperature=0.0)

    assert not hasattr(result, "abstained") or result.abstained is False
    assert result.patient_generation_status == "success"
    assert result.patient_fk_grade is not None
    assert result.patient_fk_grade < 12.0
    # Patient explanation must not be a fallback error
    assert FALLBACK_ERROR_MESSAGE not in result.patient_text
    assert "Your report could not be explained" not in result.patient_text
    assert "circumscribed" in result.patient_text.lower() or "benign" in result.patient_text.lower()

    # Attribution and metrics are present and populated
    assert result.coverage is not None
    assert result.coverage > 0.0
    assert result.confidence is not None
    assert result.confidence > 0.0
    assert "retrieval_ms" in result.latency_ms
    assert "clinician_ms" in result.latency_ms
    assert "patient_ms" in result.latency_ms
    assert "attribution_ms" in result.latency_ms
    assert "guard_ms" in result.latency_ms
    assert "total_ms" in result.latency_ms

    # API returns matching serialized structure
    d = result.to_dict()
    assert d["patient_fk_grade"] is not None
    assert d["patient_generation_status"] == "success"
    assert d["assessment_provenance"] == "source_explicit"


# ==============================================================================
# Scenario B — Patient generation failure & fallback handling
# ==============================================================================
class FailingBackend(LLMBackend):
    """Simulates LLM provider timeout or unexpected exception."""
    def generate(self, messages, temperature=0.2, max_tokens=512, seed=0):
        if "patient-communication assistant" in "\n".join(m.get("content", "") for m in messages).lower():
            raise TimeoutError("Provider timed out after 30000ms")
        return DummyBackend().generate(messages, temperature, max_tokens, seed)


class MalformedOutputBackend(LLMBackend):
    """Simulates LLM returning empty or malformed non-explanation."""
    def generate(self, messages, temperature=0.2, max_tokens=512, seed=0):
        if "patient-communication assistant" in "\n".join(m.get("content", "") for m in messages).lower():
            return "", None
        return DummyBackend().generate(messages, temperature, max_tokens, seed)


def test_scenario_b_provider_timeout_failure():
    cfg = RP5Config()
    head = PatientHead(FailingBackend(), cfg)
    draft = {
        "view": "MG",
        "findings": "mass at upper outer quadrant, 12.0 mm.",
        "final_assessment": 2,
        "recommendation": "Routine screening.",
        "lesions": [{"kind": "mass", "location": "upper outer quadrant", "size_mm": 12.0}],
    }
    passages = [
        Passage(
            chunk=Chunk("c1", "d1", "S1", "MASS", "MASS descriptors: circumscribed", 6),
            score=0.9,
        )
    ]
    text, grade, regen = head.generate(draft, passages, 0.0, 42)

    assert grade is None
    assert text == FALLBACK_ERROR_MESSAGE
    assert regen is False


def test_scenario_b_malformed_empty_output_failure():
    cfg = RP5Config()
    head = PatientHead(MalformedOutputBackend(), cfg)
    draft = {
        "view": "MG",
        "findings": "mass at upper outer quadrant, 12.0 mm.",
        "final_assessment": 2,
        "recommendation": "Routine screening.",
        "lesions": [{"kind": "mass", "location": "upper outer quadrant", "size_mm": 12.0}],
    }
    text, grade, regen = head.generate(draft, [], 0.0, 42)

    assert grade is None
    assert text == FALLBACK_ERROR_MESSAGE


def test_scenario_b_pipeline_handles_patient_failure():
    root = Path(__file__).parents[1]
    cfg = RP5Config(
        corpus_path=root / "data" / "corpus.jsonl",
        index_type="numpy",
        confidence_threshold=0.35,
        coverage_threshold=0.70,
    )
    pipe = RAGPipeline(cfg, backend=FailingBackend()).load_corpus()
    card = FindingCard(
        case_id="SCENARIO-B",
        modality="MG",
        lesions=[Lesion(kind="mass", location="left", descriptors=["circumscribed"], size_mm=12.0)],
        birads=2,
    )
    res = pipe.answer(card, temperature=0.0)

    assert res.patient_fk_grade is None
    assert res.patient_generation_status == "failed"
    d = res.to_dict()
    assert d["patient_fk_grade"] is None
    assert d["patient_text"] == FALLBACK_ERROR_MESSAGE
    assert any("Patient explanation" in w for w in res.validation_warnings)


# ==============================================================================
# Scenario C — Measurement normalization
# ==============================================================================
def test_scenario_c_extract_and_normalize_measurements():
    # 1. Extraction of 12.0 mm
    size, warns = extract_measurement("mass at upper outer quadrant, 12.0 mm.")
    assert size == 12.0
    assert not warns

    # 2. Conversion from cm to mm (1.2 cm -> 12.0 mm)
    size_cm, warns_cm = extract_measurement("mass measuring 1.2 cm in greatest dimension")
    assert size_cm == 12.0

    # 3. Text without measurement
    size_none, _ = extract_measurement("diffuse density with no focal mass")
    assert size_none is None

    # 4. Out of range measurement rejected safely
    size_huge, warns_huge = extract_measurement("lesion measuring 500 mm")
    assert size_huge is None
    assert any("outside plausible clinical range" in w for w in warns_huge)

    # 5. Location cleaning preserves anatomy and extracts measurement
    clean_loc, extracted, _ = clean_location_text("upper outer quadrant, 12.0 mm")
    assert clean_loc == "upper outer quadrant"
    assert extracted == 12.0


def test_scenario_c_structured_vs_text_conflict():
    # Structured 15.0 mm vs text 12.0 mm
    lesion = Lesion(
        kind="mass",
        location="upper outer quadrant, 12.0 mm",
        size_mm=15.0,
        descriptors=["circumscribed"],
    )
    norm_lesion, warns = normalize_lesion(lesion)

    # Structured measurement must be preserved
    assert norm_lesion.size_mm == 15.0
    assert norm_lesion.location == "upper outer quadrant"
    assert any("conflicts with textual measurement" in w for w in warns)


def test_scenario_c_finding_card_normalization():
    card = FindingCard(
        case_id="C-NORM",
        modality="mg",
        laterality="left",
        breast_density="0.5",  # Invalid numeric density
        lesions=[
            {"kind": "mass", "location": "upper outer quadrant, 12.0 mm", "descriptors": ["circumscribed"]}
        ],
    )
    norm_card, warns = normalize_finding_card(card)

    assert norm_card.modality == "MG"
    # 0.5 must NOT be assumed to be a valid category
    assert norm_card.breast_density is None
    assert any("Invalid breast density '0.5'" in w for w in warns)
    # Lesion size must be extracted into size_mm
    assert norm_card.lesions[0].size_mm == 12.0
    assert norm_card.lesions[0].location == "upper outer quadrant"


# ==============================================================================
# Scenario D — Attribution disagreement & clinical conflict policies
# ==============================================================================
def test_scenario_d_lexical_high_semantic_low_is_uncertain():
    cfg = RP5Config()
    aligner = Aligner(cfg)

    claim = "A mass at upper outer quadrant measuring 12.0 mm."
    # Irrelevant passage sharing lexical words
    unrelated_passage = Passage(
        chunk=Chunk(
            "s4_unrelated",
            "doc",
            "S4",
            "CASE",
            "A mass was evaluated at the upper outer quadrant in this unrelated screening case.",
            15,
        ),
        score=0.4,
    )
    card_text = "Modality: MG | Lesion 1: calcification at lower inner quadrant; descriptors: amorphous"

    res = aligner.align([claim], [unrelated_passage], card_text)
    attrs = res[claim]
    top_attr = attrs[0]

    # The claim must NOT be accepted as supported solely from token overlap
    # It must be tagged according to policy
    assert top_attr.status in ("uncertain", "unsupported")
    if not top_attr.supported:
        assert top_attr.decision_reason in (
            "lexical_overlap_without_semantic_support",
            "insufficient_evidence_support",
            "borderline_support_requires_review",
            "absent_from_finding_card",
        )


def test_scenario_d_negation_conflict_is_unsupported():
    cfg = RP5Config()
    aligner = Aligner(cfg)

    claim = "No mass is present in the breast."
    passage = Passage(
        chunk=Chunk("c1", "d1", "S1", "MASS", "A circumscribed mass is present in the breast.", 10),
        score=0.9,
    )
    res = aligner.align([claim], [passage], "Modality: MG")
    attr = res[claim][0]

    assert attr.status == "unsupported"
    assert attr.supported is False
    assert attr.decision_reason == "negation_contradiction"


def test_scenario_d_measurement_mismatch_is_unsupported():
    cfg = RP5Config()
    aligner = Aligner(cfg)

    claim = "A mass measuring 12.0 mm is present."
    passage = Passage(
        chunk=Chunk("c1", "d1", "S4", "CASE", "A mass measuring 25.0 mm was observed.", 10),
        score=0.9,
    )
    res = aligner.align([claim], [passage], "Modality: MG")
    attr = res[claim][0]

    assert attr.status == "unsupported"
    assert attr.supported is False
    assert "measurement_mismatch" in attr.decision_reason


def test_scenario_d_laterality_mismatch_is_unsupported():
    cfg = RP5Config()
    aligner = Aligner(cfg)

    claim = "A mass in the left breast."
    passage = Passage(
        chunk=Chunk("c1", "d1", "S4", "CASE", "A mass in the right breast.", 8),
        score=0.9,
    )
    res = aligner.align([claim], [passage], "Modality: MG")
    attr = res[claim][0]

    assert attr.status == "unsupported"
    assert attr.supported is False
    assert attr.decision_reason == "laterality_mismatch"


# ==============================================================================
# Scenario E — Clinical validation & BI-RADS provenance
# ==============================================================================
def test_scenario_e_contradictory_recommendation_abstained():
    cfg = RP5Config(confidence_threshold=0.35)
    guard = GuardAgent(cfg)

    card = FindingCard(case_id="E-CONTRA", modality="MG", lesions=[Lesion("mass", "left")])
    # BI-RADS 1 (negative) with Biopsy recommendation is a fatal contradiction
    contradictory_draft = {
        "view": "MG",
        "findings": "Negative exam.",
        "final_assessment": 1,
        "recommendation": "Biopsy is recommended immediately.",
        "lesions": [],
    }
    res = guard.evaluate(
        draft=contradictory_draft,
        card=card,
        passages=[],
        attribution_map={},
        patient_text="Everything looks fine.",
        patient_fk_grade=5.0,
        retrieval_scores=[0.9],
        confidence=0.9,
    )
    assert res is not None
    assert res.abstained is True
    assert res.reason == "category_conflict"
    assert any("recommendation is inconsistent" in m for m in res.missing_information)


def test_scenario_e_provenance_and_clinician_review(test_pipeline):
    # When reference_birads is not supplied, draft assessment is model_proposed
    card_unspecified = FindingCard(
        case_id="E-PROV",
        modality="MG",
        lesions=[Lesion("mass", "upper outer quadrant", 12.0, ["circumscribed"])],
        birads=None,
    )
    res = test_pipeline.answer(card_unspecified, temperature=0.0)

    assert res.assessment_provenance == "model_proposed"
    assert res.requires_clinician_review is True
    d = res.to_dict()
    assert d["assessment_provenance"] == "model_proposed"
    assert d["requires_clinician_review"] is True


# ==============================================================================
# Scenario F — Performance & high-resolution stage latency
# ==============================================================================
def test_scenario_f_latency_measurements(test_pipeline):
    card = FindingCard(
        case_id="F-PERF",
        modality="MG",
        lesions=[Lesion("mass", "left", 10.0, ["circumscribed"])],
        birads=2,
    )
    res = test_pipeline.answer(card, temperature=0.0)
    lat = res.latency_ms

    assert lat["total_ms"] > 0.0
    assert lat["retrieval_ms"] >= 0.0
    assert lat["clinician_ms"] >= 0.0
    assert lat["patient_ms"] >= 0.0
    assert lat["attribution_ms"] >= 0.0
    assert lat["guard_ms"] >= 0.0

    # Total duration must encompass all individual stages
    stages_sum = (
        lat["retrieval_ms"]
        + lat["clinician_ms"]
        + lat["patient_ms"]
        + lat["attribution_ms"]
        + lat["guard_ms"]
    )
    assert lat["total_ms"] >= stages_sum * 0.7  # Reasonable margin for measurement order


# ==============================================================================
# Scenario G — Request isolation
# ==============================================================================
def test_scenario_g_request_isolation(test_pipeline):
    card1 = FindingCard(
        case_id="CASE-1",
        modality="MG",
        lesions=[Lesion("mass", "upper outer quadrant", 12.0, ["circumscribed"])],
        birads=2,
    )
    card2 = FindingCard(
        case_id="CASE-2",
        modality="MG",
        lesions=[Lesion("calcification", "lower inner quadrant", None, ["punctate"])],
        birads=4,
    )

    res1 = test_pipeline.answer(card1, temperature=0.0)
    res2 = test_pipeline.answer(card2, temperature=0.0)

    # Output isolation
    assert res1.case_id == "CASE-1"
    assert res2.case_id == "CASE-2"
    assert res1.clinician_draft["final_assessment"] == 2
    assert res2.clinician_draft["final_assessment"] == 4
    assert res1.patient_text != res2.patient_text
    assert "calcification" not in res1.clinician_text.lower()
    assert "calcification" in res2.clinician_text.lower()


# ==============================================================================
# API End-to-End Integration
# ==============================================================================
def test_api_full_flow():
    import rp5.api
    rp5.api._pipeline = None
    client = TestClient(app)
    payload = {
        "case_id": "API-TEST",
        "modality": "MG",
        "laterality": "left",
        "breast_density": "B",
        "pathology": None,
        "reason_for_exam": "screening",
        "lesions": [
            {
                "kind": "mass",
                "location": "upper outer quadrant",
                "size_mm": 12.0,
                "descriptors": ["circumscribed"],
            }
        ],
        "reference_birads": 2,
    }
    resp = client.post("/api/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["case_id"] == "API-TEST"
    assert data["abstained"] is False
    assert data["patient_generation_status"] == "success"
    assert data["patient_fk_grade"] is not None
    assert data["coverage"] is not None
    assert data["confidence"] is not None
    assert "latency_ms" in data
    assert "attribution" in data
