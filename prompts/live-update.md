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

STEP 2: READ PREVIOUS VERSION
Read /tmp/race_day_cheatcard.pdf to see what the current version contains.

STEP 3: BUILD IMPROVED PDF
Create an improved version using Python with reportlab. Save to /tmp/race_day_cheatcard.pdf (overwrite). Install reportlab first: pip install reportlab

The PDF must include:

TOP PLAYS ONLY (most important section):
- ONLY recommend Win/Place bets on GREEN picks (4+ sources)
- If no GREEN picks exist, take the single strongest YELLOW as a lone play
- GREEN picks: $10 Win + $5 Place
- SAVER BET: When GREEN pick is heavy favorite (2/1 or shorter), add $3 saver Win on next-best consensus pick
- VALUE PLAY: If any horse has Value Score >= 3.0, add $3 Win saver regardless of tier
- SKIP ORANGE and RED for Win bets. Goal: 2-4 total Win bets for the card.

EXOTIC BETS (using GREEN and strong YELLOW picks only):
- EXACTA: Key GREEN pick on top over next 2-3 consensus picks ($1 exacta key)
- TRIFECTA: In best 1-2 races, key GREEN pick over next 3 ($0.50 trifecta key)
- DAILY DOUBLE: Best consecutive-race pair with strong picks
- PICK 3/4: ONE pick 3 using strongest consecutive races, single the GREEN picks, spread weaker legs, keep under $20
- Include EXACT phrases to say at the betting window for every exotic

RACE RESULTS for completed races:
- Winner, payouts, how our picks did
- Track whether our picks hit WIN, PLACE, SHOW, or missed entirely

Updated picks for UPCOMING races:
- Incorporate new scratches, odds changes, track conditions
- CRITICAL: NEVER recommend a bet on a scratched horse. Remove entirely and recalculate consensus.
- Multi-source consensus from all 6 sources
- LOCAL EXPERT RULE: Local experts from same track count as ONE source
- VALUE SCORE: (consensus/total_sources) x current_odds. Flag >= 2.0 as VALUE PLAY
- Color code: GREEN = 4+, YELLOW = 3, ORANGE = 2, RED = 1

MODIFIERS (apply to all bets):
- WEATHER: If SLOPPY/MUDDY/HEAVY, cut ALL bets 50%. Display WARNING banner.
- DAY-OF-WEEK: Thursday = reduce 30%, Friday = best day (full), Sat/Sun = normal
- Display track condition and day modifier at top of PDF

BUDGET PLANS (reflecting all modifiers):
- $30 budget (tight), $50 budget (moderate), $100 budget (full card)

Version number and timestamp so the user can see it is fresh.

IMPORTANT PDF FORMATTING:
- Use reportlab with proper margins (72pt all sides)
- Font sizes: Title 18pt, Headers 14pt, Body 10pt
- NO text overlap. Use proper line spacing.
- TOP PLAYS and EXOTIC BETS should be the most prominent sections
- Clean professional layout with color coding

STEP 4: EMAIL IT
Email the PDF to [EMAIL]. Use SMTP with the app password from /home/austin/linux-mini-agent/.env (GOOGLE_APP_PASSWORD). Send from vacypert@gmail.com.
Subject: [TRACK] Cheat Card - Updated [current time]
Body: Brief note on what changed — focus on any pick changes, new results, or scratches.

STEP 5: ATTACH TO JOB
Add /tmp/race_day_cheatcard.pdf to job attachments so the user gets it in Telegram too.

STEP 6: SUMMARY
Write a short summary: which races are done, how picks performed, any changes to upcoming picks.
