from __future__ import annotations

import os
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from rp5.config import RP5Config
from rp5.domain import FindingCard, Lesion
from rp5.pipeline import RAGPipeline


class LesionIn(BaseModel):
    kind: str = Field(min_length=1)
    location: str = Field(min_length=1)
    size_mm: float | None = None
    descriptors: list[str] = Field(default_factory=list)


class FindingCardIn(BaseModel):
    case_id: str = Field(min_length=1)
    modality: str = "MG"
    laterality: str = ""
    breast_density: str | None = None
    lesions: list[LesionIn] = Field(default_factory=list)
    pathology: str | None = None
    reason_for_exam: str = ""
    reference_birads: int | None = Field(default=None, ge=0, le=6)

    def to_domain(self) -> FindingCard:
        return FindingCard(
            case_id=self.case_id,
            modality=self.modality,
            laterality=self.laterality,
            breast_density=self.breast_density,
            lesions=[Lesion(**x.model_dump()) for x in self.lesions],
            birads=self.reference_birads,
            pathology=self.pathology,
            reason_for_exam=self.reason_for_exam,
        )


app = FastAPI(title="RP5 BI-RADS Grounded RAG Assistant", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

_cfg = RP5Config.from_env()
_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        try:
            if _cfg.backend_mode == "gguf":
                _pipeline = RAGPipeline.from_gguf(_cfg)
            else:
                _pipeline = RAGPipeline(_cfg).load_corpus()
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"RP5 backend could not start: {exc}") from exc
    return _pipeline


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "backend": _cfg.backend_mode,
        "corpus": str(_cfg.corpus_path),
        "model": str(_cfg.generator_model),
    }


@app.post("/api/analyze")
def analyze(card: FindingCardIn) -> dict[str, Any]:
    try:
        result = get_pipeline().answer(card.to_domain(), temperature=0.0)
        return result.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(exc)}") from exc


@app.get("/")
def index():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rp5.api:app", host=os.getenv("RP5_HOST", "127.0.0.1"), port=int(os.getenv("RP5_PORT", "8000")), reload=False)
