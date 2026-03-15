# Initial Cheat Card Research Prompt
#
# INSTRUCTIONS: Edit the variables below, then send this entire prompt as a job
# to your linux-mini-agent (via Telegram or `just send`).
#
# Variables to customize:
#   - TRACK: Track name and location
#   - DATE: Race date
#   - EMAILS: Email addresses to send the PDF to

I want you to do deep research today on the horse races at [TRACK NAME] [LOCATION] on [DATE].

I want to know:
- The full schedule with race times and post times
- All entries for every race (horse name, jockey, trainer, morning line odds)
- Current scratches
- Which horses are supposed to do the best based on expert picks and handicapping analysis

Build a professional PDF cheat card that includes:

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

2. TOP PLAYS ONLY (This is the most important section)
   - ONLY recommend Win/Place bets on GREEN picks (4+ sources agree)
   - If no GREEN picks exist, take the single strongest YELLOW pick as a lone play
   - For GREEN picks: $10 Win + $5 Place
   - SAVER BET: When a GREEN pick is a heavy favorite (2/1 or shorter), add a $3 saver Win bet on the next-best consensus pick in that race
   - VALUE PLAY: If any horse has Value Score >= 3.0 (strong consensus at big odds), add a $3 Win saver on it regardless of tier
   - SKIP everything else. No Win bets on ORANGE or RED picks. Period.
   - Goal: 2-4 total Win bets for the entire card, not one per race

3. EXOTIC BETS (The fun stuff)
   Build these exotic plays using ONLY GREEN and strong YELLOW picks:

   a) EXACTA PLAYS
      - In any race with a GREEN pick, key that horse on top over the next 2-3 consensus picks
      - Example: "$1 Exacta Key: #4 over #2, #6, #8" (cost: $3)
      - Only in races where you have a strong opinion on the winner

   b) TRIFECTA PLAYS
      - In the best 1-2 races of the day (GREEN picks with clear separation), build a trifecta box or key
      - Key the GREEN pick on top, box the next 3 picks underneath
      - Example: "$0.50 Trifecta Key: #4 with #2, #6, #8" (cost: $3)

   c) DAILY DOUBLE
      - Find the best consecutive-race pair where both races have GREEN or strong YELLOW picks
      - Key the top pick in each leg, spread to 2 horses in the weaker leg
      - Example: "$2 Daily Double: R6 #4 with R7 #2, #5" (cost: $4)

   d) PICK 3 / PICK 4 (if card supports it)
      - Build ONE Pick 3 using the strongest 3 consecutive races
      - Single the GREEN picks, spread to 2-3 horses in weaker legs
      - Keep total cost under $20
      - Example: "$1 Pick 3: R6 #4 / R7 #2, #5 / R8 #3" (cost: $2)

   e) WHAT TO SAY AT THE WINDOW
      - For every exotic bet, include the EXACT phrase to say at the betting window
      - Example: "Give me a one-dollar exacta, number four on top over two, six, and eight in race five"

4. WEATHER & TRACK CONDITION CHECK
   - Search for current weather and track conditions at the venue
   - If track is SLOPPY, MUDDY, or HEAVY:
     * Display WARNING banner: "OFF TRACK — CUT ALL BETS IN HALF"
     * Halve all recommended bet amounts
     * Our backtest showed 0% win rate on sloppy tracks — this is the #1 risk factor
   - Display current track condition prominently at the top

5. DAY-OF-WEEK NOTE
   - Thursday: Reduce all bets 30% (worst day in backtest, 27.8% win rate)
   - Friday: Best day (35% win rate) — full sizing
   - Saturday/Sunday: Normal sizing

6. BUDGET PLANS (already reflecting all modifiers)
   - $30 budget (tight — Win bets on GREEN picks only, one exacta)
   - $50 budget (moderate — Win/Place on GREEN picks, exactas, one trifecta or daily double)
   - $100 budget (full card — all recommended plays including Pick 3/4)
   - Show exactly which bets to make at each budget level

7. QUICK REFERENCE
   - Table key / legend for abbreviations
   - Track bias data (inside/outside, speed/closer)
   - Track tips (parking, food, viewing spots)

PDF FORMATTING:
- Use Python reportlab library
- Proper margins (72pt all sides)
- Font sizes: Title 18pt, Headers 14pt, Body 10pt
- No text overlap, proper line spacing
- Clean professional layout with color coding
- TOP PLAYS and EXOTIC BETS sections should be the most prominent — these are what the user is betting from

Save the PDF to /tmp/race_day_cheatcard.pdf

Email the PDF to: [EMAIL1], [EMAIL2]
Use SMTP with the Google App Password from /home/austin/linux-mini-agent/.env (GOOGLE_APP_PASSWORD).
Send from vacypert@gmail.com.
Subject: [TRACK NAME] Race Day Cheat Card - [DATE]

Also attach /tmp/race_day_cheatcard.pdf to this job's attachments for Telegram delivery.
