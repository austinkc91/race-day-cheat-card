# Initial Cheat Card Research Prompt
#
# INSTRUCTIONS: Edit the variables below, then send this entire prompt as a job
# to your linux-mini-agent (via Telegram or `just send`).
#
# Variables to customize:
#   - TRACK: Track name and location
#   - DATE: Race date
#   - EMAILS: Email addresses to send the PDF to
#   - STAKES: Any featured stakes races to focus on

I want you to do deep research today on the horse races at [TRACK NAME] [LOCATION] on [DATE].

I want to know:
- The full schedule with race times and post times
- All entries for every race (horse name, jockey, trainer, morning line odds)
- Current scratches
- Which horses are supposed to do the best based on expert picks and handicapping analysis

Build a professional PDF cheat card that includes:

1. RACE-BY-RACE PICKS
   - Pull picks from these 6 specific sources:
     1. SFTB (Sports From The Basement) — algorithmic speed ratings, workouts, past performances
     2. Racing Dudes — expert handicapping (78% ITM rate)
     3. FanDuel Research — data-driven win probabilities
     4. Ultimate Capper (Reggie Garrett) — free expert picks
     5. Today's Racing Digest — bias-aware analysis (since 1970)
     6. AllChalk AI — machine learning predictions
   - Score each horse by consensus: how many of the 6 sources pick them
   - LOCAL EXPERT RULE: If two or more sources are local track experts from the same track (e.g., Nancy Holthus + Matt Dinerman at Oaklawn), count them as ONE combined "Local Expert" source. They tend to agree on picks and inflate consensus artificially. Always use independent national sources as separate counts.
   - VALUE SCORE: For each horse, calculate a Value Score = (consensus_count / total_sources) × morning_line_odds. Display this in a "Value" column. A 3/6 pick at 8/1 (Value: 4.0) is a better bet than a 4/6 pick at 6/5 (Value: 0.8). Flag any horse with Value Score >= 2.0 as a "VALUE PLAY" with a star.
   - Color code by confidence: GREEN = 4+ sources, YELLOW = 3 sources, ORANGE = 2 sources, RED = 1 source
   - Mark scratches clearly with gray strikethrough and (SCR) label
   - CRITICAL: NEVER recommend a bet on a scratched horse. If a source picked a scratched horse, mark that source's pick as VOID and do NOT count it toward consensus. Remove scratched horses entirely from the BEST BETTING STRATEGY box, consensus picks, and any exotic bet tickets. Recalculate consensus scores after removing scratched horses.
   - Highlight any stakes races with deeper analysis
   - Include a BEST BETTING STRATEGY box below each race's entry table with:
     * Primary bet recommendation (e.g., "$10 WIN on #4") — ONLY on horses confirmed in entries
     * SAVER BET RULE: When the #1 pick is a heavy favorite (morning line 2/1 or shorter), ALWAYS include a $2-3 saver Win bet on the #2 consensus pick. This protects against chalk upsets and caught 2 extra winners in our March 14 backtest.
     * Backup/exotic plays (e.g., "Key #4 over #2,#6 in Exacta") — ONLY with active horses
     * What to say at the betting window (exact phrasing)

2. TABLE KEY / LEGEND
   - Right after the color code section, include a full key/legend explaining:
     * Every column abbreviation (Rank, PP, Horse, Jockey, Trainer, ML, Sources, Confidence, etc.)
     * What the color-coded rows mean (green = strong consensus, yellow = moderate, red = longshot/minimal backing)
     * How the consensus scoring works (number of sources backing the horse out of total sources checked)
     * Any symbols or abbreviations used throughout the card
   - This should be on its own section so the reader can reference it quickly

3. COMPLETE BETTING GUIDE
   - All bet types explained: Win, Place, Show, Across the Board, Exacta, Trifecta, Superfecta, Daily Double, Pick 3/4/5/6
   - Boxing vs Straight vs Keying vs Wheeling with cost formulas
   - Exact phrases to say at betting windows
   - Payout chart for common odds levels

4. PLACE/SHOW TRACKING
   - For every race, include a PLACE/SHOW RECOMMENDATION alongside the Win bet
   - When the #1 pick has odds of 3/1 or shorter, add a $2 Place bet recommendation
   - When the #1 pick has odds of 5/1 or longer, add a $2 Show bet recommendation as insurance
   - Track ITM% (In The Money = 1st, 2nd, or 3rd) as a metric alongside win rate
   - ITM% is a better measure of source quality than pure win rate — our March 14 backtest showed picks finishing 2nd/3rd frequently

5. WEATHER & TRACK CONDITION MODIFIER
   - BEFORE generating picks, search for current weather and track conditions at the venue
   - web_search: [TRACK NAME] track condition today [DATE]
   - web_search: [TRACK NAME] weather forecast today
   - If track is listed as SLOPPY, MUDDY, or HEAVY:
     * Display a prominent WARNING banner at the top of the PDF: "OFF TRACK — REDUCE ALL BETS BY 50%"
     * Cut ALL recommended bet amounts in half across every budget tier
     * Our 9-day backtest showed 0% win rate on sloppy tracks (March 7) — this is the #1 risk factor
   - If track is GOOD or FAST, proceed with normal bet sizing
   - Always display current track condition prominently at the top of the cheat card

6. CONFIDENCE-TIERED BETTING
   - Do NOT bet the same amount on every race. Scale bet size by consensus strength:
     * GREEN picks (4+ sources): Full recommended bet (e.g., $10 Win)
     * YELLOW picks (3 sources): 75% of full bet (e.g., $7-8 Win)
     * ORANGE picks (2 sources): 50% of full bet (e.g., $5 Win) — exotics only preferred
     * RED picks (1 source): Skip Win bet entirely, use only in exotic tickets as a longshot
   - This tiered approach concentrates money on highest-confidence picks where our edge is strongest
   - Display the tier and recommended bet amount clearly in each race's BEST BETTING STRATEGY box

7. DAY-OF-WEEK & MOMENTUM ADJUSTMENTS
   - Check what day of the week it is. Our 9-day backtest (92 races) showed clear patterns:
     * FRIDAY: Best day (35% win rate, positive ROI) — use full bet sizing
     * SATURDAY: Good, especially after a hot Friday — use full bet sizing
     * SUNDAY: Average — use full bet sizing
     * THURSDAY: Worst day (27.8% win rate) — REDUCE all bets by 30%
   - Display the day-of-week modifier at the top of the PDF near track condition
   - MOMENTUM: If the user mentions yesterday was a good/hot day, note "HOT STREAK — momentum suggests confidence" in the header

8. BUDGET STRATEGIES
   - $50 budget plan (conservative)
   - $100 budget plan (moderate)
   - $150+ budget plan (aggressive)
   - Allocate specific dollar amounts to specific races
   - IMPORTANT: All budget amounts should already reflect the track condition modifier (50% cut on off-tracks) and day-of-week modifier (30% cut on Thursdays) and confidence-tier scaling

9. TRACK INFO & TIPS
   - Track bias data (inside/outside, speed/closer bias)
   - Weather and track conditions
   - Pro tips for the venue (parking, food, best viewing spots)
   - Any trainer/jockey angles (hot barns, rider changes)

PDF FORMATTING:
- Use Python reportlab library
- Proper margins (72pt all sides)
- Font sizes: Title 18pt, Headers 14pt, Body 10pt
- No text overlap, proper line spacing
- Clean professional layout with color coding

Save the PDF to /tmp/race_day_cheatcard.pdf

Email the PDF to: [EMAIL1], [EMAIL2]
Use SMTP with the Google App Password from /home/austin/linux-mini-agent/.env (GOOGLE_APP_PASSWORD).
Send from vacypert@gmail.com.
Subject: [TRACK NAME] Race Day Cheat Card - [DATE]

Also attach /tmp/race_day_cheatcard.pdf to this job's attachments for Telegram delivery.

Add any other information you think would be helpful for someone attending the races.
