# Initial Cheat Card Research Prompt
#
# INSTRUCTIONS: Edit the variables below, then send this entire prompt as a job
# to your linux-mini-agent (via Telegram or `just send`).
#
# Variables to customize:
#   - TRACK: Track name, code, and location
#   - DATE: Race date
#   - TRACK_SLUG: URL-friendly track name (e.g., "fair-grounds", "oaklawn")
#
# STRATEGY: This prompt implements the All-In Betting Strategy from STRATEGY.md
# (3-year validated, 528 races, 10,000 Monte Carlo sims, 508% ROI at $2 base)
#
# OUTPUT: JSON data file at /tmp/race_day_data/<track-slug>.json
# The web UI at port 7700 auto-refreshes every 30 seconds — no PDF needed.

I want you to do deep research today on the horse races at [TRACK NAME] ([TRACK CODE]) in [LOCATION] on [DATE].

I want to know:
- The full schedule with race times and post times
- All entries for every race (horse name, jockey, trainer, morning line odds)
- Race types for every race (CLM, MSW, ALW, STK, MOC, etc.)
- Current scratches
- Which horses are supposed to do the best based on expert picks and handicapping analysis

Build a comprehensive cheat card data file that includes:

1. RACE-BY-RACE ANALYSIS
   - Pull picks from these 6 specific sources:
     1. SFTB (Sports From The Basement) — algorithmic speed ratings, workouts, past performances
     2. Racing Dudes — expert handicapping (78% ITM rate)
     3. FanDuel Research — data-driven win probabilities
     4. Ultimate Capper (Reggie Garrett) — free expert picks
     5. Today's Racing Digest — bias-aware analysis (since 1970)
     6. AllChalk AI — machine learning predictions
   - Score each horse by consensus: how many of the 6 sources pick them
   - LOCAL EXPERT RULE: If two or more sources are local track experts from the same track (e.g., Nancy Holthus + Matt Dinerman at Oaklawn), count them as ONE combined "Local Expert" source. They tend to agree on picks and inflate consensus artificially.
   - VALUE SCORE: For each horse, calculate Value Score = (consensus_count / total_sources) x morning_line_odds. Flag any horse with Value Score >= 2.0 as a "VALUE PLAY".
   - Color code by confidence: GREEN = 4+ sources, YELLOW = 3 sources, ORANGE = 2 sources, RED = 1 source
   - Mark scratches clearly with (SCR) label
   - CRITICAL: NEVER recommend a bet on a scratched horse. Remove scratched horses entirely from picks and recalculate consensus.

2. RACE TYPE TARGETING (from 3-year backtest)
   - CLM (Claiming) = GOLDMINE — 22.6% upset rate, avg 9.6 starters, biggest exotic payouts. PRIORITIZE these races for all bet types.
   - MSW (Maiden Special Weight) = Great for longshot value — highest avg win payout ($17.38)
   - ALW (Allowance) = Normal plays
   - SKIP Stakes/MOC races — Too chalky, favorites win too often, low exotic value. Do NOT recommend Win bets in Stakes/MOC races. Exotics only if consensus is very strong.
   - Label each race with its type prominently.

3. TOP PLAYS — STRAIGHT BETS (Most important section)
   CRITICAL RULES FROM BACKTEST (86% ROI, 70% profitable days):
   - WIN BETS ONLY AT 5/1+ ODDS. Never bet chalk (favorites). Expert consensus picks have NEGATIVE ROI on win bets at short odds. 79% of all winners paid $5+ (non-chalk).
   - Bet $8-10 per WIN play on GREEN picks (4+ sources) that are 5/1 or longer.
   - If a GREEN pick is under 5/1 odds, DO NOT bet Win on it. Use it for exotics only.
   - NO PLACE BETS. Place bets dilute ROI per the backtest. Skip them entirely.
   - SAVER LONGSHOT: $5 on any horse at 7/1+ odds that has at least 2 sources (ORANGE+). You only need 10-15% hit rate to profit. This is where BIG payouts come from.
   - VALUE PLAY: Value Score >= 2.0 at 5/1+ odds gets a $8-10 Win bet regardless of color tier.
   - Goal: 2-4 total Win bets + 1-2 saver longshots for the ENTIRE card. NOT one bet per race.
   - Daily straight bet budget: ~$35

4. EXOTIC BETS (174% ROI from backtest — this is where the real money is)
   Build using GREEN and strong YELLOW picks:

   a) TIER 1: $2 EXACTA BOX — EVERY RACE
      - Box our expert pick + a value horse = $4/race
      - Our picks finish top 2 about 38% of the time = huge edge
      - At $2 base, hits pay $100-160. Expected: 2-3 hits/month.

   b) TIER 1b: $2 EXACTA WHEEL — GREEN PICKS ONLY
      - When a GREEN consensus pick exists, KEY that horse on top AND bottom with 2-3 value horses.
      - Example: "$2 exacta wheel #4 with #1,#6,#8" = $6 top + $6 bottom = $12/race
      - Better coverage than a box — covers more finish combos involving your strongest pick
      - Only on the 1-2 best races per card. Budget: ~$12/day.

   c) TIER 2: $2 TRIFECTA BOX — ALL GOLDMINE CLM RACES
      - Box 3 horses in EVERY CLM race with 8+ starters = $12/race
      - Play ALL qualifying CLM races — cast a wider net for monster trifectas
      - Typical card has 2-4 CLM races = $24-48 total trifecta spend
      - At $2 base, hits pay $600-2,000+. Expected: 1-2 hits/month.

   d) TIER 3: $0.20 SUPERFECTA BOX — TWO BIG FIELD RACES
      - Box 4 horses in the TWO biggest fields = $4.80 each = ~$10 total
      - More shots at $1,000-5,000+ payouts. Expected: 1 hit every 1-2 months.

   e) TIER 4: PICK 3 — EVERY DAY
      - $1/combo, 8 combos across 3 strongest consecutive races = $8/day
      - No longer Saturday-only — more chances at $500-1,000+ bombs
      - Single the GREEN picks, spread 2-3 horses in weaker legs

   f) DAILY DOUBLE
      - Best consecutive-race pair where both have GREEN or strong YELLOW
      - $3/combo, key top pick in each leg, spread to 2 horses in weaker leg
      - Example: "$3 Daily Double: R6 #4 with R7 #2, #5" (cost: $6)

   f) WHAT TO SAY AT THE WINDOW
      - For EVERY bet, include the EXACT phrase to say at the window
      - Example: "Give me a one-dollar exacta box, numbers four and six in race five"

   Daily exotic budget: ~$90 (exactas + wheels + trifectas + superfectas + multi-race)

5. WEATHER & TRACK CONDITION CHECK
   - Search for current weather and track conditions at the venue
   - If track is SLOPPY, MUDDY, or HEAVY:
     * Display WARNING banner: "OFF TRACK — CUT ALL BETS IN HALF"
     * Halve all recommended bet amounts
     * Our backtest showed sloppy track days are unpredictable — cut exposure by 50%
   - Display current track condition prominently at the top

6. DAY-OF-WEEK NOTE
   - Thursday: Reduce all bets 30% (worst day in backtest, 27.8% win rate)
   - Friday: Best day (35% win rate) — full sizing
   - Saturday/Sunday: Normal sizing
   - Monday-Wednesday: Normal sizing

7. BUDGET PLANS (reflecting all modifiers above)
   - $50 budget (lean — $5 WIN bets, $1 exacta boxes, $1 tri on best CLM only)
   - $125 budget (standard — full strategy: $8-10 WIN bets, $2 exacta boxes + wheels, $2 tri on ALL CLM, Pick 3 + DD + superfecta)
   - $200 budget (aggressive — $15 WIN bets, $3 exacta boxes + wheels, $3 tri, Pick 4 on Saturdays)
   - Show exactly which bets to make at each budget level
   - REMEMBER: No place bets at any budget level. Win only at 5/1+.
   - TRIFECTA PRIORITY: At $125+, trifecta box ALL qualifying CLM races (8+ starters) at $2/box.
   - EXACTA WHEEL PRIORITY: At $125+, add exacta wheels on the 1-2 strongest GREEN picks.

8. QUICK REFERENCE
   - Table key / legend for abbreviations
   - Race type guide (CLM = goldmine, MSW = longshot value, SKIP Stakes/MOC)
   - Track bias data (inside/outside, speed/closer)
   - Track tips (parking, food, viewing spots)
   - ONE-SENTENCE STRATEGY: "Stop betting favorites, bet WIN only at 5/1+, use expert picks for exacta/trifecta boxes where their 51% board rate is an edge, and target claiming races with big fields."

OUTPUT — WRITE JSON DATA FILE:
- Follow the JSON schema at ~/race-day-cheat-card/web/schema.json EXACTLY
- Create the directory first: mkdir -p /tmp/race_day_data
- Write to: /tmp/race_day_data/[TRACK_SLUG].json
- The web UI at port 7700 auto-refreshes every 30 seconds — it will pick up your data immediately
- Write valid JSON or the page breaks
- Include version "v1.0" and increment on updates

SET UP AUTO-UPDATE CRON:
After writing the initial data file, create a cron job via the Listen server so the card stays updated:
- POST to http://localhost:7600/cron
- Schedule: "*/10 * * * *" (every 10 minutes)
- Name: "Cheat Card: [TRACK NAME]"
- Prompt: Use the live-update prompt from ~/race-day-cheat-card/prompts/live-update.md with variables filled in

Also attach a screenshot or summary to this job for Telegram delivery so Austin knows the card is live.
