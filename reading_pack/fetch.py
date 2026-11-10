"""Per-paper acquisition: reuse an existing file, pick up a manual download, or fetch open access."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

from reading_pack.catalog import Paper
from reading_pack.net import (
    Http, arxiv_pdf, arxiv_search, catalog_candidates, landing_pdf, openalex, semantic_scholar, source_name,
)
from reading_pack.pdf.verify import STOP, check_pdf, norm


@dataclass
class Result:
    num: int
    status: str  # downloaded | cached | manual | missing
    path: str | None = None
    source: str = ""
    url: str = ""
    pages: int = 0
    doi: str | None = None
    link: str | None = None
    note: str = ""


def file_name(paper: Paper) -> str:
    surname = "".join(w[:1].upper() + w[1:] for w in norm(paper.surname).split())
    words = [w for w in norm(paper.title).split() if w not in STOP][:4]
    short = "".join(w[:1].upper() + w[1:] for w in words)[:40]
    return f"{paper.num:03d}_{surname}{paper.year}_{short}.pdf"


class Ledger:
    """Where each file came from, kept next to the papers so re-runs can report it."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: dict[str, dict] = json.loads(path.read_text()) if path.exists() else {}

    def get(self, num: int) -> dict:
        return self.data.get(str(num), {})

    def put(self, result: Result) -> None:
        self.data[str(result.num)] = asdict(result)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True))
        tmp.replace(self.path)


class Fetcher:
    def __init__(self, papers_dir: Path, http: Http, ledger: Ledger, log=print) -> None:
        self.papers_dir = papers_dir
        self.manual_dir = papers_dir / "manual"
        self.http = http
        self.ledger = ledger
        self.log = log

    def _first(self, folder: Path, num: int) -> Path | None:
        hits = sorted(folder.glob(f"{num:03d}_*.pdf")) if folder.is_dir() else []
        return hits[0] if hits else None

    def _save(self, data: bytes, target: Path) -> None:
        tmp = target.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.replace(target)

    def acquire(self, paper: Paper) -> Result:
        local = self.acquire_offline(paper)
        return local if local.status != "missing" else self._download(paper, self._target(paper))

    def _target(self, paper: Paper) -> Path:
        return self.papers_dir / file_name(paper)

    def acquire_offline(self, paper: Paper) -> Result:
        """Use what is on disk: an earlier download or a manual copy; otherwise report missing."""
        if existing := self._first(self.papers_dir, paper.num):
            prev = self.ledger.get(paper.num)
            return Result(paper.num, "cached", str(existing), prev.get("source", "earlier run"),
                          prev.get("url", ""), prev.get("pages", 0), prev.get("doi"),
                          prev.get("link"), prev.get("note", ""))
        if manual := self._first(self.manual_dir, paper.num):
            return self._take_manual(paper, manual, self._target(paper))
        prev = self.ledger.get(paper.num)
        doi = prev.get("doi") or paper.doi
        return Result(paper.num, "missing", doi=doi,
                      link=prev.get("link") or (f"https://doi.org/{doi}" if doi else None),
                      note=prev.get("note", "not fetched yet"))

    def _take_manual(self, paper: Paper, manual: Path, target: Path) -> Result:
        ok, reason, pages = check_pdf(manual.read_bytes(), paper.title)
        shutil.copyfile(manual, target)
        note = "" if ok else f"warning: {reason}; kept because you supplied it"
        self.log(f"  manual copy {manual.name} ({reason})")
        return Result(paper.num, "manual", str(target), "manual download (university library)",
                      str(manual), pages, paper.doi, note=note)

    def _download(self, paper: Paper, target: Path) -> Result:
        tried: set[str] = set()
        attempts: list[str] = []

        def attempt(url: str, via: str) -> Result | None:
            if url in tried:
                return None
            tried.add(url)
            r = self.http.get(url)
            if r is None:
                attempts.append(f"{url}: no response")
                return None
            if r.status_code != 200:
                attempts.append(f"{url}: HTTP {r.status_code}")
                return None
            ok, reason, pages = check_pdf(r.content, paper.title)
            if not ok and (pdf_url := landing_pdf(r)) and pdf_url not in tried:
                attempts.append(f"{url}: landing page, following {pdf_url}")
                return attempt(pdf_url, via)
            if not ok:
                attempts.append(f"{url}: {reason}")
                return None
            self._save(r.content, target)
            self.log(f"  saved {target.name} ({pages} p) from {url}")
            return Result(paper.num, "downloaded", str(target), source_name(url, via), url, pages,
                          paper.doi)

        for url, via in catalog_candidates(paper):
            if res := attempt(url, via):
                return res
        meta = semantic_scholar(self.http, paper)
        if meta.error:
            attempts.append(f"Semantic Scholar: {meta.error}")
        openalex(self.http, paper, meta)
        for url in meta.oa_urls:
            if res := attempt(url, "Semantic Scholar / OpenAlex open-access listing"):
                return res
        if meta.arxiv and (res := attempt(arxiv_pdf(meta.arxiv), "Semantic Scholar arXiv id")):
            return res
        if (aid := arxiv_search(self.http, paper)) and (res := attempt(arxiv_pdf(aid), "arXiv search")):
            return res
        doi = meta.doi or paper.doi
        link = f"https://doi.org/{doi}" if doi else meta.link
        self.log(f"  MISSING: no verified open-access PDF ({len(attempts)} tried)")
        return Result(paper.num, "missing", doi=doi, link=link or meta.link,
                      note="; ".join(attempts) or "no open-access copy listed")
