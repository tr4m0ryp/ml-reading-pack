"""Generated pages: cover, table of contents, phase dividers and placeholders for missing papers."""

from __future__ import annotations

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from reading_pack.catalog import Paper, Phase
from reading_pack.videos import duration

SS = getSampleStyleSheet()
TITLE = ParagraphStyle("t", parent=SS["Title"], fontSize=30, leading=36, spaceAfter=18)
SUB = ParagraphStyle("s", parent=SS["Normal"], fontSize=13, leading=18, alignment=1,
                     textColor=colors.HexColor("#444444"))
H = ParagraphStyle("h", parent=SS["Heading1"], fontSize=20, leading=24)
BODY = ParagraphStyle("b", parent=SS["Normal"], fontSize=12, leading=17)
CELL = ParagraphStyle("c", parent=SS["Normal"], fontSize=8.5, leading=10.5)
PHASE_CELL = ParagraphStyle("pc", parent=CELL, fontName="Helvetica-Bold", fontSize=10, leading=13)
DIV_NUM = ParagraphStyle("dn", parent=SS["Normal"], fontSize=16, alignment=1,
                         textColor=colors.HexColor("#777777"), spaceAfter=10)
DIV_NAME = ParagraphStyle("dname", parent=TITLE, fontSize=28, leading=34)
DIV_WHY = ParagraphStyle("dw", parent=BODY, fontSize=14, leading=20, alignment=1)


def _render(story: list) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm)
    doc.build(story)
    return buf.getvalue()


def cover(phases: tuple[Phase, ...], included: int, total: int, date: str) -> bytes:
    story = [Spacer(1, 4 * cm), Paragraph("Machine Learning: Top 100 Papers", TITLE),
             Paragraph("A reading order in 12 phases, from statistical foundations to modern LLMs",
                       SUB), Spacer(1, 1.5 * cm),
             Paragraph(f"{included} of {total} papers included &middot; built {escape(date)}", SUB),
             Spacer(1, 1.5 * cm)]
    story += [Paragraph(f"Phase {ph.num}: {escape(ph.name)} ({len(ph.papers)} papers)", SUB)
              for ph in phases]
    story += [Spacer(1, 1 * cm), Paragraph(
        "Personal study copy. Every paper remains under its authors' and publishers' terms; "
        "sources are listed in report.md.", SUB)]
    return _render(story)


def _video_line(v: dict | None) -> str:
    if not v:
        return ""
    meta = ", ".join(x for x in (v.get("channel", ""), v.get("style", ""), duration(v)) if x)
    return (f"<br/><font color='#1a5fb4'>Video: <link href='{escape(v['url'])}'>"
            f"{escape(v['video_title'])}</link></font> <font color='#777777'>({escape(meta)})</font>")


def toc(phases: tuple[Phase, ...], phase_pages: dict[int, int], paper_pages: dict[int, int],
        missing: set[int], videos: dict[int, dict]) -> bytes:
    rows, style = [], [("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 2)]
    for ph in phases:
        style += [("TOPPADDING", (0, len(rows)), (-1, len(rows)), 9),
                  ("LINEBELOW", (0, len(rows)), (-1, len(rows)), 0.5, colors.grey)]
        rows.append(["", Paragraph(f"Phase {ph.num}: {escape(ph.name)}", PHASE_CELL),
                     Paragraph(str(phase_pages.get(ph.num, "")), PHASE_CELL)])
        for p in ph.papers:
            gone = " <i>(not included, see missing.txt)</i>" if p.num in missing else ""
            text = f"{escape(p.title)} &middot; <font color='#555555'>{escape(p.authors)}, {p.year}</font>{gone}"
            text += _video_line(videos.get(p.num))
            rows.append([Paragraph(f"{p.num:03d}", CELL), Paragraph(text, CELL),
                         Paragraph(str(paper_pages.get(p.num, "")), CELL)])
    table = Table(rows, colWidths=[1.1 * cm, 14.2 * cm, 1.7 * cm], repeatRows=0)
    table.setStyle(TableStyle(style))
    return _render([Paragraph("Contents", H), Spacer(1, 0.3 * cm), table])


def divider(phase: Phase, videos: dict[int, dict]) -> bytes:
    first, last = phase.papers[0].num, phase.papers[-1].num
    top = 3 if len(phase.papers) <= 12 else 0.5  # big phases need the room for their video list
    story = [Spacer(1, top * cm), Paragraph(f"Phase {phase.num} of 12", DIV_NUM),
             Paragraph(escape(phase.name), DIV_NAME), Spacer(1, 0.6 * cm),
             Paragraph(escape(phase.why), DIV_WHY), Spacer(1, 0.6 * cm),
             Paragraph(f"Papers {first:03d} to {last:03d}", DIV_NUM)]
    watch = [p for p in phase.papers if p.num in videos]
    if watch:
        story += [Spacer(1, 0.4 * cm), Paragraph("<b>Watch alongside</b>", BODY)]
        story += [Paragraph(f"<b>{p.num:03d}</b> {escape(p.title)}{_video_line(videos[p.num])}", CELL)
                  for p in watch]
    return _render(story)


def placeholder(paper: Paper, doi: str | None, link: str | None, reason: str) -> bytes:
    story = [Spacer(1, 6 * cm), Paragraph(f"{paper.num:03d}", DIV_NUM),
             Paragraph(escape(paper.title), H),
             Paragraph(f"{escape(paper.authors)}, {paper.year}", BODY), Spacer(1, 1 * cm),
             Paragraph(f"<b>Not included:</b> {escape(reason)}", BODY)]
    if doi:
        story.append(Paragraph(f"DOI: {escape(doi)}", BODY))
    if link:
        story.append(Paragraph(f"Link: <link href='{escape(link)}'>{escape(link)}</link>", BODY))
    story.append(Paragraph(
        f"Save it as papers/manual/{paper.num:03d}_&lt;anything&gt;.pdf and re-run the script.", BODY))
    return _render(story)


__all__ = ["cover", "divider", "placeholder", "toc"]
