from pathlib import Path

from rp5.attribution.aligner import Aligner, coverage, split_sentences
from rp5.config import RP5Config
from rp5.domain import Chunk, FindingCard, Lesion, Passage
from rp5.evaluation.consistency import consistency_report
from rp5.evaluation.metrics import (
    bleu,
    citation_coverage,
    cohen_kappa,
    factscore_support,
    gwet_ac1,
    mrr,
    ndcg_at_k,
    radgraph_style_entity_f1,
    recall_at_k,
    rouge_l,
)
from rp5.evaluation.readability import flesch_kincaid, flesch_reading_ease
from rp5.guard.guard_agent import GuardAgent
from rp5.pipeline import RAGPipeline


def test_metrics():
    rel = {"a": 1, "b": 1}
    assert recall_at_k(["a", "x", "b"], rel, 3) == 1.0
    assert ndcg_at_k(["a", "b"], rel, 2) == 1.0
    assert mrr([["x", "a"]], rel) == 0.5
    assert gwet_ac1(["1", "2"], ["1", "2"]) == 1.0
    assert cohen_kappa(["1", "2"], ["1", "2"]) == 1.0
    assert bleu("a circumscribed mass was found", "a circumscribed mass was found") > 0.9
    assert rouge_l("a circumscribed mass was found", "a circumscribed mass was found") == 1.0


def test_factscore_and_radgraph():
    claims = ["A mass is present at the upper outer quadrant."]
    evidence = ["A mass is present at the upper outer quadrant."]
    support = factscore_support(claims, evidence)
    assert support == 1.0

    vocab = ["mass", "circumscribed", "spiculated"]
    f1 = radgraph_style_entity_f1("circumscribed mass", "circumscribed mass observed", vocab)
    assert f1 == 1.0


def test_readability():
    text = "The doctor checked your breast. Everything looks fine."
    grade = flesch_kincaid(text)
    ease = flesch_reading_ease(text)
    assert grade < 8.0
    assert ease > 60.0


def test_sentence_split_and_coverage():
    claims = split_sentences("One claim. Another claim!")
    assert len(claims) == 2
    assert coverage({claims[0]: []}) == 0.0
    assert citation_coverage({claims[0]: []}) == 0.0


def test_guard_conflicts_and_descriptors():
    cfg = RP5Config(confidence_threshold=0.55)
    guard = GuardAgent(cfg)

    # 1. Test benign pathology with BI-RADS 5 card triggers category_conflict
    card_conflict = FindingCard(
        case_id="C-CONF",
        modality="MG",
        lesions=[Lesion(kind="mass", location="right", descriptors=["spiculated"])],
        birads=5,
        pathology="benign",
    )
    draft_valid = {
        "view": "MG",
        "breast_density": "B",
        "lesions": [{"kind": "mass", "location": "right", "descriptors": ["spiculated"]}],
        "findings": "A spiculated mass is present.",
        "final_assessment": 5,
        "recommendation": "Biopsy is strongly advised.",
    }
    passages = [
        Passage(
            chunk=Chunk("c1", "d1", "S1", "MASS", "MASS descriptors: spiculated, circumscribed", 6),
            score=0.9,
        )
    ]
    res_conf = guard.evaluate(
        draft=draft_valid,
        card=card_conflict,
        passages=passages,
        attribution_map={"claim": [type("Attr", (), {"supported": True})()]},
        patient_text="Simple explanation.",
        patient_fk_grade=5.0,
        retrieval_scores=[0.9],
        confidence=0.9,
    )
    assert res_conf is not None
    assert res_conf.reason == "category_conflict"

    # 2. Test unsupported descriptor triggers unsupported_descriptor
    card_ooc = FindingCard(
        case_id="C-OOC",
        modality="MG",
        lesions=[Lesion(kind="mass", location="left", descriptors=["hyperlucent fake"])],
    )
    draft_ooc = {
        "view": "MG",
        "breast_density": "B",
        "lesions": [{"kind": "mass", "location": "left", "descriptors": ["hyperlucent fake"]}],
        "findings": "A fake mass is present.",
        "final_assessment": 2,
        "recommendation": "Routine screening.",
    }
    res_ooc = guard.evaluate(
        draft=draft_ooc,
        card=card_ooc,
        passages=passages,
        attribution_map={"claim": [type("Attr", (), {"supported": True})()]},
        patient_text="Simple explanation.",
        patient_fk_grade=5.0,
        retrieval_scores=[0.9],
        confidence=0.9,
    )
    assert res_ooc is not None
    assert res_ooc.reason == "unsupported_descriptor"


def test_consistency_report():
    runs = [
        {"gwet_ac1_non_abstained": 1.0, "mean_citation_coverage": 1.0},
        {"gwet_ac1_non_abstained": 0.9, "mean_citation_coverage": 0.95},
    ]
    report = consistency_report(runs)
    assert report["n_runs"] == 2
    assert "gwet_ac1_non_abstained" in report["metrics"]
    assert report["metrics"]["gwet_ac1_non_abstained"]["mean"] == 0.95


def test_dummy_pipeline():
    root = Path(__file__).parents[1]
    cfg = RP5Config(
        corpus_path=root / "data" / "corpus.jsonl",
        index_type="numpy",
        reference_label_in_prompt=False,
        confidence_threshold=0.35,
    )
    pipe = RAGPipeline(cfg).load_corpus()
    card = FindingCard(
        case_id="T1",
        modality="MG",
        laterality="left",
        lesions=[Lesion(kind="mass", location="upper outer quadrant", descriptors=["circumscribed"], size_mm=12)],
        birads=2,
        pathology="benign",
    )
    result = pipe.answer(card, temperature=0.0)
    assert hasattr(result, "to_dict")


def test_api_endpoints():
    from fastapi.testclient import TestClient
    from rp5.api import app
    client = TestClient(app)
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"


def test_finding_card_dict_lesions():
    # Verify dict input to lesions is automatically converted to Lesion objects
    card = FindingCard(
        case_id="D-TEST",
        modality="MG",
        lesions=[{"kind": "mass", "location": "left", "descriptors": ["circumscribed"]}],
    )
    assert len(card.lesions) == 1
    assert isinstance(card.lesions[0], Lesion)
    assert card.lesions[0].kind == "mass"
    serialized = card.serialize()
    assert "circumscribed" in serialized


