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
Search for the LATEST information from these 6 SPECIFIC SOURCES. Focus on what has CHANGED:
1. web_search: [TRACK] SFTB picks today [DATE]
2. web_search: [TRACK] Racing Dudes picks today [DATE]
3. web_search: [TRACK] FanDuel Research picks today [DATE]
4. web_search: [TRACK] Ultimate Capper Reggie Garrett picks today [DATE]
5. web_search: [TRACK] Today's Racing Digest picks today [DATE]
6. web_search: [TRACK] AllChalk AI picks today [DATE]
7. web_search: [TRACK] results today [DATE]
8. web_search: [TRACK] scratches today
9. web_search: [TRACK] odds today [DATE]

THE 6 SOURCES (use ALL of them, every update):
1. SFTB (Sports From The Basement) — algorithmic speed ratings, workouts, past performances
2. Racing Dudes — expert handicapping (78% ITM rate)
3. FanDuel Research — data-driven win probabilities
4. Ultimate Capper (Reggie Garrett) — free expert picks
5. Today's Racing Digest — bias-aware analysis (since 1970)
6. AllChalk AI — machine learning predictions

STEP 2: READ PREVIOUS VERSION
Read /tmp/race_day_cheatcard.pdf to see what the current version contains.

STEP 3: BUILD IMPROVED PDF
Create an improved version using Python with reportlab. Save to /tmp/race_day_cheatcard.pdf (overwrite). Install reportlab first: pip install reportlab

The PDF must include:
- RACE RESULTS for any races already completed (winner, payouts, how our picks did)
- Updated picks for UPCOMING races incorporating any new scratches, odds changes, track conditions
- CRITICAL: NEVER recommend a bet on a scratched horse. If a source picked a horse that is now scratched, mark that pick as VOID and do NOT count it toward consensus. Remove scratched horses entirely from betting recommendations, consensus picks, and exotic bet tickets. Recalculate all consensus scores after removing scratches.
- Multi-source consensus from all 6 sources (SFTB, RD, FD, UC, TRD, AC)
   - LOCAL EXPERT RULE: If two or more sources are local track experts from the same track, count them as ONE combined "Local Expert" source to avoid inflating consensus artificially
   - VALUE SCORE: For each horse, calculate Value Score = (consensus_count / total_sources) × current_odds. Display in a "Value" column. Flag any horse with Value Score >= 2.0 as a "VALUE PLAY" with a star. A 3/6 pick at 8/1 (Value: 4.0) is a better bet than a 4/6 pick at 6/5 (Value: 0.8).
   - Color code: GREEN = 4+ sources, YELLOW = 3 sources, ORANGE = 2 sources, RED = 1 source
- All bet types explained (Win, Place, Show, Exacta, Trifecta, Superfecta, Daily Double, Pick 3/4/5/6)
- Boxing vs Keying vs Wheeling with cost formulas
- Exact phrases to say at betting windows
- Payout chart for all odds levels
- SAVER BET RULE: When the #1 pick is a heavy favorite (2/1 or shorter), ALWAYS include a $2-3 saver Win bet on the #2 consensus pick
- PLACE/SHOW TRACKING: Include Place/Show recommendations for each race. Track ITM% (In The Money) alongside win rate. For completed races, show whether picks finished in the money even if they didn't win.
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
