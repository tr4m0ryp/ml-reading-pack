"""Assemble cover + contents + (divider, papers)* into one PDF with Phase > Paper bookmarks."""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from reading_pack.catalog import Phase
from reading_pack.fetch import Result
from reading_pack.pdf import frontmatter as fm
from reading_pack.videos import load_videos


def _pages(data: bytes) -> int:
    return len(PdfReader(io.BytesIO(data)).pages)


def _paper_blocks(phases: tuple[Phase, ...], results: dict[int, Result]) -> dict[int, tuple[object, int]]:
    """num -> (source, page_count); source is a path, or placeholder bytes when unusable."""
    blocks: dict[int, tuple[object, int]] = {}
    for ph in phases:
        for p in ph.papers:
            res = results[p.num]
            if res.path:
                try:
                    blocks[p.num] = (res.path, len(PdfReader(res.path).pages))
                    continue
                except Exception as exc:  # noqa: BLE001
                    res.note = f"file unreadable at merge ({type(exc).__name__}); placeholder used"
                    res.status = "missing"
            data = fm.placeholder(p, res.doi, res.link, "no verified open-access PDF")
            blocks[p.num] = (data, _pages(data))
    return blocks


def assemble(out: Path, phases: tuple[Phase, ...], results: dict[int, Result]) -> int:
    blocks = _paper_blocks(phases, results)
    missing = {n for n, r in results.items() if r.status == "missing"}
    included = len(results) - len(missing)
    cover = fm.cover(phases, included, len(results), date.today().isoformat())
    videos = load_videos()
    dividers = {ph.num: fm.divider(ph, videos) for ph in phases}

    toc_pages, phase_at, paper_at = 1, {}, {}
    for _ in range(4):  # the TOC length decides every later page number; iterate to a fixed point
        page = _pages(cover) + toc_pages + 1
        for ph in phases:
            phase_at[ph.num] = page
            page += _pages(dividers[ph.num])
            for p in ph.papers:
                paper_at[p.num] = page
                page += blocks[p.num][1]
        toc = fm.toc(phases, phase_at, paper_at, missing, videos)
        if _pages(toc) == toc_pages:
            break
        toc_pages = _pages(toc)

    writer = PdfWriter()
    writer.append(PdfReader(io.BytesIO(cover)), import_outline=False)
    writer.add_outline_item("Cover", 0)
    toc_start = len(writer.pages)
    writer.append(PdfReader(io.BytesIO(toc)), import_outline=False)
    writer.add_outline_item("Contents", toc_start)  # bookmarks need their page to exist first
    for ph in phases:
        div_start = len(writer.pages)
        writer.append(PdfReader(io.BytesIO(dividers[ph.num])), import_outline=False)
        parent = writer.add_outline_item(f"Phase {ph.num}: {ph.name}", div_start)
        for p in ph.papers:
            start = len(writer.pages)
            src, _ = blocks[p.num]
            reader = PdfReader(io.BytesIO(src)) if isinstance(src, bytes) else PdfReader(src)
            writer.append(reader, import_outline=False)
            mark = f"{p.num:03d} {p.title}" + (" (missing)" if p.num in missing else "")
            writer.add_outline_item(mark, start, parent=parent)
    assert len(writer.pages) == page - 1, "page numbers in the contents drifted"
    writer.page_mode = "/UseOutlines"
    tmp = out.with_suffix(".part")
    with tmp.open("wb") as fh:
        writer.write(fh)
    tmp.replace(out)
    return len(writer.pages)
