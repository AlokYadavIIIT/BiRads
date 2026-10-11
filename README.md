# RP5 — BI-RADS-Grounded RAG Assistant

This repository is a research prototype implementing the professor's RP5 design: four-stratum corpus → section-aware chunking → sentence-transformer embeddings → FAISS/NumPy retrieval → optional S4 few-shot examples → dual clinician/patient generation → attribution → guard/abstention → hallucination audit → evaluation.

## Important research boundary

The included `data/corpus/*/demo_*` files are **synthetic smoke-test content**. They are not an ACR/BI-RADS clinical source and must not be used for clinical decisions. Replace them with your licence-checked, professor-approved corpus before reporting results.

The main workflow deliberately hides any evaluation/reference BI-RADS label from the generation prompt by default. This prevents label leakage when measuring BI-RADS agreement. The reference label can be enabled for a separate report-rewriting experiment.

## Architecture

```text
                    ┌───────────────────────────┐
                    │        Finding Card       │
                    │ modality/laterality/      │
                    │ lesions/descriptors/...   │
                    └──────────────┬────────────┘
                                   │
                         serialize query (q)
                                   │
                  ┌────────────────▼─────────────────┐
                  │ Retrieval                        │
                  │ MiniLM → FAISS/NumPy → top-k=6 │
                  └────────────────┬─────────────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
        S4 few-shot examples                    Retrieved evidence
                │                                     │
                └──────────────────┬──────────────────┘
                                   │
                       ┌───────────▼───────────┐
                       │  Clinician Head       │
                       │  strict JSON schema   │
                       └───────────┬───────────┘
                                   │
                       ┌───────────▼───────────┐
                       │ Patient Head           │
                       │ FK ≤ 8 + regeneration │
                       └───────────┬───────────┘
                                   │
                       ┌───────────▼───────────┐
                       │ Attribution            │
                       │ lexical + embedding   │
                       │ + optional NLI        │
                       └───────────┬───────────┘
                                   │
                       ┌───────────▼───────────┐
                       │ Guard Agent            │
                       │ BI-RADS / citation    │
                       │ contradiction / tau   │
                       └───────────┬───────────┘
                                   │
                         PASS ─────┴───── ABSTAIN
``` 

## 1. Setup on Windows

Use Python 3.10–3.12 for the smoothest scientific-package experience.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Smoke test without an LLM

Build the synthetic demo corpus:

```powershell
python -m rp5.run_experiments build-corpus `
  --lexicon data/corpus/S1_lexicon/demo_lexicon.txt `
  --guidance data/corpus/S2_guidance/demo_guidance.txt `
  --templates data/corpus/S3_templates/demo_templates.txt `
  --examples data/corpus/S4_examples/demo_examples.txt
```

Run:

```powershell
$env:RP5_BACKEND="dummy"
python -m rp5.run_experiments evaluate --vignettes data/demo/vignettes.jsonl
```

Run the adversarial audit:

```powershell
python -m rp5.run_experiments audit --vignettes data/demo/vignettes.jsonl
```

## 3. Real local GGUF model

Put the professor-approved GGUF file under `models/`, then:

```powershell
$env:RP5_BACKEND="gguf"
$env:RP5_MODEL_PATH="models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
python -m rp5.api
```

Open `http://127.0.0.1:8000`.

The same API also supports:

```text
POST /api/analyze
GET  /api/health
```

## 4. Corpus policy

- **S1 Lexicon:** professor-approved BI-RADS lexicon text.
- **S2 Guidance:** ACR practice parameters and report guidance.
- **S3 Templates:** locally normalized structured-report shells.
- **S4 Examples:** de-identified / disclosed / expert-reviewed examples.

Keep a provenance log for every document and never mix patient-facing examples into the authoritative lexicon strata.

## 5. Evaluation protocol

Recommended order:

1. Freeze the 100-query retrieval tuning set.
2. Tune chunk size ∈ {256,512,768,1024}, overlap ∈ {32,64,128}, top-k ∈ {4,6,8}, and optionally MiniLM vs MPNet.
3. Lock the selected configuration.
4. Run Tier-1 few-shot generation first.
5. Perform the three adversarial audit families.
6. Run the clinician review on 100 drafts.
7. Only then consider the optional LoRA ablation.
8. Report abstention and hallucination together.

Use:

```text
nDCG@k / recall@k / MRR
Gwet AC1 / Cohen κ
BLEU / ROUGE-L
FactScore-style support
RadGraph-style entity F1 proxy
Flesch–Kincaid
citation coverage
hallucination rate
abstention rate
latency / peak RAM / output consistency
```

## 6. What was strengthened from the supplied draft

The professor's original package already specifies the core RP5 stages and CPU-first design. This implementation adds engineering safeguards around those stages: explicit evaluation-label isolation, actual re-chunking in retrieval tuning, NumPy fallback when FAISS is unavailable, stricter schema validation, explicit patient attribution, timing fixes, more complete guard checks, and a local FastAPI/UI layer.

## 7. Medical-safety statement

This is a research/demonstration assistant for drafting and explanation. It is not a diagnostic system and does not replace a radiologist. Any real clinical corpus, patient data, or study involving people must follow the professor's review process, institutional requirements, and applicable privacy/ethics approvals.
