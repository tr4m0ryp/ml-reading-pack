"""missing.txt (what to fetch through the library) and report.md (what came from where)."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from reading_pack.catalog import Phase
from reading_pack.fetch import Result


def write_missing(path: Path, phases: tuple[Phase, ...], results: dict[int, Result]) -> int:
    lines = ["# Papers without a verified legal open-access PDF.",
             "# Download each through your university library and save it as",
             "#   papers/manual/NNN_<anything>.pdf   (NNN = the number below)",
             "# then re-run: python build_reading_pack.py", ""]
    count = 0
    for ph in phases:
        for p in ph.papers:
            r = results[p.num]
            if r.status != "missing":
                continue
            count += 1
            lines += [f"{p.num:03d}  {p.authors} ({p.year}). {p.title}",
                      f"     DOI:  {r.doi or 'unknown'}",
                      f"     Link: {r.link or 'https://scholar.google.com/scholar?q=' + p.title.replace(' ', '+')}",
                      ""]
    path.write_text("\n".join(lines) if count else "# Nothing missing: every paper was found.\n")
    return count


def write_report(path: Path, phases: tuple[Phase, ...], results: dict[int, Result],
                 total_pages: int | None, http_requests: int) -> None:
    rs = [results[p.num] for ph in phases for p in ph.papers]
    have = [r for r in rs if r.status != "missing"]
    by_source = Counter(r.source.split(",")[0] for r in have)
    out = [f"# ML Top 100 reading pack: build report",
           "",
           f"Built {datetime.now():%Y-%m-%d %H:%M}. **{len(have)} of {len(rs)}** papers included"
           + (f"; merged PDF has {total_pages} pages." if total_pages else "."),
           f"HTTP requests this run: {http_requests} (throttled to one per 3 s).",
           "",
           "## Sources",
           ""]
    out += [f"- {src}: {n}" for src, n in by_source.most_common()]
    out += ["", "## Papers", "", "| # | Paper | Status | Source | Pages |", "|---|---|---|---|---|"]
    titles = {p.num: f"{p.authors} {p.year}: {p.title}" for ph in phases for p in ph.papers}
    for r in rs:
        src = f"[{r.source}]({r.url})" if r.url.startswith("http") else (r.source or "")
        warn = f" ({r.note})" if r.note and r.status != "missing" else ""
        out.append(f"| {r.num:03d} | {titles[r.num].replace('|', '/')} | {r.status}{warn} | "
                   f"{src} | {r.pages or ''} |")
    skipped = [r for r in rs if r.status == "missing"]
    if skipped:
        out += ["", "## Skipped (no legal open-access PDF verified)", ""]
        for r in skipped:
            out.append(f"- **{r.num:03d}** {titles[r.num]}. DOI {r.doi or 'unknown'}.")
            out.append(f"  Tried: {r.note}")
    path.write_text("\n".join(out) + "\n")
