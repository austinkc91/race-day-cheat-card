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
# STRATEGY: This prompt implements the All-In Betting Strategy from STRATEGY.md
# (3-year validated, 528 races, 10,000 Monte Carlo sims, 508% ROI at $2 base)
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

STEP 3: APPLY THE BETTING STRATEGY
- WIN bets $8-10/play only at 5/1+ odds. Saver longshots $5 at 7/1+.
- Consensus tier system: GREEN (4+ sources), YELLOW (3), ORANGE (2), RED (1)
- LOCAL EXPERT RULE: Local experts from same track count as ONE source
- VALUE SCORE: (consensus/total_sources) x current_odds. Flag >= 2.0 as VALUE PLAY
- Race type targeting: CLM = GOLDMINE, MSW = longshot value, MOC/STK = SKIP
- $2 Exacta Box every race with our pick + value horse
- $2 Exacta Wheel on GREEN picks: key horse top AND bottom with 2-3 value horses (1-2 best races only)
- $2 Trifecta Box on ALL CLM races with 8+ starters (cast wider net for monster tris)
- $0.20 Superfecta Box on 2 biggest fields
- Pick 3 every day ($1/combo, 8 combos)
- Daily Double $3/combo on best consecutive pair
- Halve bets on sloppy/muddy tracks
- No place bets
- RE-CHECK ODDS: If a GREEN pick has drifted below 5/1, move it to exotics-only. If an ORANGE+ horse has drifted to 7/1+, consider as saver longshot.
- CRITICAL: NEVER recommend a bet on a scratched horse. Remove entirely and recalculate consensus.

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
- $50 budget (lean), $125 budget (standard), $200 budget (aggressive)
- NO place bets at any budget level
- At $125+: $2 exacta boxes, $2 trifecta boxes, exacta wheels on GREEN picks, Pick 3 every day

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
