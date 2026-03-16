#!/usr/bin/env python3
"""
Generate a professional horse racing cheat card PDF from JSON data.

Usage:
    python3 generate_pdf.py [/path/to/race_day_data.json]

Defaults to /tmp/race_day_data.json if no argument given.
Outputs PDF to /tmp/race_day_cheatcard.pdf.
"""

import json
import sys
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    KeepTogether, PageBreak, HRFlowable,
)
from reportlab.lib.colors import HexColor

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
BLUE_HEADER = HexColor("#1565C0")
BLUE_LIGHT = HexColor("#E3F2FD")
GREEN_BET_BG = HexColor("#E8F5E9")
GREEN_BET_BORDER = HexColor("#4CAF50")
GREEN_DARK = HexColor("#2E7D32")
RED = HexColor("#F44336")
GRAY_LIGHT = HexColor("#F5F5F5")
GRAY_MED = HexColor("#9E9E9E")
WHITE = colors.white
BLACK = colors.black

TIER_COLORS = {
    "GREEN": HexColor("#4CAF50"),
    "YELLOW": HexColor("#FFC107"),
    "ORANGE": HexColor("#FF9800"),
    "RED": HexColor("#F44336"),
}

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
_styles = getSampleStyleSheet()

STYLE_TITLE = ParagraphStyle(
    "CheatTitle", parent=_styles["Heading1"],
    fontSize=18, leading=22, textColor=BLUE_HEADER, spaceAfter=2,
)
STYLE_SUBTITLE = ParagraphStyle(
    "CheatSub", parent=_styles["Normal"],
    fontSize=11, leading=14, textColor=HexColor("#333333"),
)
STYLE_RACE_HEADER = ParagraphStyle(
    "RaceHead", parent=_styles["Heading2"],
    fontSize=13, leading=16, textColor=WHITE, spaceAfter=0, spaceBefore=0,
)
STYLE_BODY = ParagraphStyle(
    "Body9", parent=_styles["Normal"],
    fontSize=9, leading=11,
)
STYLE_BODY_BOLD = ParagraphStyle(
    "Body9B", parent=STYLE_BODY, fontName="Helvetica-Bold",
)
STYLE_SMALL = ParagraphStyle(
    "Small8", parent=_styles["Normal"],
    fontSize=8, leading=10,
)
STYLE_SMALL_BOLD = ParagraphStyle(
    "Small8B", parent=STYLE_SMALL, fontName="Helvetica-Bold",
)
STYLE_ITALIC = ParagraphStyle(
    "Italic9", parent=STYLE_BODY, fontName="Helvetica-Oblique",
)
STYLE_CELL = ParagraphStyle(
    "Cell8", parent=_styles["Normal"],
    fontSize=8, leading=10,
)
STYLE_CELL_BOLD = ParagraphStyle(
    "Cell8B", parent=STYLE_CELL, fontName="Helvetica-Bold",
)
STYLE_BET = ParagraphStyle(
    "Bet9", parent=_styles["Normal"],
    fontSize=9, leading=12, fontName="Helvetica",
)
STYLE_BET_BOLD = ParagraphStyle(
    "Bet9B", parent=STYLE_BET, fontName="Helvetica-Bold",
)
STYLE_SECTION = ParagraphStyle(
    "Section", parent=_styles["Heading2"],
    fontSize=13, leading=16, textColor=BLUE_HEADER, spaceBefore=10, spaceAfter=4,
)
STYLE_FOOTER = ParagraphStyle(
    "Footer", parent=_styles["Normal"],
    fontSize=8, leading=10, textColor=GRAY_MED, alignment=TA_CENTER,
)


def safe(data, key, default=""):
    """Get a key from dict safely."""
    if data is None:
        return default
    return data.get(key, default) or default


def p(text, style=STYLE_CELL):
    """Shortcut to create a Paragraph."""
    return Paragraph(str(text), style)


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def build_header(data):
    """Track name, date, first post."""
    elements = []
    track = safe(data, "track", "Race Day")
    date = safe(data, "date", "")
    location = safe(data, "location", "")
    first_post = safe(data, "first_post", "")

    elements.append(Paragraph(f"<b>{track}</b> &mdash; Cheat Card", STYLE_TITLE))
    parts = []
    if location:
        parts.append(location)
    if date:
        parts.append(date)
    if first_post:
        parts.append(f"First Post: {first_post}")
    elements.append(Paragraph(" | ".join(parts), STYLE_SUBTITLE))
    elements.append(Spacer(1, 6))
    return elements


def build_weather(data):
    """Weather & track conditions box."""
    weather = safe(data, "weather", {})
    if not weather:
        return []

    forecast = safe(weather, "forecast", "N/A")
    dirt = safe(weather, "track_dirt", "")
    turf = safe(weather, "track_turf", "")
    advisory = safe(weather, "advisory", "")

    lines = [f"<b>Weather:</b> {forecast}"]
    cond_parts = []
    if dirt:
        cond_parts.append(f"Dirt: <b>{dirt}</b>")
    if turf:
        cond_parts.append(f"Turf: <b>{turf}</b>")
    if cond_parts:
        lines.append("<b>Track:</b> " + " | ".join(cond_parts))
    if advisory:
        lines.append(f"<font color='#F44336'><b>Advisory:</b> {advisory}</font>")

    content = "<br/>".join(lines)
    tbl = Table([[Paragraph(content, STYLE_BODY)]], colWidths=[7.1 * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE_LIGHT),
        ("BOX", (0, 0), (-1, -1), 1, BLUE_HEADER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [tbl, Spacer(1, 6)]


def build_strategy(data):
    """Strategy quote."""
    quote = safe(data, "strategy_quote", "")
    if not quote:
        return []
    return [
        Paragraph(f"<i>\"{quote}\"</i>", STYLE_ITALIC),
        Spacer(1, 4),
    ]


def build_sources(data):
    """Expert sources line."""
    sources = safe(data, "sources", [])
    note = safe(data, "sources_note", "")
    elements = []
    if sources:
        elements.append(Paragraph(
            f"<b>Sources:</b> {', '.join(sources)}", STYLE_BODY
        ))
    if note:
        elements.append(Paragraph(
            f"<i>{note}</i>",
            ParagraphStyle("note", parent=STYLE_BODY, fontSize=8, textColor=GRAY_MED),
        ))
    if elements:
        elements.append(Spacer(1, 6))
    return elements


def build_scratches(data):
    """Scratches line."""
    scratches = safe(data, "scratches", [])
    if not scratches:
        return []
    txt = "<b>Scratches:</b> " + " | ".join(scratches)
    return [Paragraph(txt, ParagraphStyle("scratch", parent=STYLE_BODY, textColor=RED)), Spacer(1, 6)]


def build_pnl(data):
    """P&L tracking table."""
    pnl = safe(data, "pnl", [])
    totals = safe(data, "pnl_totals", {})
    if not pnl:
        return []

    elements = [Paragraph("<b>P&amp;L TRACKING</b>", STYLE_SECTION)]

    # Header row
    header = ["Race", "Bet Type", "Horse(s)", "Wagered", "Result", "Payout", "Net"]
    rows = [header]
    for entry in pnl:
        result_str = safe(entry, "result", "PENDING")
        payout_val = entry.get("payout", 0) or 0
        net_val = entry.get("net", 0) or 0
        rows.append([
            safe(entry, "race"),
            safe(entry, "bet_type"),
            safe(entry, "horse"),
            f"${entry.get('wagered', 0):.2f}",
            result_str,
            f"${payout_val:.2f}" if payout_val else "-",
            f"${net_val:+.2f}" if net_val != 0 else "-",
        ])

    # Totals row
    wagered = totals.get("wagered", 0) or 0
    returned = totals.get("returned", 0) or 0
    net = totals.get("net", 0) or 0
    roi = safe(totals, "roi", "0%")
    rows.append(["TOTAL", "", "", f"${wagered:.2f}", f"ROI: {roi}", f"${returned:.2f}", f"${net:+.2f}"])

    col_widths = [0.5 * inch, 1.1 * inch, 1.1 * inch, 0.7 * inch, 0.9 * inch, 0.7 * inch, 0.7 * inch]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [WHITE, GRAY_LIGHT]),
        ("BACKGROUND", (0, -1), (-1, -1), HexColor("#E3F2FD")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ALIGN", (3, 0), (-1, -1), "RIGHT"),
    ]

    # Color the net column for totals
    if net > 0:
        style_cmds.append(("TEXTCOLOR", (-1, -1), (-1, -1), GREEN_DARK))
    elif net < 0:
        style_cmds.append(("TEXTCOLOR", (-1, -1), (-1, -1), RED))

    # Color individual result cells
    for i, entry in enumerate(pnl, start=1):
        result_str = safe(entry, "result", "PENDING")
        if result_str == "WIN":
            style_cmds.append(("TEXTCOLOR", (4, i), (4, i), GREEN_DARK))
        elif result_str == "LOSS":
            style_cmds.append(("TEXTCOLOR", (4, i), (4, i), RED))

    tbl.setStyle(TableStyle(style_cmds))
    elements.append(tbl)
    elements.append(Spacer(1, 8))
    return elements


def build_race(race, scratches_list):
    """Build elements for a single race, including bet box. Returns KeepTogether."""
    num = race.get("number", "?")
    time = safe(race, "time", "")
    rtype = safe(race, "type", "")
    type_label = safe(race, "type_label", rtype)
    distance = safe(race, "distance", "")
    purse = safe(race, "purse", "")
    starters = race.get("starters", "")
    horses = race.get("horses", [])
    bets = race.get("bets", [])
    result = race.get("result")

    elements = []

    # --- Race header bar ---
    header_text = f"Race {num}"
    if time:
        header_text += f" &mdash; {time}"
    if type_label:
        header_text += f" &mdash; {type_label}"
    if distance:
        header_text += f" &mdash; {distance}"
    if purse:
        header_text += f" &mdash; {purse}"
    if starters:
        header_text += f" ({starters} starters)"

    hdr_tbl = Table(
        [[Paragraph(header_text, STYLE_RACE_HEADER)]],
        colWidths=[7.1 * inch],
    )
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE_HEADER),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(hdr_tbl)

    # --- Horse table ---
    col_headers = ["PP", "Horse", "Jockey", "Trainer", "ML", "Picks", "Tier", "Val"]
    col_widths = [0.3 * inch, 1.4 * inch, 1.0 * inch, 1.1 * inch, 0.5 * inch, 1.2 * inch, 0.7 * inch, 0.6 * inch]

    rows = [[p(h, STYLE_CELL_BOLD) for h in col_headers]]

    # Build a set of scratched horse names for this race
    race_scratches = set()
    for s in scratches_list:
        # format: "R2: Horse Name" or "R2: Horse Name (AE)"
        if s.startswith(f"R{num}:"):
            name = s.split(":", 1)[1].strip()
            # Remove parenthetical notes
            if "(" in name:
                name = name[:name.index("(")].strip()
            race_scratches.add(name.upper())

    for h in horses:
        pp = h.get("pp", "")
        name = safe(h, "name", "")
        jockey = safe(h, "jockey", "")
        trainer = safe(h, "trainer", "")
        ml = safe(h, "ml", "")
        picks = safe(h, "picks", "")
        tier = safe(h, "tier", "")
        value = safe(h, "value", "")
        bold = h.get("bold", False)

        is_scratched = name.upper() in race_scratches

        if is_scratched:
            scratch_style = ParagraphStyle("scratch_cell", parent=STYLE_CELL,
                                           fontName="Helvetica-Oblique", textColor=GRAY_MED)
            row = [
                p(str(pp), scratch_style),
                p(f"<strike>{name}</strike> SCR", scratch_style),
                p(jockey, scratch_style),
                p(trainer, scratch_style),
                p(ml, scratch_style),
                p("", scratch_style),
                p("", scratch_style),
                p("", scratch_style),
            ]
        else:
            name_style = STYLE_CELL_BOLD if bold else STYLE_CELL
            row = [
                p(str(pp), STYLE_CELL),
                p(name, name_style),
                p(jockey, STYLE_CELL),
                p(trainer, STYLE_CELL),
                p(ml, STYLE_CELL),
                p(picks, STYLE_CELL),
                p(tier, STYLE_CELL),
                p(value, STYLE_CELL_BOLD if value else STYLE_CELL),
            ]
        rows.append(row)

    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1E88E5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]

    # Color tier cells
    for i, h in enumerate(horses, start=1):
        tier = safe(h, "tier", "").upper()
        if tier in TIER_COLORS:
            style_cmds.append(("BACKGROUND", (6, i), (6, i), TIER_COLORS[tier]))
            # Use black text on yellow, white on others
            tc = BLACK if tier == "YELLOW" else WHITE
            style_cmds.append(("TEXTCOLOR", (6, i), (6, i), tc))

    tbl.setStyle(TableStyle(style_cmds))
    elements.append(tbl)

    # --- Bets box directly below race table ---
    bet_elements = []
    if bets:
        for b in bets:
            btype = safe(b, "type", "")
            detail = safe(b, "detail", "")
            cost = safe(b, "cost", "")
            say = safe(b, "say", "")
            line = f"<b>{btype}</b>: {detail}"
            if cost:
                line += f" &mdash; <b>{cost}</b>"
            bet_elements.append(Paragraph(line, STYLE_BET))
            if say:
                bet_elements.append(Paragraph(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Say: \"{say}\"</i>",
                    ParagraphStyle("say", parent=STYLE_BET, fontSize=8, textColor=HexColor("#555555")),
                ))
    else:
        bet_elements.append(Paragraph(
            "<b>BETS:</b> $1 Exacta Box only (see exotic section)",
            STYLE_BET,
        ))

    # Build the bet box as a colored table cell
    bet_header = Paragraph("<b>BETS FOR RACE {}</b>".format(num), STYLE_BET_BOLD)
    inner = [bet_header, Spacer(1, 2)] + bet_elements

    # Use a nested table trick: single cell with all bet paragraphs
    from reportlab.platypus import TableStyle as TS
    bet_cell_content = []
    for el in inner:
        bet_cell_content.append([el])

    bet_inner_tbl = Table(bet_cell_content, colWidths=[6.9 * inch])
    bet_inner_tbl.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    bet_outer = Table([[bet_inner_tbl]], colWidths=[7.1 * inch])
    bet_outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), GREEN_BET_BG),
        ("BOX", (0, 0), (-1, -1), 1.5, GREEN_BET_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(bet_outer)

    # --- Result if available ---
    if result:
        elements.append(Paragraph(
            f"<b>RESULT:</b> {result}",
            ParagraphStyle("result", parent=STYLE_BODY_BOLD, textColor=GREEN_DARK),
        ))

    elements.append(Spacer(1, 10))

    return KeepTogether(elements)


def build_budget_plans(data):
    """Budget plans table."""
    plans = safe(data, "budget_plans", [])
    if not plans:
        return []

    elements = [Paragraph("<b>BUDGET PLANS</b>", STYLE_SECTION)]

    header = ["Budget", "Straight", "Exacta", "Trifecta", "Superfecta", "Daily Double", "Notes"]
    rows = [header]
    for plan in plans:
        rows.append([
            safe(plan, "budget"),
            safe(plan, "straight"),
            safe(plan, "exacta"),
            safe(plan, "trifecta"),
            safe(plan, "superfecta"),
            safe(plan, "daily_double"),
            safe(plan, "notes"),
        ])

    col_widths = [0.9 * inch, 0.7 * inch, 1.1 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 1.6 * inch]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 8))
    return elements


def build_race_type_targeting(data):
    """Race type targeting table."""
    targeting = safe(data, "race_type_targeting", [])
    if not targeting:
        return []

    elements = [Paragraph("<b>RACE TYPE TARGETING</b>", STYLE_SECTION)]

    header = ["Type", "Strategy", "Upset Rate", "Avg Payout", "Today's Races"]
    rows = [header]
    for t in targeting:
        rows.append([
            safe(t, "type"),
            safe(t, "strategy"),
            safe(t, "upset_rate"),
            safe(t, "avg_payout"),
            safe(t, "todays_races"),
        ])

    col_widths = [0.6 * inch, 2.0 * inch, 0.9 * inch, 1.0 * inch, 1.2 * inch]
    tbl = Table(rows, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GRAY_LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 8))
    return elements


def build_quick_reference(data):
    """Quick reference section."""
    elements = [Paragraph("<b>QUICK REFERENCE</b>", STYLE_SECTION)]

    day_mod = safe(data, "day_modifier", "")

    ref_lines = [
        "<b>Race Types:</b> CLM=Claiming, MCL=Maiden Claiming, ALW=Allowance, AOC=Allowance Optional Claiming, "
        "SOC=Starter Optional Claiming, MOC=Maiden Optional Claiming, MSW=Maiden Special Weight, STK=Stakes",
        "<b>Tiers:</b> GREEN=Strong Play, YELLOW=Good Value, ORANGE=Moderate, RED=Risky/Longshot",
        "<b>VP</b> = Value Play (positive expected value based on ML vs consensus)",
        "<b>Betting Rule:</b> WIN bets only at 5/1 or higher. Use exacta/trifecta boxes for value picks.",
    ]
    if day_mod:
        ref_lines.append(f"<b>Day Modifier:</b> {day_mod}")

    for line in ref_lines:
        elements.append(Paragraph(line, STYLE_SMALL))
        elements.append(Spacer(1, 2))

    elements.append(Spacer(1, 6))
    return elements


def build_footer(data):
    """Footer with version, timestamp, good luck."""
    version = safe(data, "version", "")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = []
    if version:
        parts.append(version)
    parts.append(f"Generated {now}")
    parts.append("Good luck at the windows!")

    return [
        HRFlowable(width="100%", thickness=1, color=GRAY_MED),
        Spacer(1, 4),
        Paragraph(" | ".join(parts), STYLE_FOOTER),
    ]


# ---------------------------------------------------------------------------
# Main PDF builder
# ---------------------------------------------------------------------------

def generate_pdf(data, output_path="/tmp/race_day_cheatcard.pdf"):
    """Generate the full cheat card PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=50,
        bottomMargin=50,
        leftMargin=50,
        rightMargin=50,
    )

    story = []

    # 1. Header
    story.extend(build_header(data))

    # 2. Weather
    story.extend(build_weather(data))

    # 3. Strategy quote
    story.extend(build_strategy(data))

    # 4. Sources
    story.extend(build_sources(data))

    # Scratches
    story.extend(build_scratches(data))

    # 5. P&L tracking
    story.extend(build_pnl(data))

    # 6. Races
    races = data.get("races", [])
    scratches_list = data.get("scratches", [])
    for race in races:
        story.append(build_race(race, scratches_list))

    # 7. Budget plans
    story.extend(build_budget_plans(data))

    # 8. Race type targeting
    story.extend(build_race_type_targeting(data))

    # 9. Quick reference
    story.extend(build_quick_reference(data))

    # 10. Footer
    story.extend(build_footer(data))

    doc.build(story)
    print(f"PDF generated: {output_path}")
    return output_path


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/race_day_data.json"

    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        print("Usage: python3 generate_pdf.py [/path/to/race_day_data.json]")
        sys.exit(1)

    with open(input_path, "r") as f:
        data = json.load(f)

    output_path = "/tmp/race_day_cheatcard.pdf"
    generate_pdf(data, output_path)


if __name__ == "__main__":
    main()
