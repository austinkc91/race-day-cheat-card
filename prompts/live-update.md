# Live Update Loop Prompt
#
# INSTRUCTIONS: This prompt is used by the cron job that auto-updates the cheat card
# every 10 minutes during race day. Edit the variables below before creating the cron.
#
# Variables to customize:
#   - TRACK: Track name, code, and location
#   - DATE: Race date
#   - RACE_TIMES: First and last post times
#   - AUTO_STOP: Time to stop updating (usually 30 min after last race)
#   - TRACK_SLUG: URL-friendly track name (e.g., "fair-grounds", "oaklawn")
#
# STRATEGY: This prompt implements the SELECTIVE betting approach from STRATEGY.md
# Key insight: No mechanical system beats horse racing. Only bet where you see an angle.
#
# OUTPUT: Updates JSON data file at /tmp/race_day_data/<track-slug>.json
# The web UI at port 7700 auto-refreshes every 30 seconds — no PDF needed.

RACE DAY CHEAT CARD SELF-IMPROVEMENT LOOP

You are updating the [TRACK NAME] ([TRACK CODE]) horse racing cheat card. Races run [FIRST POST] - [LAST POST] [TIMEZONE].

AUTO-STOP CHECK: First, check the current time. If it is after [AUTO_STOP_TIME], just write a short summary saying "Races are over" and do NOT update the data file.

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
Read the current data file at /tmp/race_day_data/[TRACK_SLUG].json to see what version we're on and what's already been researched.

STEP 3: APPLY THE SELECTIVE BETTING STRATEGY
Read STRATEGY.md for full details. Key principles:

ONLY RECOMMEND BETS WHERE YOU SEE A SPECIFIC ANGLE:
- VALUE PLAY horse (score >= 2.0) in CLM/MC race with 8+ starters
- Competitive field with ML favorite at 3/1+ (no heavy chalk)
- Class droppers that experts aren't picking
- GREEN consensus pick at 5/1+ ML odds (crowd vs experts disagree)

SKIP THESE RACES (no bet recommendation):
- Heavy chalk favorite (even money or 3/5) — payouts too small
- Small fields (5-6 starters) — exactas only pay $5-$8
- Stakes/MOC races — favorites win too often
- No clear angle

BET TYPES (when you have a spot):
- Exacta Key ($1-2/combo): Key your pick on top AND bottom with 2-3 contenders. 4-8 combos.
- Trifecta Box ($0.50/combo): Top 4 picks in 8+ starter CLM/MC races. Max 1-3 per card.
- Win Bet ($5-10): VALUE PLAYS only at 5/1+. Max 1-2 per card.
- Pick 3 / Daily Double: GREEN picks for singles, ML top 3 for spread. 1 per card max.

DAILY BUDGET: $50-80 (selective, not every race)

EXPERT CONSENSUS:
- Collect from 6 sources, color-code GREEN/YELLOW/ORANGE/RED
- Calculate Value Score = (consensus / sources) x ML odds. Flag >= 2.0 as VALUE PLAY.
- CRITICAL: NEVER recommend a bet on a scratched horse. Remove and recalculate.

RACE RESULTS for completed races:
- Winner, payouts, how our picks did
- Track whether our bets hit or missed

P&L TRACKING (CRITICAL — must update after Race 1 finishes):
- Update the pnl array with results for completed races
- One entry per bet placed
- Fill in result (WIN/LOSS), actual payout, and net +/-
- Keep upcoming bets as PENDING
- Update pnl_totals with running totals: wagered, returned, net, roi%
- This is the first thing Austin looks at

MODIFIERS (apply to all bets):
- WEATHER: If SLOPPY/MUDDY/HEAVY, cut ALL bets 50%. Set weather.advisory field.
- DAY-OF-WEEK: Thursday = be extra selective, reduce 30%. Friday = best day. Sat/Sun = normal.
- Display modifier in day_modifier field

BUDGET PLANS:
- $50 budget (lean — exacta keys on 2-3 best spots + 1 trifecta box)
- $80 budget (standard — exacta keys on 3-5 spots + 1-2 trifecta boxes + Pick 3)
- $120 budget (aggressive — add win bets on value plays + Daily Double)

WINDOW PHRASES:
- For EVERY recommended bet, include the EXACT phrase to say at the window
- Example: "Give me a one-dollar exacta, four on top with six and two in race five"

STEP 4: WRITE UPDATED DATA FILE
- Follow the JSON schema at ~/race-day-cheat-card/web/schema.json EXACTLY
- Write to: /tmp/race_day_data/[TRACK_SLUG].json
- Increment the version number each update
- Update race statuses: check results for completed races
- IMPORTANT: Do NOT modify bets/picks for races with status "COMPLETED" — preserve their results exactly
- For PENDING races, update with the LATEST odds, scratches, and picks
- Include timestamp so the user can see it is fresh
- Write valid JSON or the page breaks — the web UI reads this every 30 seconds

STEP 5: SUMMARY
Write a short summary: which races are done, how picks performed, any changes to upcoming picks.
Keep the summary SHORT for Telegram.
