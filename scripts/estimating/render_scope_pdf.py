#!/usr/bin/env python3
"""Render a scope_of_work.json into a clean, printable PDF report via
reportlab — no browser dependency. Report-only output — nothing here
submits, prices, or commits anything.

Usage:
  python3 render_scope_pdf.py path/to/scope_of_work.json --out report.pdf --title "..."
"""
import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)

CONFIDENCE_COLOR = {
    "schedule_verified": colors.HexColor("#1a7a3c"),
    "cross_checked": colors.HexColor("#1a7a3c"),
    "single_source": colors.HexColor("#8a6d1a"),
    "vision_count": colors.HexColor("#8a6d1a"),
    "benchmark_only": colors.HexColor("#8a6d1a"),
    "unresolved": colors.HexColor("#a02020"),
}

TITLE_STYLE = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=16, leading=20, spaceAfter=6)
SUBTITLE_STYLE = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=9.5, textColor=colors.HexColor("#555555"), spaceAfter=10)
BANNER_STYLE = ParagraphStyle("banner", fontName="Helvetica", fontSize=8.7, leading=12)
ITEM_STYLE = ParagraphStyle("item", fontName="Helvetica-Bold", fontSize=8.7, leading=11)
NOTE_STYLE = ParagraphStyle("note", fontName="Helvetica", fontSize=7.3, leading=9.5, textColor=colors.HexColor("#555555"), spaceBefore=2)
SRC_STYLE = ParagraphStyle("src", fontName="Helvetica", fontSize=7, leading=9, textColor=colors.HexColor("#444444"))
CONF_STYLE_BASE = ParagraphStyle("conf", fontName="Helvetica-Bold", fontSize=7.3, alignment=1)
HEADER_STYLE = ParagraphStyle("header", fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#333333"))
STAT_NUM_STYLE = ParagraphStyle("statnum", fontName="Helvetica-Bold", fontSize=15)
STAT_LABEL_STYLE = ParagraphStyle("statlabel", fontName="Helvetica", fontSize=8, textColor=colors.HexColor("#555555"))


def fmt_qty(qty):
    if qty is None:
        return "—"
    if isinstance(qty, float):
        s = f"{qty:,.2f}".rstrip("0").rstrip(".")
        return s
    return f"{qty:,}"


def build_pdf(scope: dict, title: str, subtitle: str, out_path: str):
    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        topMargin=0.55 * inch, bottomMargin=0.55 * inch,
        leftMargin=0.5 * inch, rightMargin=0.5 * inch,
    )
    story = [Paragraph(title, TITLE_STYLE), Paragraph(subtitle, SUBTITLE_STYLE)]

    banner_tbl = Table(
        [[Paragraph(
            "<b>Report-only.</b> This is a materials/quantity breakdown generated from the real bid "
            "attachments for internal review. It does not submit a bid, price a proposal, or commit "
            "ENGCO to anything — every line is either cited to an exact source or explicitly "
            "flagged as needing human takeoff.", BANNER_STYLE)]],
        colWidths=[7.5 * inch],
    )
    banner_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff4e5")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#d99a3a")),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story += [banner_tbl, Spacer(1, 10)]

    unresolved = sum(1 for l in scope["lines"] if l["confidence"] == "unresolved")
    verified = scope["line_count"] - unresolved
    stats_tbl = Table(
        [[
            Paragraph(f"{scope['line_count']}<br/><font size=8 color='#555555'>total line items</font>", STAT_NUM_STYLE),
            Paragraph(f"{verified}<br/><font size=8 color='#555555'>cited/verified</font>", STAT_NUM_STYLE),
            Paragraph(f"{unresolved}<br/><font size=8 color='#555555'>flagged for human takeoff</font>", STAT_NUM_STYLE),
        ]],
        colWidths=[2.5 * inch] * 3,
    )
    stats_tbl.setStyle(TableStyle([
        ("BOX", (0, 0), (0, 0), 0.75, colors.HexColor("#dddddd")),
        ("BOX", (1, 0), (1, 0), 0.75, colors.HexColor("#dddddd")),
        ("BOX", (2, 0), (2, 0), 0.75, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story += [stats_tbl, Spacer(1, 12)]

    header = [
        Paragraph("Div", HEADER_STYLE), Paragraph("Item", HEADER_STYLE),
        Paragraph("Qty", HEADER_STYLE), Paragraph("Unit", HEADER_STYLE),
        Paragraph("Confidence", HEADER_STYLE), Paragraph("Source", HEADER_STYLE),
    ]
    rows = [header]
    for line in scope["lines"]:
        item_html = f"{line['item']}"
        if line.get("note"):
            item_para = Paragraph(item_html, ITEM_STYLE)
            note_para = Paragraph(line["note"], NOTE_STYLE)
            item_cell = [item_para, note_para]
        else:
            item_cell = Paragraph(item_html, ITEM_STYLE)

        cites = line["citations"]
        if cites:
            src_html = "<br/><br/>".join(
                f"{c['source_file']} p{c['source_page']}"
                + (f" — <i>{c['source_snippet']}</i>" if c.get("source_snippet") else "")
                for c in cites
            )
        else:
            src_html = "n/a (unresolved)"

        color = CONFIDENCE_COLOR.get(line["confidence"], colors.HexColor("#555555"))
        conf_style = ParagraphStyle("conf_inst", parent=CONF_STYLE_BASE, textColor=color)

        rows.append([
            Paragraph(line["csi_division"], SRC_STYLE),
            item_cell,
            Paragraph(fmt_qty(line["quantity"]), ParagraphStyle("qty", fontName="Helvetica", fontSize=8.5, alignment=2)),
            Paragraph(line["unit"], SRC_STYLE),
            Paragraph(line["confidence"], conf_style),
            Paragraph(src_html, SRC_STYLE),
        ])

    col_widths = [0.32 * inch, 2.55 * inch, 0.55 * inch, 0.4 * inch, 0.85 * inch, 2.83 * inch]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4f4f4")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#999999")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#e5e5e5")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    tbl.setStyle(TableStyle(style))
    story.append(tbl)

    footer = Paragraph(
        "Generated by the ENGCO ONE estimating toolkit — scripts/estimating/build_kingwood_scope.py &amp; render_scope_pdf.py",
        ParagraphStyle("footer", fontName="Helvetica", fontSize=7, textColor=colors.HexColor("#888888"), spaceBefore=12),
    )
    story.append(footer)

    doc.build(story)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scope_json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    args = ap.parse_args()

    scope = json.loads(Path(args.scope_json).read_text())
    out_path = str(Path(args.out).resolve())
    build_pdf(scope, args.title, args.subtitle, out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
