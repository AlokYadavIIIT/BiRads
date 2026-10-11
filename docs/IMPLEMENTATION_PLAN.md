# RP5 implementation plan

## Phase 1 — corpus and data contract
Create the four strata exactly as specified by the methodology. Keep source, licence/status, transformation note and reviewer status for every document. Build the `FindingCard` JSON contract and keep evaluation/reference labels separate from model-visible input.

## Phase 2 — retrieval
Run section-aware chunking. Freeze the 100-question judgment set. Compare MiniLM and, where resources permit, MPNet. Tune chunk size, overlap and top-k. Save the winning configuration and do not retune on the final test set.

## Phase 3 — generation
Use Tier 1 few-shot prompting first. Require strict JSON output. Log the raw model response, parsed draft and validation failures. Do not begin LoRA before the first hallucination/citation audit gate.

## Phase 4 — attribution and guard
Generate a sentence-level attribution map. Enforce citation coverage, descriptor allowlisting, recommendation/category consistency, internal contradiction checks, readability ceiling and confidence threshold. Treat ABSTAIN as a valid output.

## Phase 5 — audit and evaluation
Run the three adversarial families. Record auto-verdicts and manual-review hooks. Evaluate retrieval, BI-RADS agreement, factual support, readability, latency, abstention and consistency. Clinician reviewers should work blinded to system identity during comparative scoring.

## Phase 6 — paper-ready packaging
Export a reproducibility manifest containing model name/path hash, configuration, corpus version, seed, retrieval tuning result, audit set version, evaluation results and code commit. Report measured results, including failures and abstentions, rather than only successful cases.

## Suggested team split

- Member 1: corpus/provenance + data validation
- Member 2: embeddings/retrieval/tuning
- Member 3: LLM generation + JSON enforcement
- Member 4: guard/attribution/audit
- Member 5: FastAPI UI + evaluation dashboards + packaging

All members should use the same frozen configuration file for final experiments.
