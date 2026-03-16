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
#
# STRATEGY: This prompt implements the All-In Betting Strategy from STRATEGY.md
# (3-year validated, 528 races, 10,000 Monte Carlo sims, 508% ROI at $2 base)

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

RACE TYPE TARGETING (from 3-year backtest):
- Label every race with its type (CLM, MSW, ALW, STK, MOC)
- CLM (Claiming) = GOLDMINE — prioritize for all bet types
- MSW = Great for longshot value
- SKIP Stakes/MOC for straight bets — too chalky, favorites win too often

TOP PLAYS — STRAIGHT BETS (most important section):
CRITICAL BACKTESTED RULES (86% ROI):
- WIN BETS ONLY AT 5/1+ ODDS. Never bet chalk/favorites — negative ROI per backtest.
- Bet $3-5 per WIN play on GREEN picks (4+ sources) that are 5/1 or longer.
- If a GREEN pick is under 5/1 odds, DO NOT bet Win. Use for exotics only.
- NO PLACE BETS. They dilute ROI. Skip entirely.
- SAVER LONGSHOT: $2-3 on any horse at 7/1+ odds with at least 2 sources (ORANGE+).
- VALUE PLAY: Value Score >= 2.0 at 5/1+ odds gets $3-5 Win bet regardless of tier.
- Goal: 2-4 Win bets + 1-2 saver longshots for the ENTIRE card.
- Daily straight bet budget: ~$12

EXOTIC BETS (174% ROI — where the real money is):
- TIER 1: $1 EXACTA BOX every race (expert pick + value horse = $2/race)
- TIER 2: $0.50 TRIFECTA BOX in best CLM races with 10+ starters ($3 total)
- TIER 3: $0.10 SUPERFECTA BOX in one big field race ($2.40 total)
- TIER 4: PICK 3 on SATURDAYS ONLY ($4 for 8 combos) — skip on weekdays
- DAILY DOUBLE: Best consecutive pair with strong picks
- Include EXACT phrases to say at the betting window for EVERY bet
- Daily exotic budget: ~$11

RACE RESULTS for completed races:
- Winner, payouts, how our picks did
- Track whether our picks hit WIN or missed
- Note: NO place tracking since we don't bet Place

Updated picks for UPCOMING races:
- Incorporate new scratches, odds changes, track conditions
- CRITICAL: NEVER recommend a bet on a scratched horse. Remove entirely and recalculate consensus.
- Multi-source consensus from all 6 sources
- LOCAL EXPERT RULE: Local experts from same track count as ONE source
- VALUE SCORE: (consensus/total_sources) x current_odds. Flag >= 2.0 as VALUE PLAY
- Color code: GREEN = 4+, YELLOW = 3, ORANGE = 2, RED = 1
- RE-CHECK ODDS: If a GREEN pick has drifted below 5/1, move it to exotics-only. If an ORANGE+ horse has drifted to 7/1+, consider as saver longshot.

MODIFIERS (apply to all bets):
- WEATHER: If SLOPPY/MUDDY/HEAVY, cut ALL bets 50%. Display WARNING banner.
- DAY-OF-WEEK: Thursday = reduce 30%, Friday = best day (full), Sat/Sun = normal
- Display track condition and day modifier at top of PDF

BUDGET PLANS (reflecting all modifiers):
- $23 budget (backtested optimal), $30 budget, $50 budget
- NO place bets at any budget level

Version number and timestamp so the user can see it is fresh.

IMPORTANT PDF FORMATTING:
- Use reportlab with proper margins (72pt all sides)
- Font sizes: Title 18pt, Headers 14pt, Body 10pt
- NO text overlap. Use proper line spacing.
- Clean professional layout with color coding

CRITICAL LAYOUT RULE — BETS BELOW EACH RACE:
- For EVERY race, immediately below the horse table, show a prominent "BETS FOR THIS RACE" box
- This box should have a colored background (light green or light blue) so it stands out
- List EVERY bet for that specific race: Win bet, Saver, Exacta box, Trifecta, Superfecta, Daily Double
- Include "what to say at the window" phrase for each bet
- If NO bets qualify, show "BETS: $1 Exacta Box only"
- The user should look at ONE race and immediately see every bet to make
- Do NOT put bets in a separate section — they MUST be directly below each race table
- Budget plans and summary can still appear at the end

STEP 4: EMAIL IT
Email the PDF to [EMAIL]. Use SMTP with the app password from /home/austin/linux-mini-agent/.env (GOOGLE_APP_PASSWORD). Send from vacypert@gmail.com.
Subject: [TRACK] Cheat Card - Updated [current time]
Body: Brief note on what changed — focus on any pick changes, new results, or scratches.

STEP 5: ATTACH TO JOB
Add /tmp/race_day_cheatcard.pdf to job attachments so the user gets it in Telegram too.

STEP 6: SUMMARY
Write a short summary: which races are done, how picks performed, any changes to upcoming picks.
