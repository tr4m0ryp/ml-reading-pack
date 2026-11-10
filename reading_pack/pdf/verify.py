"""Check that downloaded bytes are a real PDF of the expected paper (title on page 1)."""

from __future__ import annotations

import io
import logging
import re
import unicodedata

from pypdf import PdfReader

logging.getLogger("pypdf").setLevel(logging.ERROR)

STOP = {"a", "an", "the", "of", "and", "for", "with", "via", "in", "on", "to", "by", "from",
        "using", "any", "its", "their", "at", "is", "as", "be"}
TITLE_PAGES = 2  # page 1, plus page 2 for publisher cover sheets


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"-\s*\n\s*", "", text.lower())  # re-join words hyphenated across lines
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _words(title: str) -> list[str]:
    return [w for w in norm(title).split() if w not in STOP]


def title_similarity(found: str, expected: str) -> float:
    """Share of the expected title's content words present in `found` (1.0 = all present)."""
    words = _words(expected)
    if not words:
        return 0.0
    hay = norm(found)
    if norm(expected).replace(" ", "") in hay.replace(" ", ""):
        return 1.0
    present = set(hay.split())
    squashed = hay.replace(" ", "")
    hits = sum(1 for w in words if w in present or (len(w) > 4 and w in squashed))
    return hits / len(words)


def check_pdf(data: bytes, title: str) -> tuple[bool, str, int]:
    """Return (ok, reason, page_count)."""
    if b"%PDF" not in data[:1024]:
        kind = "HTML page" if b"<html" in data[:2048].lower() else "non-PDF content"
        return False, f"{kind}, not a PDF", 0
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            reader.decrypt("")
        pages = len(reader.pages)
        text = ""
        for page in reader.pages[:TITLE_PAGES]:
            try:
                text += "\n" + (page.extract_text() or "")
            except Exception:  # noqa: BLE001 - odd fonts must not abort the run
                continue
    except Exception as exc:  # noqa: BLE001
        return False, f"unreadable PDF ({type(exc).__name__})", 0
    if pages == 0:
        return False, "PDF has no pages", 0
    if not norm(text):
        return False, "no text layer on page 1 (scanned?), title not verifiable", pages
    score = title_similarity(text, title)
    if score < 0.8:
        return False, f"title not found on page 1 (match {score:.0%})", pages
    return True, "title verified", pages
