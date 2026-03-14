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
   - Pull picks from at least 5 independent sources (Racing Dudes, SFTB algorithm, FanDuel Research, Today's Racing Digest, Ultimate Capper, and any local beat writers for this track)
   - Score each horse by consensus: how many sources pick them
   - Color code by confidence (green = 5+ sources, yellow = 3-4, red = 1-2)
   - Mark scratches clearly
   - Highlight any stakes races with deeper analysis
   - Include a BEST BETTING STRATEGY box below each race's entry table with:
     * Primary bet recommendation (e.g., "$10 WIN on #4")
     * Backup/exotic plays (e.g., "Key #4 over #2,#6 in Exacta")
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

4. BUDGET STRATEGIES
   - $50 budget plan (conservative)
   - $100 budget plan (moderate)
   - $150+ budget plan (aggressive)
   - Allocate specific dollar amounts to specific races

5. TRACK INFO & TIPS
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
