# ml-reading-pack

Builds `ML_Top100_Reading_Order.pdf`: 100 machine-learning papers in a 12-phase reading order,
with a cover, a contents page with page numbers and an explainer video per paper, a divider
per phase, and Phase > Paper bookmarks. Papers come only from legal open-access sources
(arXiv, open proceedings, JMLR, author pages); each download is checked to be a real PDF with
the right title on page 1.

```bash
python3 -m venv .venv && .venv/bin/pip install requests pypdf reportlab
.venv/bin/python build_reading_pack.py          # re-runnable; skips files already present
```

Papers without an open-access copy are listed in `missing.txt`. Save them as
`papers/manual/NNN_<anything>.pdf` and re-run. `report.md` lists where each paper came from,
`videos.md` / `videos.json` the explainer videos. The PDFs themselves are not in this repo.

## License

ml-reading-pack is **source-available**, licensed under the [PolyForm Noncommercial License 1.0.0](./LICENSE) — **not** an OSI open-source license.

- **You may** use, modify, fork, and share ml-reading-pack freely for any **noncommercial** purpose, as long as you keep the copyright and `Required Notice:` lines (see [`NOTICE`](./NOTICE)) and credit *"ml-reading-pack by Keygraph, Inc."*
- **You may not** sell it, bundle it into a paid product, or run it as a paid/hosted service **without a commercial license**.

Copyright (c) 2026 Keygraph, Inc. The papers and videos it points to remain under their authors' and publishers' terms. Commercial licensing enquiries: see [`NOTICE`](./NOTICE).
