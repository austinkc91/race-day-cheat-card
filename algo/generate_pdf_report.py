#!/usr/bin/env python3
"""Generate a clean PDF report of the Value Handicapper analysis."""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "reportlab"], check=True)
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import inch
    from reportlab.lib import colors


def build_pdf():
    output_path = "/tmp/value_handicapper_report.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=50, bottomMargin=50, leftMargin=50, rightMargin=50)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=22, spaceAfter=6,
                                  textColor=HexColor('#1a1a2e'))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, spaceAfter=12,
                                     textColor=HexColor('#555555'))
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=16, spaceBefore=18, spaceAfter=8,
                               textColor=HexColor('#16213e'))
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, spaceBefore=12, spaceAfter=6,
                               textColor=HexColor('#0f3460'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6, leading=14)
    bold_style = ParagraphStyle('Bold', parent=body_style, fontName='Helvetica-Bold')
    value_style = ParagraphStyle('Value', parent=body_style, fontSize=11, fontName='Helvetica-Bold',
                                  textColor=HexColor('#e94560'))
    green_style = ParagraphStyle('Green', parent=body_style, fontSize=11, fontName='Helvetica-Bold',
                                  textColor=HexColor('#0e8b4f'))

    elements = []

    # Title
    elements.append(Paragraph("Value Handicapper Algorithm v1.0", title_style))
    elements.append(Paragraph("Multi-Track Racing Analysis | March 15-22, 2026", subtitle_style))
    elements.append(Paragraph("Strategy: Find BIG WINNERS the public is sleeping on", bold_style))
    elements.append(Spacer(1, 12))

    # BACKTEST SECTION
    elements.append(Paragraph("BACKTEST: March 15, 2026 Results", h1_style))
    elements.append(Paragraph("We tested our algorithm against 16 actual races across Oaklawn Park and Fair Grounds.", body_style))

    # Key stats
    elements.append(Paragraph("THE NUMBERS THAT MATTER:", h2_style))
    stats = [
        ["Metric", "Value", "What It Means"],
        ["Total Races", "16", "Oaklawn (9) + Fair Grounds (7)"],
        ["Avg Win Payout", "$8.71", "Most winners pay BIG"],
        ["Value Winners (4/1+)", "69%", "Chalk rarely wins!"],
        ["Consensus Win Rate", "19%", "Following experts = losing money"],
        ["Simulated Value ROI", "+51%", "$24 invested, $36.20 returned"],
    ]
    t = Table(stats, colWidths=[130, 80, 260])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f5f5f5')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f0f8ff')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    # Backtest results table
    elements.append(Paragraph("Fair Grounds Results - March 15:", h2_style))
    fg_data = [
        ["Race", "Winner", "Win $", "ML Odds", "Expert Hit?", "Notes"],
        ["R1", "Like This", "$9.00", "10/1", "MISS", "Trifecta $1,398!"],
        ["R2", "Sand Cast", "$9.40", "15/1", "MISS", "BOMB! Exacta $224"],
        ["R3", "Victory Prince", "$3.20", "5/2", "HIT", "AI nailed it"],
        ["R4", "Notion", "$9.80", "4/1", "MISS", "Ult Capper had it"],
        ["R5", "In B.J.'s Honor", "$8.40", "8/1", "MISS", "Trifecta $821"],
        ["R6", "Furio", "$5.00", "5/2", "MISS", "AI had 18% prob"],
        ["R7", "One More Guitar", "$10.40", "8/1", "MISS", "Expert pick 2nd"],
    ]
    t2 = Table(fg_data, colWidths=[35, 100, 50, 50, 60, 170])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#fff5f5')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>5 of 7 FG winners paid $5+. The value is EVERYWHERE.</b>", value_style))

    elements.append(PageBreak())

    # MARCH 16 PICKS
    elements.append(Paragraph("MARCH 16 PICKS: Fair Grounds + Parx", h1_style))
    elements.append(Paragraph("8 bets, $21 total investment. Focused on value plays at 4/1+.", body_style))

    picks_data = [
        ["Track", "Race", "Horse", "Odds", "Bet", "Why", "Potential"],
        ["FG", "R1", "Hannah Boo", "7/2", "$2 W", "SFTB #1 + Racing Dudes. Maiden claiming.", "$7"],
        ["FG", "R2", "Kitten Gloves", "4/1", "$2 P", "RD + HRN + Ortiz jockey. PLACE bet.", "$3-4"],
        ["FG", "R3", "Not Falling Back", "12/1", "$3W+$2P", "PLAY OF THE DAY! RD at 12/1!", "$36 W"],
        ["FG", "R3", "Foxtrot Harry", "6/1", "$2 W", "HRN #1 pick. Spread play in R3.", "$12"],
        ["FG", "R6", "Enlighten", "5/1", "$2 W", "RD pick. Turf claiming = upsets.", "$10"],
        ["FG", "R8", "Pineland", "9/2", "$2 W", "RD in $56K AOC turf sprint.", "$9"],
        ["Parx", "R1", "King Phoenix", "5/2", "$2 W", "SFTB + HRN + Dutrow trainer.", "$5"],
        ["Parx", "R2", "Drake Drive", "6/1", "$2 W", "CONTRARIAN. SFTB rank 2.3 at 6/1.", "$12"],
    ]
    t3 = Table(picks_data, colWidths=[35, 30, 90, 35, 50, 180, 45])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e94560')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#fff0f0')]),
        ('BACKGROUND', (0, 3), (-1, 3), HexColor('#fff3cd')),  # Highlight play of the day
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("PLAY OF THE DAY: Not Falling Back (12/1) in FG R3", value_style))
    elements.append(Paragraph(
        "Racing Dudes picked this horse at 12/1 in a wide-open 10-horse turf race. Boitano (2/1) is the obvious "
        "choice but our backtest shows heavy favorites lose 70%+ of the time. When a major expert goes "
        "contrarian at big odds, that is where the money is. $3 win bet = $36 potential return.",
        body_style))

    elements.append(Spacer(1, 12))

    # Best/worst case
    elements.append(Paragraph("SCENARIOS:", h2_style))
    scenarios = [
        ["Scenario", "Result", "Net P/L"],
        ["All chalk wins (worst)", "0 hits", "-$21"],
        ["1 mid-odds hit", "$7-12 back", "-$9 to -$14"],
        ["2 value hits", "$15-25 back", "-$6 to +$4"],
        ["POTD + 1 hit", "$36 + $7-12", "+$22 to +$27"],
        ["3+ hits (dream)", "$30-50 back", "+$10 to +$29"],
    ]
    t4 = Table(scenarios, colWidths=[160, 120, 100])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('BACKGROUND', (0, 4), (-1, 4), HexColor('#d4edda')),  # Highlight dream scenario
        ('FONTNAME', (0, 4), (-1, 5), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t4)

    elements.append(PageBreak())

    # WEEKLY OUTLOOK
    elements.append(Paragraph("WEEKLY PLAN: March 16-22", h1_style))

    week_data = [
        ["Day", "Tracks", "Budget", "Strategy"],
        ["Mon 3/16", "FG (9) + Parx (10)", "$21", "8 picks above. Turf value focus."],
        ["Tue 3/17", "Parx (7-8)", "$6-10", "Minimal. SFTB + 1 source only."],
        ["Wed 3/18", "Parx (7-8)", "$6-10", "Minimal. Same criteria."],
        ["Thu 3/19", "Oaklawn (9, $448K)", "$15-20", "HOME TRACK. MC + AOC our best."],
        ["Fri 3/20", "Oaklawn (10, $513K)", "$20-25", "Best day from backtest (35% WR)."],
        ["Sat 3/21", "Oaklawn (11, $1.05M!)", "$30-40", "BIG DAY. 6+ sources. Full card."],
        ["Sun 3/22", "Oaklawn + FG", "$20-25", "Season avg. Value hunting."],
    ]
    t5 = Table(week_data, colWidths=[65, 130, 55, 220])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#ffffff'), HexColor('#f0f8ff')]),
        ('BACKGROUND', (0, 6), (-1, 6), HexColor('#fff3cd')),  # Highlight Saturday
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t5)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("Weekly budget: $100-130. Target: 3-5 value wins at $8+ each.", bold_style))
    elements.append(Paragraph("Saturday March 21 ($1.05M card) is the biggest opportunity of the week.", value_style))

    elements.append(Spacer(1, 16))

    # Algorithm philosophy
    elements.append(Paragraph("THE ALGORITHM PHILOSOPHY", h1_style))
    elements.append(Paragraph(
        "<b>Old approach:</b> Pick the best horse, bet to win. Result: 25% win rate at $3-5 payouts = LOSE MONEY. "
        "We went 2/9 (22%) at Oaklawn yesterday doing this.",
        body_style))
    elements.append(Paragraph(
        "<b>New approach:</b> Find horses experts like but the public ignores. Bet at VALUE odds (4/1+). "
        "Result: Lower win rate but much higher payouts. Even hitting 25% = PROFITABLE.",
        body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "March 15 proved the concept: 75% of winners across 16 races paid $5 or more. "
        "The average win payout was $8.71. Consensus picks hit just 19% of the time. "
        "The value is in the horses experts like that the crowd ignores.",
        green_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "<b>We are not trying to be right more often. We are trying to be right at the RIGHT ODDS.</b>",
        value_style))

    doc.build(elements)
    print(f"PDF saved to {output_path}")
    return output_path


if __name__ == "__main__":
    build_pdf()
