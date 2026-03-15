# Live Update Loop Prompt
#
# INSTRUCTIONS: This prompt is used by the cron job that auto-updates the cheat card
# every 10 minutes during race day. Edit the variables below before creating the cron.
#
# Variables to customize:
#   - TRACK: Track name and location
#   - DATE: Race date
#   - RACE_TIMES: First and last post times
#   - AUTO_STOP: Time to stop updating (usually 30 min after last race)
#   - EMAIL: Email address for delivery
#   - PDF_PATH: Where to save the PDF (default: /tmp/race_day_cheatcard.pdf)

RACE DAY CHEAT CARD SELF-IMPROVEMENT LOOP

You are updating the [TRACK NAME] horse racing cheat card. Races run [FIRST POST] - [LAST POST] [TIMEZONE].

AUTO-STOP CHECK: First, check the current time. If it is after [AUTO_STOP_TIME], just write a short summary saying "Races are over" and do NOT generate a new PDF.

STEP 1: RESEARCH LATEST DATA
Search for the LATEST information. Focus on what has CHANGED:
1. web_search: [TRACK] results today [DATE]
2. web_search: [TRACK] scratches today
3. web_search: [TRACK] odds today [DATE]
4. web_search: [TRACK] racing picks today expert
5. web_search: [TRACK] [STAKES RACE 1] picks and [TRACK] [STAKES RACE 2] picks

STEP 2: READ PREVIOUS VERSION
Read /tmp/race_day_cheatcard.pdf to see what the current version contains.

STEP 3: BUILD IMPROVED PDF
Create an improved version using Python with reportlab. Save to /tmp/race_day_cheatcard.pdf (overwrite). Install reportlab first: pip install reportlab

The PDF must include:
- RACE RESULTS for any races already completed (winner, payouts, how our picks did)
- Updated picks for UPCOMING races incorporating any new scratches, odds changes, track conditions
- CRITICAL: NEVER recommend a bet on a scratched horse. If a source picked a horse that is now scratched, mark that pick as VOID and do NOT count it toward consensus. Remove scratched horses entirely from betting recommendations, consensus picks, and exotic bet tickets. Recalculate all consensus scores after removing scratches.
- Multi-source consensus algorithm picks
- All bet types explained (Win, Place, Show, Exacta, Trifecta, Superfecta, Daily Double, Pick 3/4/5/6)
- Boxing vs Keying vs Wheeling with cost formulas
- Exact phrases to say at betting windows
- Payout chart for all odds levels
- Budget strategies ($50, $100, $150+)
- Track bias data and pro tips
- Version number and timestamp so the user can see it is fresh

IMPORTANT PDF FORMATTING:
- Use reportlab with proper margins (72pt all sides)
- Font sizes: Title 18pt, Headers 14pt, Body 10pt
- NO text overlap. Use proper line spacing.
- Use colors for consensus strength (green = strong pick, yellow = moderate, red = longshot)
- Clean professional layout

STEP 4: EMAIL IT
Email the PDF to [EMAIL]. Use SMTP with the app password from /home/austin/linux-mini-agent/.env (GOOGLE_APP_PASSWORD). Send from vacypert@gmail.com.
Subject: [TRACK] Cheat Card - Updated [current time]
Body: Brief note on what changed in this version.

STEP 5: ATTACH TO JOB
Add /tmp/race_day_cheatcard.pdf to job attachments so the user gets it in Telegram too.

STEP 6: SUMMARY
Write a short summary of what was improved and key changes.
