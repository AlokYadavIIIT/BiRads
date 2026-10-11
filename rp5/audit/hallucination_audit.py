from __future__ import annotations

import json
from pathlib import Path

from rp5.attribution.aligner import split_sentences
from rp5.domain import Abstention
from rp5.evaluation.metrics import factscore_support


def run_audit(pipeline, probes, out_path: Path) -> dict:
    records = []
    claims_total = 0
    unsupported_total = 0
    abstentions = 0

    for probe in probes:
        result = pipeline.answer(
            probe.card,
            temperature=0.0,
            perturb=(probe.family == "distractor"),
        )
        if isinstance(result, Abstention):
            abstentions += 1
            records.append({
                "qid": probe.qid,
                "family": probe.family,
                "abstained": True,
                "reason": result.reason,
                "manual_adjudication": None,
            })
            continue

        claims = split_sentences(result.clinician_text)
        evidence = [p.chunk.text for p in pipeline.last_passages] + [probe.card.serialize(False)]
        support = factscore_support(claims, evidence)
        unsupported = round((1 - support) * len(claims))
        claims_total += len(claims)
        unsupported_total += unsupported
        record = {
            "qid": probe.qid,
            "family": probe.family,
            "abstained": False,
            "n_claims": len(claims),
            "auto_support": support,
            "unsupported_claims": unsupported,
            "manual_adjudication": None,
        }

        if probe.family == "distractor":
            record["clinician_text"] = result.clinician_text
            record["claims"] = claims
            record["evidence"] = evidence

        records.append(record)

    rate = unsupported_total / claims_total if claims_total else 0.0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for row in records:
            fh.write(json.dumps(row) + "\n")
    return {
        "hallucination_rate_auto": round(rate, 4),
        "abstention_rate": round(abstentions / len(probes), 4) if probes else 0.0,
        "unsupported_claims": unsupported_total,
        "total_claims": claims_total,
        "probes": len(probes),
        "out_file": str(out_path),
    }
