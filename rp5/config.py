from __future__ import annotations

import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class RP5Config:
    # Corpus
    corpus_path: Path = Path("data/corpus.jsonl")
    provenance_log: Path = Path("data/provenance.jsonl")
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Retrieval
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    top_k: int = 6
    recall_floor: float = 0.85
    index_type: str = "faiss"  # faiss | numpy

    # Generation
    generator_model: str = "models/Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    alt_generator_model: str = "models/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
    backend_mode: str = "dummy"  # dummy | gguf
    n_ctx: int = 4096
    max_tokens_clin: int = 640
    max_tokens_pat: int = 640
    temperature: float = 0.2
    seed: int = 42
    few_shot_k: int = 6

    # Attribution / guard
    support_threshold: float = 0.45
    coverage_threshold: float = 0.90
    confidence_threshold: float = 0.55
    use_nli: bool = False

    # Readability
    fk_grade_target: float = 8.0
    readability_max_regens: int = 1

    # Evaluation
    temperatures: tuple[float, ...] = (0.0, 0.3, 0.7)
    consistency_runs: int = 5
    reference_label_in_prompt: bool = False
    enforce_reference_label_guard: bool = False

    @classmethod
    def from_env(cls) -> "RP5Config":
        cfg = cls()
        env = os.environ
        updates = {}
        if env.get("RP5_BACKEND"):
            updates["backend_mode"] = env["RP5_BACKEND"].lower()
        if env.get("RP5_MODEL_PATH"):
            updates["generator_model"] = env["RP5_MODEL_PATH"]
        if env.get("RP5_INDEX_TYPE"):
            updates["index_type"] = env["RP5_INDEX_TYPE"].lower()
        if env.get("RP5_TOP_K"):
            updates["top_k"] = int(env["RP5_TOP_K"])
        if env.get("RP5_CHUNK_SIZE"):
            updates["chunk_size"] = int(env["RP5_CHUNK_SIZE"])
        if env.get("RP5_CHUNK_OVERLAP"):
            updates["chunk_overlap"] = int(env["RP5_CHUNK_OVERLAP"])
        if env.get("RP5_USE_NLI"):
            updates["use_nli"] = env["RP5_USE_NLI"].lower() in {"1", "true", "yes"}
        if env.get("RP5_CONFIDENCE_THRESHOLD"):
            updates["confidence_threshold"] = float(env["RP5_CONFIDENCE_THRESHOLD"])
        elif env.get("RP5_TAU"):
            updates["confidence_threshold"] = float(env["RP5_TAU"])
        if env.get("RP5_COVERAGE_THRESHOLD"):
            updates["coverage_threshold"] = float(env["RP5_COVERAGE_THRESHOLD"])
        return replace(cfg, **updates)

    def public_dump(self) -> dict:
        return {k: str(v) for k, v in asdict(self).items()}


# Backward-compatible alias used by the professor's original draft.
RPSConfig = RP5Config
