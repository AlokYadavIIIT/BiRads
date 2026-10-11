from __future__ import annotations

import re
from dataclasses import replace
from typing import Iterable

from rp5.config import RP5Config
from rp5.domain import Chunk, CorpusDocument


_SECTION_HEADING = re.compile(
    r"^(FINDINGS|IMPRESSION|ASSESSMENT|RECOMMENDATION|TECHNIQUE|HISTORY|INDICATION)\b",
    re.I,
)
_LEXICON_HEADING = re.compile(r"^([A-Z][A-Za-z0-9 /()\-]{2,55})\s*$")


def _tokenize(text: str) -> list[str]:
    try:
        import tiktoken
        return tiktoken.get_encoding("cl100k_base").encode(text)
    except Exception:
        return re.findall(r"\S+", text)


def _detokenize(tokens: list[str]) -> str:
    if tokens and isinstance(tokens[0], int):
        try:
            import tiktoken
            return tiktoken.get_encoding("cl100k_base").decode(tokens)
        except Exception:
            return " ".join(str(x) for x in tokens)
    return " ".join(tokens)


def _split_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    cur_name, cur_body = "PREAMBLE", []
    for line in text.splitlines():
        stripped = line.strip()
        if _SECTION_HEADING.match(stripped):
            if cur_body:
                sections.append((cur_name, "\n".join(cur_body).strip()))
            cur_name, cur_body = stripped.upper(), []
        else:
            cur_body.append(line)
    if cur_body:
        sections.append((cur_name, "\n".join(cur_body).strip()))
    return [(n, b) for n, b in sections if b]


class Chunker:
    def __init__(self, cfg: RP5Config):
        self.cfg = cfg

    def with_window(self, chunk_size: int, overlap: int) -> "Chunker":
        return Chunker(replace(self.cfg, chunk_size=chunk_size, chunk_overlap=overlap))

    def chunk_document(self, doc: CorpusDocument) -> list[Chunk]:
        if doc.stratum == "S1":
            return self._chunk_lexicon(doc)
        return self._chunk_sections(doc)

    def _window_chunks(self, doc: CorpusDocument, section: str, text: str) -> list[Chunk]:
        tokens = _tokenize(text)
        if not tokens:
            return []
        size = self.cfg.chunk_size
        step = max(1, size - self.cfg.chunk_overlap)
        chunks: list[Chunk] = []
        if len(tokens) <= size:
            chunks.append(self._make(doc, section, tokens))
            return chunks
        for i in range(0, len(tokens), step):
            part = tokens[i:i + size]
            if not part:
                break
            chunks.append(self._make(doc, f"{section}[part-{i//step + 1}]", part))
        return chunks

    def _chunk_lexicon(self, doc: CorpusDocument) -> list[Chunk]:
        entries: list[tuple[str, str]] = []
        name, body = "PREAMBLE", []
        for line in doc.text.splitlines():
            stripped = line.strip()
            if stripped and _LEXICON_HEADING.match(stripped) and len(stripped) < 60:
                if body:
                    entries.append((name, "\n".join(body).strip()))
                name, body = stripped, []
            else:
                body.append(line)
        if body:
            entries.append((name, "\n".join(body).strip()))

        out: list[Chunk] = []
        for entry_name, entry_body in entries:
            if not entry_body:
                continue
            out.extend(self._window_chunks(doc, entry_name, f"{entry_name}\n{entry_body}"))
        return out

    def _chunk_sections(self, doc: CorpusDocument) -> list[Chunk]:
        out: list[Chunk] = []
        for section, body in _split_sections(doc.text):
            out.extend(self._window_chunks(doc, section, body))
        return out

    def _make(self, doc: CorpusDocument, section: str, tokens: list[str]) -> Chunk:
        return Chunk(
            chunk_id=f"{doc.doc_id}::{section}::{len(tokens)}",
            doc_id=doc.doc_id,
            stratum=doc.stratum,
            section=section,
            text=_detokenize(tokens),
            token_count=len(tokens),
        )

    def chunk_all(self, docs: Iterable[CorpusDocument]) -> list[Chunk]:
        out: list[Chunk] = []
        for doc in docs:
            out.extend(self.chunk_document(doc))
        return out
