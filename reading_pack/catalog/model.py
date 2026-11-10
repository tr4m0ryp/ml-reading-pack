"""Catalog records: a phase of the reading order and the papers in it."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Paper:
    num: int
    surname: str  # first author's surname, used in the file name
    authors: str  # as shown in the table of contents
    year: int
    title: str  # full official title, used to verify page 1
    arxiv: str | None = None
    urls: tuple[str, ...] = ()  # proceedings / author / institutional copies, tried first
    doi: str | None = None

    @property
    def label(self) -> str:
        return f"{self.num:03d} {self.authors} {self.year}: {self.title}"


@dataclass(frozen=True)
class Phase:
    num: int
    name: str
    why: str
    papers: tuple[Paper, ...] = field(default_factory=tuple)


P = Paper
