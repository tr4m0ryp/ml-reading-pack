"""Explainer videos per paper (videos.json), shown in the contents and on phase dividers."""

from __future__ import annotations

import json
from pathlib import Path

VIDEOS_FILE = Path(__file__).resolve().parent.parent / "videos.json"


def load_videos(path: Path = VIDEOS_FILE) -> dict[int, dict]:
    """num -> {url, video_title, channel, style, duration_s, ...}; only entries with a URL."""
    if not path.exists():
        return {}
    return {v["num"]: v for v in json.loads(path.read_text()) if v.get("url")}


def duration(v: dict) -> str:
    s = v.get("duration_s")
    if not s:
        return ""
    return f"{s // 3600}h {s % 3600 // 60:02d}m" if s >= 3600 else f"{s // 60} min"
