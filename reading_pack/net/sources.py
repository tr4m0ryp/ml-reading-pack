"""Where to look for a legal open-access PDF: catalog hints, arXiv, Semantic Scholar, arXiv search."""

from __future__ import annotations

import html
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from reading_pack.catalog import Paper
from reading_pack.net.http import Http
from reading_pack.pdf.verify import title_similarity

S2_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS = "title,year,externalIds,openAccessPdf,url"
OPENALEX = "https://api.openalex.org/works"
ARXIV_API = "http://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"

SOURCE_NAMES = {
    "arxiv.org": "arXiv",
    "export.arxiv.org": "arXiv",
    "proceedings.neurips.cc": "NeurIPS proceedings",
    "papers.nips.cc": "NeurIPS proceedings",
    "proceedings.mlr.press": "PMLR (ICML/AISTATS proceedings)",
    "www.jmlr.org": "JMLR",
    "jmlr.org": "JMLR",
    "openaccess.thecvf.com": "CVF Open Access",
    "aclanthology.org": "ACL Anthology",
    "cdn.aaai.org": "AAAI proceedings (KDD-96)",
    "link.springer.com": "Springer (free-to-read publisher copy)",
    "www.nature.com": "Nature (open-access article)",
}


def source_name(url: str, via: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    name = SOURCE_NAMES.get(host, f"author/institutional page ({host})")
    return name if via == "catalog" else f"{name}, found via {via}"


def arxiv_pdf(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}"


@dataclass
class Meta:
    """What Semantic Scholar knows; fills missing.txt when no PDF can be fetched."""
    doi: str | None = None
    link: str | None = None
    oa_urls: list[str] = field(default_factory=list)
    arxiv: str | None = None
    error: str | None = None


def landing_pdf(r) -> str | None:
    """A repository landing page often names its PDF in a citation_pdf_url meta tag."""
    if "html" not in r.headers.get("content-type", ""):
        return None
    m = re.search(r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)', r.text)
    m = m or re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url', r.text)
    return urljoin(r.url, html.unescape(m.group(1))) if m else None


def catalog_candidates(paper: Paper) -> list[tuple[str, str]]:
    cands = [(u, "catalog") for u in paper.urls]
    if paper.arxiv:
        cands.append((arxiv_pdf(paper.arxiv), "catalog"))
    return cands


S2_MAX_STRIKES = 3  # consecutive failures before S2 is skipped for the rest of the run
_s2_strikes = 0


def semantic_scholar(http: Http, paper: Paper) -> Meta:
    global _s2_strikes
    meta = Meta(doi=paper.doi)
    if _s2_strikes >= S2_MAX_STRIKES:
        meta.error = "skipped (rate-limited earlier this run; set S2_API_KEY to avoid)"
        return meta
    headers = {}
    if key := os.environ.get("S2_API_KEY"):
        headers["x-api-key"] = key
    r = http.get(S2_SEARCH, params={"query": paper.title, "fields": S2_FIELDS, "limit": 5},
                 headers=headers, retries=2)
    if r is None or r.status_code != 200:
        _s2_strikes += 1
        meta.error = f"HTTP {r.status_code}" if r is not None else "no response"
        return meta
    _s2_strikes = 0
    for hit in r.json().get("data") or []:
        if not _matches(hit.get("title"), hit.get("year"), paper):
            continue
        ext = hit.get("externalIds") or {}
        meta.doi = meta.doi or ext.get("DOI")
        meta.arxiv = meta.arxiv or ext.get("ArXiv")
        meta.link = meta.link or hit.get("url")
        _add(meta, (hit.get("openAccessPdf") or {}).get("url"))
    return meta


def openalex(http: Http, paper: Paper, meta: Meta) -> None:
    """Second metadata index (keyless, generous limits): adds legal OA PDF locations to `meta`."""
    params = {"search": paper.title, "per-page": 5,
              "select": "title,publication_year,doi,open_access,locations"}
    if contact := os.environ.get("READING_PACK_CONTACT", "").strip():
        params["mailto"] = contact
    r = http.get(OPENALEX, params=params)
    if r is None or r.status_code != 200:
        return
    for hit in r.json().get("results") or []:
        if not _matches(hit.get("title"), hit.get("publication_year"), paper):
            continue
        if not meta.doi and hit.get("doi"):
            meta.doi = hit["doi"].removeprefix("https://doi.org/")
        for loc in hit.get("locations") or []:
            if loc.get("is_oa"):
                _add(meta, loc.get("pdf_url"))
        _add(meta, (hit.get("open_access") or {}).get("oa_url"))


def _matches(title: str | None, year: int | None, paper: Paper) -> bool:
    if title_similarity(title or "", paper.title) < 0.85:
        return False
    return not year or abs(int(year) - paper.year) <= 3


def _add(meta: Meta, url: str | None) -> None:
    if url and url not in meta.oa_urls:
        meta.oa_urls.append(url)


def arxiv_search(http: Http, paper: Paper) -> str | None:
    words = "".join(c if c.isalnum() else " " for c in paper.title).split()
    query = " AND ".join(f"ti:{w}" for w in words if len(w) > 2)[:900]
    r = http.get(ARXIV_API, params={"search_query": query, "max_results": 5})
    if r is None or r.status_code != 200:
        return None
    try:
        feed = ET.fromstring(r.content)
    except ET.ParseError:
        return None
    for entry in feed.findall(f"{ATOM}entry"):
        title = " ".join((entry.findtext(f"{ATOM}title") or "").split())
        if title_similarity(title, paper.title) >= 0.9:
            return (entry.findtext(f"{ATOM}id") or "").rsplit("/abs/", 1)[-1] or None
    return None
