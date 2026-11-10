"""The 100-paper reading order, grouped into 12 phases."""

from reading_pack.catalog.early import PHASE_1, PHASE_2, PHASE_3, PHASE_4
from reading_pack.catalog.late import (
    PHASE_5, PHASE_6, PHASE_7, PHASE_8, PHASE_9, PHASE_10, PHASE_11, PHASE_12,
)
from reading_pack.catalog.model import Paper, Phase

PHASES: tuple[Phase, ...] = (
    PHASE_1, PHASE_2, PHASE_3, PHASE_4, PHASE_5, PHASE_6,
    PHASE_7, PHASE_8, PHASE_9, PHASE_10, PHASE_11, PHASE_12,
)
PAPERS: tuple[Paper, ...] = tuple(p for ph in PHASES for p in ph.papers)

assert [p.num for p in PAPERS] == list(range(1, 101)), "reading order must be 1..100"

__all__ = ["PAPERS", "PHASES", "Paper", "Phase"]
