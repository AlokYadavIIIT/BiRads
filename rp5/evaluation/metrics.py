from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable, Sequence


def ndcg_at_k(ranked: Sequence[str], rel: dict[str, int], k: int) -> float:
    ranked = list(ranked[:k])
    if not ranked:
        return 0.0
    dcg = sum(rel.get(item, 0) / math.log2(i + 2) for i, item in enumerate(ranked))
    ideal_values = sorted(rel.values(), reverse=True)[:k]
    idcg = sum(v / math.log2(i + 2) for i, v in enumerate(ideal_values))
    return dcg / idcg if idcg else 0.0


def recall_at_k(ranked: Sequence[str], rel: dict[str, int], k: int) -> float:
    relevant = {key for key, value in rel.items() if value > 0}
    if not relevant:
        return 0.0
    return len(relevant.intersection(ranked[:k])) / len(relevant)


def mrr(ranked_lists: Sequence[Sequence[str]], rel: dict[str, int]) -> float:
    reciprocal = []
    relevant = {key for key, value in rel.items() if value > 0}
    for ranked in ranked_lists:
        rr = 0.0
        for i, item in enumerate(ranked, 1):
            if item in relevant:
                rr = 1.0 / i
                break
        reciprocal.append(rr)
    return sum(reciprocal) / len(reciprocal) if reciprocal else 0.0


def gwet_ac1(r1: Sequence[str], r2: Sequence[str]) -> float:
    if len(r1) != len(r2) or not r1:
        return 0.0
    cats = sorted(set(r1) | set(r2))
    p_a = sum(a == b for a, b in zip(r1, r2)) / len(r1)
    if len(cats) <= 1:
        return 1.0
    probs = {
        c: (sum(a == c for a in r1) + sum(b == c for b in r2)) / (2 * len(r1))
        for c in cats
    }
    p_e = sum(p * (1 - p) for p in probs.values()) / (len(cats) - 1)
    if p_e >= 1:
        return 1.0 if p_a == 1.0 else 0.0
    return (p_a - p_e) / (1 - p_e)


def cohen_kappa(r1: Sequence[str], r2: Sequence[str]) -> float:
    if len(r1) != len(r2) or not r1:
        return 0.0
    n = len(r1)
    cats = sorted(set(r1) | set(r2))
    p_a = sum(a == b for a, b in zip(r1, r2)) / n
    c1, c2 = Counter(r1), Counter(r2)
    p_e = sum((c1[c] / n) * (c2[c] / n) for c in cats)
    return (p_a - p_e) / (1 - p_e) if p_e < 1 else (1.0 if p_a == 1.0 else 0.0)


def bleu(reference: str, hypothesis: str, max_n: int = 4) -> float:
    ref = reference.lower().split()
    hyp = hypothesis.lower().split()
    if not hyp or not ref:
        return 0.0
    precisions = []
    for n in range(1, max_n + 1):
        ref_ng = Counter(tuple(ref[i:i+n]) for i in range(max(0, len(ref)-n+1)))
        hyp_ng = Counter(tuple(hyp[i:i+n]) for i in range(max(0, len(hyp)-n+1)))
        denom = sum(hyp_ng.values())
        if denom == 0:
            continue
        hits = sum(min(v, ref_ng.get(g, 0)) for g, v in hyp_ng.items())
        precisions.append(hits / denom)
    if not precisions or any(p <= 0 for p in precisions):
        return 0.0
    geo = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
    bp = 1.0 if len(hyp) >= len(ref) else math.exp(1 - len(ref) / len(hyp))
    return bp * geo


def rouge_l(reference: str, hypothesis: str) -> float:
    a, b = reference.lower().split(), hypothesis.lower().split()
    if not a or not b:
        return 0.0
    prev = [0] * (len(b) + 1)
    for token_a in a:
        cur = [0]
        for j, token_b in enumerate(b, 1):
            cur.append(prev[j-1] + 1 if token_a == token_b else max(prev[j], cur[j-1]))
        prev = cur
    lcs = prev[-1]
    precision = lcs / len(b)
    recall = lcs / len(a)
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def factscore_support(claims: Iterable[str], evidence: Sequence[str]) -> float:
    evidence_tokens = set()
    for text in evidence:
        evidence_tokens.update(re.findall(r"[a-z0-9-]+", text.lower()))
    supported, total = 0, 0
    for claim in claims:
        terms = {x for x in re.findall(r"[a-z0-9-]+", claim.lower()) if len(x) > 3}
        total += 1
        if terms and terms.issubset(evidence_tokens):
            supported += 1
    return supported / total if total else 0.0


def citation_coverage(attribution_map: dict) -> float:
    if not attribution_map:
        return 0.0
    return sum(1 for attrs in attribution_map.values() if attrs and attrs[0].supported) / len(attribution_map)


def radgraph_style_entity_f1(reference: str, hypothesis: str, vocab: Sequence[str]) -> float:
    def entities(text: str) -> set[str]:
        t = text.lower()
        return {v.lower() for v in vocab if v.lower() in t}
    ref_e, hyp_e = entities(reference), entities(hypothesis)
    if not ref_e:
        return 1.0 if not hyp_e else 0.0
    inter = len(ref_e & hyp_e)
    p = inter / len(hyp_e) if hyp_e else 0.0
    r = inter / len(ref_e)
    return 2 * p * r / (p + r) if p + r else 0.0
