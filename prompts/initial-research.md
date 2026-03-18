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
# STRATEGY: This prompt implements the ML-Driven Betting Strategy from STRATEGY.md
# Key insight: Morning Line top 5 catches 80%+ of exactas vs 30% for expert consensus
# Backtested: 36-41% ROI, 100% days profitable across Parx + Fair Grounds
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

3. ML-DRIVEN EXOTIC BETS (36% ROI — THE CORE MONEY MAKER)
   CRITICAL: Use MORNING LINE ODDS (not expert consensus) to select horses for exotic bets.
   Sort all active (non-scratched) horses by ML odds, lowest first. The top 5 by ML are your exotic bet horses.

   a) TIER 1: $0.50 EXACTA BOX — TOP 5 BY ML — EVERY RACE
      - Box the 5 horses with the lowest (best) morning line odds = 20 combos x $0.50 = $10/race
      - Hit rate: 80%+ of all races (backtested). The track handicapper who sets ML watches workouts and knows the horses.
      - Expert consensus only catches 30% of exactas. ML catches 80%+. This is the key insight.
      - Average exacta payout at $0.50/combo: $3-$41 per hit.
      - Budget: ~$100/day for a 10-race card.

   b) TIER 2: $0.50 TRIFECTA BOX — TOP 4 BY ML — RACES WITH 7+ STARTERS
      - Box the 4 horses with the lowest ML odds = 24 combos x $0.50 = $12/race
      - Only play races with 7+ starters (enough field depth for meaningful payouts).
      - Hit rate: ~30% of qualifying races. Pays $47-$234 per hit at $0.50/combo.
      - Typical card has 4-6 qualifying races = $48-$72 in trifecta spend.

   c) TIER 3: $3 SHOW BET — #1 ML PICK — EVERY RACE
      - Bet $3 show on the horse with the lowest morning line odds every race.
      - Hit rate: ~60%. Provides steady small returns that offset exacta misses.
      - Budget: ~$30/day for a 10-race card.

   d) TIER 4: PICK 3 — EVERY DAY
      - $1/combo, 8 combos across 3 strongest consecutive races = $8/day
      - Use expert GREEN picks for singling, ML top 3 for spread legs

   e) TIER 5: DAILY DOUBLE
      - $3/combo on best consecutive pair. Key top ML pick, spread to top 2-3 ML in weaker leg.

   f) WHAT TO SAY AT THE WINDOW
      - For EVERY bet, include the EXACT phrase to say at the window
      - Example: "Give me a fifty-cent exacta box, numbers four, six, two, nine, and one in race five"

   Daily exotic budget: ~$150 (ML5 exactas + ML4 trifectas + show bets + multi-race)

4. OPTIONAL STRAIGHT BETS (for bigger days)
   - WIN bets $5-8/play ONLY at 5/1+ ML odds on horses that also have expert consensus (YELLOW+).
   - Max 1 WIN bet per race, only on the shortest ML horse in the 5/1-12/1 range.
   - Expert consensus adds confidence but is NOT required for exotic selection.
   - NO PLACE BETS. Place bets dilute ROI.
   - Daily straight bet budget (optional): ~$30-50

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
   - $80 budget (lean — $0.50 exacta box top 4 by ML + $3 show bets only)
   - $150 budget (standard — full strategy: ML5 $0.50 exacta + ML4 $0.50 tri 7+st + show + Pick 3 + DD)
   - $250 budget (aggressive — $1 exacta box ML5 + $1 tri ML4 + WIN bets + Pick 4 on Saturdays)
   - Show exactly which bets to make at each budget level
   - REMEMBER: Use ML rankings for all exotic horse selection. Expert consensus for multi-race singles.
   - TRIFECTA PRIORITY: At $150+, trifecta box top 4 ML in ALL races with 7+ starters.
   - EXACTA PRIORITY: ML5 exacta box EVERY race at all budget levels. This is the backbone.

8. QUICK REFERENCE
   - Table key / legend for abbreviations
   - Race type guide (CLM = goldmine, MSW = longshot value, SKIP Stakes/MOC)
   - Track bias data (inside/outside, speed/closer)
   - Track tips (parking, food, viewing spots)
   - ONE-SENTENCE STRATEGY: "Use morning line top 5 for exacta boxes and top 4 for trifecta boxes on every race — the track handicapper beats expert consensus for exotic bet selection."

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
