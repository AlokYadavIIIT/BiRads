from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from rp5.config import RP5Config
from rp5.corpus.chunker import Chunker
from rp5.domain import CorpusDocument


def load_stratum(paths: list[Path], stratum: str, transform_note: str = "") -> list[CorpusDocument]:
    docs: list[CorpusDocument] = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
        docs.append(
            CorpusDocument(
                doc_id=f"{stratum.lower()}:{path.stem}",
                stratum=stratum,
                source=str(path),
                text=path.read_text(encoding="utf-8"),
                transform_note=transform_note,
            )
        )
    return docs


def build(
    cfg: RP5Config,
    lexicon: list[Path],
    guidance: list[Path],
    templates: list[Path],
    examples: list[Path],
    example_note: str,
) -> list:
    docs = (
        load_stratum(lexicon, "S1")
        + load_stratum(guidance, "S2")
        + load_stratum(templates, "S3")
        + load_stratum(examples, "S4", example_note)
    )
    cfg.provenance_log.parent.mkdir(parents=True, exist_ok=True)
    with cfg.provenance_log.open("w", encoding="utf-8") as fh:
        for doc in docs:
            fh.write(
                json.dumps(
                    {
                        "doc_id": doc.doc_id,
                        "stratum": doc.stratum,
                        "source": doc.source,
                        "transform": doc.transform_note,
                        "logged_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
                + "\n"
            )

    chunks = Chunker(cfg).chunk_all(docs)
    cfg.corpus_path.parent.mkdir(parents=True, exist_ok=True)
    with cfg.corpus_path.open("w", encoding="utf-8") as fh:
        for chunk in chunks:
            fh.write(json.dumps(chunk.__dict__) + "\n")
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the four-stratum RP5 corpus")
    parser.add_argument("--lexicon", nargs="+", required=True)
    parser.add_argument("--guidance", nargs="+", required=True)
    parser.add_argument("--templates", nargs="+", required=True)
    parser.add_argument("--examples", nargs="+", required=True)
    parser.add_argument("--example-note", default="expert-revised from disclosed open publications")
    args = parser.parse_args()
    chunks = build(
        RP5Config.from_env(),
        [Path(x) for x in args.lexicon],
        [Path(x) for x in args.guidance],
        [Path(x) for x in args.templates],
        [Path(x) for x in args.examples],
        args.example_note,
    )
    print(f"built {len(chunks)} chunks")


if __name__ == "__main__":
    main()
