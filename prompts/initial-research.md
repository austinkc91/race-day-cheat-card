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
   - Bet $3-5 per WIN play on GREEN picks (4+ sources) that are 5/1 or longer.
   - If a GREEN pick is under 5/1 odds, DO NOT bet Win on it. Use it for exotics only.
   - NO PLACE BETS. Place bets dilute ROI per the backtest. Skip them entirely.
   - SAVER LONGSHOT: $2-3 on any horse at 7/1+ odds that has at least 2 sources (ORANGE+). You only need 10-15% hit rate to profit. This is where BIG payouts come from.
   - VALUE PLAY: Value Score >= 2.0 at 5/1+ odds gets a $3-5 Win bet regardless of color tier.
   - Goal: 2-4 total Win bets + 1-2 saver longshots for the ENTIRE card. NOT one bet per race.
   - Daily straight bet budget: ~$12

4. EXOTIC BETS (174% ROI from backtest — this is where the real money is)
   Build using GREEN and strong YELLOW picks:

   a) TIER 1: $1 EXACTA BOX — EVERY RACE
      - Box our expert pick + a value horse = $2/race
      - Our picks finish top 2 about 38% of the time = huge edge
      - Expected: 2-3 hits/month at $50-80 each

   b) TIER 2: $1 TRIFECTA BOX — ALL GOLDMINE CLM RACES
      - Box 3 horses in EVERY CLM race with 8+ starters = $6/race
      - Play ALL qualifying CLM races, not just the best one — cast a wider net to catch monster trifectas
      - Typical card has 2-4 CLM races = $12-24 total trifecta spend
      - Expected: 1-2 hits/month at $300-1,000+

   c) TIER 3: $0.10 SUPERFECTA BOX — ONE BIG FIELD RACE
      - Box 4 horses in the biggest field of the day = $2.40 total
      - Pure lottery ticket — payouts $1,000-5,000+
      - Expected: 1 hit every 2-3 months

   d) TIER 4: PICK 3 — SATURDAYS ONLY
      - $4 for 8 combos across 3 strongest consecutive races
      - Saturday big cards only (highest purses, most data)
      - Single the GREEN picks, spread 2-3 horses in weaker legs
      - Skip Pick 3 on weekdays
      - Expected: occasional $500-1,000+ bombs

   e) DAILY DOUBLE
      - Best consecutive-race pair where both have GREEN or strong YELLOW
      - Key top pick in each leg, spread to 2 horses in weaker leg
      - Example: "$2 Daily Double: R6 #4 with R7 #2, #5" (cost: $4)

   f) WHAT TO SAY AT THE WINDOW
      - For EVERY bet, include the EXACT phrase to say at the window
      - Example: "Give me a one-dollar exacta box, numbers four and six in race five"

   Daily exotic budget: ~$15-25 (higher due to trifecta boxes on all CLM races)

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
   - $20 budget (lean — exactas every race + trifecta on best CLM only)
   - $30 budget (standard — exactas + trifecta boxes on ALL CLM races)
   - $50 budget (aggressive — full straight bets + all exotics + superfecta)
   - Show exactly which bets to make at each budget level
   - REMEMBER: No place bets at any budget level. Win only at 5/1+.
   - TRIFECTA PRIORITY: At $30+, trifecta box ALL qualifying CLM races (8+ starters). This is the key tweak — we keep barely missing $300-1,000 trifectas by only playing one race.

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
