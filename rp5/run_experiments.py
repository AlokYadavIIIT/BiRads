from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from rp5.audit.audit_sets import make_conflicting, make_distractor, make_out_of_corpus
from rp5.audit.hallucination_audit import run_audit
from rp5.config import RP5Config
from rp5.domain import Abstention, FindingCard
from rp5.evaluation.consistency import consistency_report
from rp5.evaluation.metrics import citation_coverage, gwet_ac1
from rp5.generation.llm_backend import DummyBackend
from rp5.pipeline import RAGPipeline
from rp5.retrieval.index import load_chunks
from rp5.retrieval.tuning import load_judgments, tune


def _load_cards(path: Path) -> list[FindingCard]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            obj = json.loads(line)
            obj["lesions"] = [
                x if isinstance(x, dict) else x.__dict__ for x in obj.get("lesions", [])
            ]
            from rp5.domain import Lesion
            obj["lesions"] = [Lesion(**x) if isinstance(x, dict) else x for x in obj["lesions"]]
            rows.append(FindingCard(**obj))
    return rows


def build_pipeline(cfg: RP5Config) -> RAGPipeline:
    if cfg.backend_mode == "gguf":
        return RAGPipeline.from_gguf(cfg)
    return RAGPipeline(cfg, backend=DummyBackend()).load_corpus()


def evaluate(cfg: RP5Config, pipeline: RAGPipeline, cards: list[FindingCard], out: Path) -> dict:
    rows = []
    refs, preds = [], []
    abstained = 0
    covers, grades, latencies = [], [], []
    for card in cards:
        result = pipeline.answer(card, temperature=0.0)
        if isinstance(result, Abstention):
            abstained += 1
            rows.append({"case_id": card.case_id, "abstained": True, "reason": result.reason})
            continue
        refs.append(str(card.birads) if card.birads is not None else "0")
        preds.append(str(result.clinician_draft["final_assessment"]))
        covers.append(result.coverage)
        grades.append(result.patient_fk_grade)
        latencies.append(result.latency_ms["total_ms"])
        rows.append({
            "case_id": card.case_id,
            "abstained": False,
            "reference_birads": card.birads,
            "predicted_birads": result.clinician_draft["final_assessment"],
            "citation_coverage": result.coverage,
            "patient_fk_grade": result.patient_fk_grade,
            "latency_ms": result.latency_ms,
        })
    report = {
        "n_vignettes": len(cards),
        "n_non_abstained": len(refs),
        "abstention_rate": abstained / len(cards) if cards else 0.0,
        "gwet_ac1_non_abstained": gwet_ac1(refs, preds) if refs else None,
        "mean_citation_coverage": sum(covers) / len(covers) if covers else 0.0,
        "mean_patient_fk_grade": sum(grades) / len(grades) if grades else 0.0,
        "mean_latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
        "reference_label_in_prompt": cfg.reference_label_in_prompt,
        "cases": rows,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description="RP5 research experiment runner")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_build = sub.add_parser("build-corpus")
    p_build.add_argument("--lexicon", nargs="+", required=True)
    p_build.add_argument("--guidance", nargs="+", required=True)
    p_build.add_argument("--templates", nargs="+", required=True)
    p_build.add_argument("--examples", nargs="+", required=True)
    p_tune = sub.add_parser("tune-retrieval")
    p_tune.add_argument("--judgments", required=True)
    p_tune.add_argument("--docs-json", required=True)
    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("--vignettes", required=True)
    p_eval.add_argument("--out", default="results/evaluation.json")
    p_audit = sub.add_parser("audit")
    p_audit.add_argument("--vignettes", required=True)
    p_audit.add_argument("--out", default="results/audit.json")
    p_cons = sub.add_parser("consistency")
    p_cons.add_argument("--vignettes", required=True)
    p_cons.add_argument("--out", default="results/consistency.json")
    args = parser.parse_args()

    cfg = RP5Config.from_env()
    if args.cmd == "build-corpus":
        from rp5.corpus.build_corpus import build
        chunks = build(
            cfg,
            [Path(x) for x in args.lexicon],
            [Path(x) for x in args.guidance],
            [Path(x) for x in args.templates],
            [Path(x) for x in args.examples],
            "expert-revised from disclosed publications",
        )
        print(f"Built {len(chunks)} chunks at {cfg.corpus_path}")
        return

    if args.cmd == "tune-retrieval":
        # docs-json is a JSON array of CorpusDocument objects.
        from rp5.domain import CorpusDocument
        docs = [CorpusDocument(**x) for x in json.loads(Path(args.docs_json).read_text(encoding="utf-8"))]
        judgments = load_judgments(Path(args.judgments))
        print(json.dumps(tune(cfg, docs, judgments), indent=2))
        return

    cards = _load_cards(Path(args.vignettes))
    pipeline = build_pipeline(cfg)
    if args.cmd == "evaluate":
        evaluate(cfg, pipeline, cards, Path(args.out))
    elif args.cmd == "audit":
        rng = random.Random(cfg.seed)
        probes = make_out_of_corpus(cards, rng) + make_conflicting(cards, rng) + make_distractor(cards, rng)
        report = run_audit(pipeline, probes, Path("results/audit_cases.jsonl"))
        Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
    elif args.cmd == "consistency":
        runs = []
        for run_id in range(cfg.consistency_runs):
            for temp in cfg.temperatures:
                report = evaluate(cfg, pipeline, cards, Path(f"results/run_{run_id}_{temp}.json"))
                runs.append({
                    "gwet_ac1_non_abstained": report.get("gwet_ac1_non_abstained") or 0.0,
                    "abstention_rate": report["abstention_rate"],
                    "mean_citation_coverage": report["mean_citation_coverage"],
                    "mean_patient_fk_grade": report["mean_patient_fk_grade"],
                    "mean_latency_ms": report["mean_latency_ms"],
                })
        Path(args.out).write_text(json.dumps(consistency_report(runs), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
