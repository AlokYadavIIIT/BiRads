from __future__ import annotations

from dataclasses import dataclass
from random import Random

from rp5.domain import FindingCard, Lesion

FAKE_DESCRIPTORS = [
    "hyperlucent spiculated galactocele",
    "reticular lobular confluence",
    "pseudocystic trabeculation",
]


@dataclass
class Probe:
    qid: str
    family: str
    card: FindingCard


def make_out_of_corpus(cards: list[FindingCard], rng: Random) -> list[Probe]:
    return [
        Probe(
            qid=f"OOC-{i}",
            family="out_of_corpus",
            card=FindingCard(
                case_id=f"OOC-{i}",
                modality=c.modality,
                lesions=[Lesion(kind="mass", location="left breast", descriptors=[rng.choice(FAKE_DESCRIPTORS)])],
                birads=None,
            ),
        )
        for i, c in enumerate(cards)
    ]


def make_conflicting(cards: list[FindingCard], rng: Random) -> list[Probe]:
    return [
        Probe(
            qid=f"CONF-{i}",
            family="conflicting",
            card=FindingCard(
                case_id=f"CONF-{i}",
                modality=c.modality,
                lesions=[Lesion(kind="mass", location="right breast", descriptors=["spiculated"])],
                birads=rng.choice([4, 5]),
                pathology="benign",
            ),
        )
        for i, c in enumerate(cards)
    ]


def make_distractor(cards: list[FindingCard], rng: Random) -> list[Probe]:
    return [Probe(f"DIST-{i}", "distractor", c) for i, c in enumerate(cards)]
