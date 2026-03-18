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
# STRATEGY: This prompt implements the ML-Driven Betting Strategy from STRATEGY.md
# Key insight: Morning Line top 5 catches 80%+ of exactas vs 30% for expert consensus
# Backtested: 36-41% ROI, 100% days profitable across Parx + Fair Grounds
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

STEP 3: APPLY THE ML-DRIVEN BETTING STRATEGY
CRITICAL: Use MORNING LINE ODDS (not expert consensus) to select horses for exotic bets.
Sort all active (non-scratched) horses by ML odds, lowest first. Top 5 by ML = your exotic bet horses.

EXOTIC BETS (core strategy, 36% ROI backtested):
- $0.50 Exacta Box top 5 by ML — EVERY RACE (20 combos = $10/race)
- $0.50 Trifecta Box top 4 by ML — races with 7+ starters (24 combos = $12/race)
- $3 Show bet on #1 ML pick — EVERY RACE
- Pick 3 every day ($1/combo, 8 combos, use GREEN picks for singles)
- Daily Double $3/combo on best consecutive pair (key top ML)
- Halve bets on sloppy/muddy tracks

OPTIONAL STRAIGHT BETS:
- WIN bets $5-8/play only at 5/1+ ML odds with expert consensus support
- No place bets

EXPERT CONSENSUS (secondary signal):
- Still collect from 6 sources and color-code GREEN/YELLOW/ORANGE/RED
- Use for Pick 3 singling and Daily Double keying
- Use as confidence boost for WIN bet selection
- Do NOT use for exacta/trifecta horse selection — ML is superior

- CRITICAL: NEVER recommend a bet on a scratched horse. Remove entirely and recalculate ML rankings.
- RE-CHECK ODDS: If live odds differ significantly from ML, use CURRENT live odds for ML ranking.

RACE RESULTS for completed races:
- Winner, payouts, how our picks did
- Track whether our picks hit WIN or missed
- Note: NO place tracking since we don't bet Place

P&L TRACKING (CRITICAL — must update after Race 1 finishes):
- Update the pnl array with results for completed races
- One entry per bet placed
- Fill in result (WIN/LOSS), actual payout, and net +/-
- Keep upcoming bets as PENDING
- Update pnl_totals with running totals: wagered, returned, net, roi%
- This is the first thing Austin looks at

MODIFIERS (apply to all bets):
- WEATHER: If SLOPPY/MUDDY/HEAVY, cut ALL bets 50%. Set weather.advisory field.
- DAY-OF-WEEK: Thursday = reduce 30%, Friday = best day (full), Sat/Sun = normal
- Display modifier in day_modifier field

BUDGET PLANS:
- $80 budget (lean — ML4 $0.50 exacta + show bets only)
- $150 budget (standard — ML5 $0.50 exacta + ML4 $0.50 tri 7+st + show + Pick 3 + DD)
- $250 budget (aggressive — ML5 $1 exacta + ML4 $1 tri + WIN bets + Pick 4)
- Use ML rankings for ALL exotic horse selection at every budget level

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
