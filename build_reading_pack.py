#!/usr/bin/env python3
"""Build ML_Top100_Reading_Order.pdf from legal open-access copies of 100 ML papers.

Re-runnable: papers already in ./papers are kept, files you drop into ./papers/manual/NNN_*.pdf
are picked up, and only the rest is fetched (arXiv, open proceedings, author pages, Semantic
Scholar openAccessPdf). Requests are throttled to one per 3 s. Optional environment:
READING_PACK_CONTACT (an email appended to the User-Agent), S2_API_KEY (Semantic Scholar key).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reading_pack.catalog import PAPERS, PHASES
from reading_pack.fetch import Fetcher, Ledger
from reading_pack.net import Http
from reading_pack.pdf.merge import assemble
from reading_pack.report import write_missing, write_report

ROOT = Path(__file__).resolve().parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ROOT, help="output folder (default: script folder)")
    ap.add_argument("--no-download", action="store_true", help="only merge what is already on disk")
    ap.add_argument("--only", type=int, nargs="*", help="fetch only these paper numbers (testing)")
    args = ap.parse_args()

    papers_dir = args.out / "papers"
    (papers_dir / "manual").mkdir(parents=True, exist_ok=True)
    http = Http()
    ledger = Ledger(papers_dir / "sources.json")
    fetcher = Fetcher(papers_dir, http, ledger)

    results = {}
    for paper in PAPERS:
        if args.no_download or (args.only and paper.num not in args.only):
            res = fetcher.acquire_offline(paper)
        else:
            print(f"[{paper.num:3d}/100] {paper.authors} {paper.year}: {paper.title}", flush=True)
            res = fetcher.acquire(paper)
            if res.status != "cached":
                ledger.put(res)
        results[paper.num] = res

    missing = write_missing(args.out / "missing.txt", PHASES, results)
    pages = assemble(args.out / "ML_Top100_Reading_Order.pdf", PHASES, results)
    write_report(args.out / "report.md", PHASES, results, pages, http.requests_made)
    print(f"\nIncluded {100 - missing}/100 papers, {pages} pages -> "
          f"{args.out / 'ML_Top100_Reading_Order.pdf'}")
    print(f"Missing: {missing} (see missing.txt); details in report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
