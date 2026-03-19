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
# STRATEGY: This prompt implements the SELECTIVE betting approach from STRATEGY.md
# Key insight: No mechanical system beats horse racing. The edge comes from research,
# selectivity, and only betting when you see a specific angle the crowd is missing.
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

2. RACE TYPE TARGETING
   - CLM (Claiming) = Best for exotics — 42% upset rate, biggest payoffs. Focus trifecta bets here.
   - MC (Maiden Claiming) = Similar to CLM — unpredictable but juicy payouts
   - MSW (Maiden Special Weight) = Good for longshot WIN bets — highest avg win payout
   - ALW/AOC (Allowance) = Normal plays, moderate selectivity
   - SKIP Stakes/MOC races for exotics — favorites dominate, low payout value
   - Label each race with its type prominently.

3. SELECTIVE BETTING RECOMMENDATIONS
   IMPORTANT: Do NOT bet every race mechanically. Only recommend bets where you see a SPECIFIC ANGLE:

   LOOK FOR THESE SPOTS:
   - VALUE PLAY horse (score >= 2.0) in a CLM/MC race with 8+ starters
   - Competitive fields where the ML favorite is 3/1+ (no heavy chalk)
   - Class droppers that experts aren't picking
   - GREEN consensus picks at 5/1+ ML odds (crowd vs experts disagree)

   SKIP THESE RACES:
   - Heavy chalk favorite (even money or 3/5) — payouts too small
   - Small fields (5-6 starters) — exactas only pay $5-$8
   - Stakes/MOC races — favorites win too often
   - No clear angle — don't bet just because there's a race

   BET TYPES (when you have a spot):

   a) EXACTA KEY ($1-2/combo)
      - KEY your strongest pick on top AND bottom with 2-3 contenders
      - Cost: $4-12 per race, only 4-8 combos (NOT 20)
      - Only in races with an angle

   b) TRIFECTA BOX ($0.50/combo, 8+ starters, 1-3 races per card)
      - Box your top 4 picks (mix of ML rank and consensus)
      - 24 combos x $0.50 = $12/race
      - Only play 1-3 best CLM/MC races per card
      - One $100+ trifecta hit makes the whole day

   c) WIN BET ($5-10, VALUE PLAYS only)
      - Only on horses with Value Score >= 2.0 AND at 5/1+ ML
      - Max 1-2 win bets per entire card

   d) PICK 3 / DAILY DOUBLE (1 per card max)
      - Use GREEN picks for singling, ML top 3 for spread legs
      - $1/combo, 6-8 combos = $6-8

   e) WHAT TO SAY AT THE WINDOW
      - For EVERY bet, include the EXACT phrase to say at the window
      - Example: "Give me a one-dollar exacta, four on top with six and two in race five"

   DAILY BUDGET: $50-80 (selective, not every race)

4. WEATHER & TRACK CONDITION CHECK
   - Search for current weather and track conditions at the venue
   - If track is SLOPPY, MUDDY, or HEAVY:
     * Display WARNING banner: "OFF TRACK — CUT ALL BETS IN HALF"
     * Halve all recommended bet amounts
   - Display current track condition prominently at the top

5. DAY-OF-WEEK NOTE
   - Thursday: Worst day historically — be extra selective, reduce sizing 30%
   - Friday: Best day — normal sizing
   - Saturday/Sunday/Monday-Wednesday: Normal sizing

6. BUDGET PLANS
   - $50 budget (lean — exacta keys on 2-3 best spots + 1 trifecta box)
   - $80 budget (standard — exacta keys on 3-5 spots + 1-2 trifecta boxes + Pick 3)
   - $120 budget (aggressive — add win bets on value plays + Daily Double)
   - Show exactly which bets to make at each budget level

7. QUICK REFERENCE
   - Table key / legend for abbreviations
   - Race type guide (CLM = best for exotics, MSW = longshot value, SKIP Stakes/MOC)
   - Track bias data (inside/outside, speed/closer)
   - Track tips (parking, food, viewing spots)
   - ONE-SENTENCE STRATEGY: "Only bet races where you see a specific angle — a value play, a class dropper, or a competitive field with no clear favorite."

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
