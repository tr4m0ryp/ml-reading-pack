"""Throttled HTTP client: one request per ~3 s across the whole run, descriptive User-Agent."""

from __future__ import annotations

import os
import time
from urllib.parse import urlparse

import requests

MIN_INTERVAL_S = 3.0
RETRY_STATUS = {429, 500, 502, 503, 504}

# Shadow libraries are never contacted, even if a metadata source points at one.
BLOCKED_HOSTS = ("sci-hub", "scihub", "libgen", "library.lol", "z-lib", "zlibrary", "1lib",
                 "b-ok", "booksc", "annas-archive", "pdfdrive", "libstc", "nexus-stc")


def _user_agent() -> str:
    ua = ("ML-Top100-ReadingPack/1.0 (personal study reading list; fetches open-access PDFs only; "
          "python-requests)")
    contact = os.environ.get("READING_PACK_CONTACT", "").strip()
    return f"{ua} mailto:{contact}" if contact else ua


def blocked(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(b in host for b in BLOCKED_HOSTS)


class Http:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = _user_agent()
        self._last = 0.0
        self.requests_made = 0

    def _throttle(self) -> None:
        wait = MIN_INTERVAL_S - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def get(self, url: str, *, params: dict | None = None, headers: dict | None = None,
            timeout: float = 90, retries: int = 3) -> requests.Response | None:
        """GET with throttle and retry; None on network failure, blocked host or exhausted retries."""
        if blocked(url):
            return None
        for attempt in range(retries):
            self._throttle()
            self.requests_made += 1
            try:
                r = self.session.get(url, params=params, headers=headers, timeout=timeout)
            except requests.RequestException:
                continue
            if blocked(r.url):
                return None
            if r.status_code in RETRY_STATUS and attempt + 1 < retries:
                time.sleep(min(90.0, 10.0 * 2 ** attempt))
                continue
            return r
        return None
