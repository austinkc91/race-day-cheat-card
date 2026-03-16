# Race Day Cheat Card

AI-powered horse racing handicapping system that generates professional PDF cheat cards with multi-source consensus picks, live updates during race day, and automatic email/Telegram delivery.

## What It Does

When you're heading to the track, this system:

1. **Researches** every race — entries, scratches, odds, expert picks from 6 specific independent sources
2. **Builds a consensus algorithm** — scores each horse by how many of the 6 sources back them (e.g., 4/6 = BEST BET)
3. **Generates a professional PDF** — color-coded picks, betting guide, budget strategies, payout charts
4. **Auto-updates every 10 minutes** during race day — incorporates results, odds changes, new scratches
5. **Delivers via email and Telegram** — you get fresh PDFs all day without checking anything

### Results — 27-Day Backtest (229 races, Feb 6 - Mar 15, 2026)

- **Expert consensus picks alone:** -24.4% ROI (not profitable)
- **Optimized straight bet strategy:** **+86% ROI**, 70% profitable days
- **Exotic bet strategy (Monte Carlo):** **+174% ROI**, 95% of simulations profitable
- **Combined system:** ~$869-$4,347/month profit depending on bet sizing
- **79% of all winners paid $5+** — the market consistently overpays favorites
- **Top payouts in data:** $143, $100, $91, $78, $60, $54, $51

**See [STRATEGY.md](STRATEGY.md) for the complete betting strategy with rules, budget, and scaling guide.**

## Requirements

This system runs on [linux-mini-agent](https://github.com/austinkc91/linux-mini-agent) — a Linux desktop automation platform that gives AI agents full control of GUI + terminal.

You need:
- Linux machine with linux-mini-agent installed and running
- `ANTHROPIC_API_KEY` in your `.env`
- `GOOGLE_APP_PASSWORD` in your `.env` (for email delivery)
- `TELEGRAM_BOT_TOKEN` in your `.env` (for Telegram delivery)

## Quick Start — On-Demand via Telegram

This system runs **only when you ask for it**. Just message your Telegram bot naturally:

> "Going to Oaklawn today, start the horse race cheat sheets"
> "Heading to Churchill Downs Saturday, fire up the cheat card"
> "Give me a cheat card for Saratoga today"

The agent will:
1. Read the prompts from this repo, fill in the track name and date
2. Research all races, entries, scratches, odds, expert picks from 6 sources
3. Check weather/track conditions and apply bet modifiers
4. Generate a professional PDF cheat card with confidence-tiered betting
5. Email it and send it via Telegram
6. Set up a live-update cron (every 10 minutes) that auto-stops after the last race

When you're done, just say:
> "Stop the horse race cheat sheets"

### Manual Usage (alternative)

You can also run it directly:

```bash
cd /path/to/linux-mini-agent
just send "$(cat /path/to/race-day-cheat-card/prompts/initial-research.md)"
```

## Project Structure

```
race-day-cheat-card/
├── README.md                    # This file
├── STRATEGY.md                  # Complete betting strategy (straight + exotics)
├── algo/                        # Backtesting code, optimizer, Monte Carlo sims
├── prompts/
│   ├── initial-research.md      # First cheat card generation prompt
│   └── live-update.md           # Auto-improvement loop prompt
├── crons/
│   └── live-update-cron.json    # Cron job definition for live updates
├── examples/
│   ├── oaklawn-2026-03-14.md    # March 14 results (75% win rate)
│   ├── oaklawn-2026-03-14-final.pdf
│   ├── oaklawn-2026-03-15.md    # March 15 card (6-source edition)
│   ├── oaklawn-2026-03-15.pdf
│   ├── backtest-5day-report.md  # 5-day backtest (47 races)
│   └── backtest-9day-report.md  # 9-day backtest (92 races, definitive)
└── config.example.env           # Environment variables needed
```

## How the Consensus Algorithm Works

The system pulls picks from 6 specific independent handicapping sources:

1. **SFTB (Sports From The Basement)** — algorithmic speed ratings, workouts, past performances
2. **Racing Dudes** — expert handicapping (78% ITM rate)
3. **FanDuel Research** — data-driven win probabilities
4. **Ultimate Capper (Reggie Garrett)** — free expert picks
5. **Today's Racing Digest** — bias-aware analysis (since 1970)
6. **AllChalk AI** — machine learning predictions

Each horse is scored by consensus count (out of 6):
- **4+ sources** = BEST BET (green) — highest confidence
- **3 sources** = STRONG PLAY (yellow) — good value
- **2 sources** = MODERATE (orange) — consider in exotics
- **1 source** = LONGSHOT (red) — only at big odds

### Value Score
Each horse also gets a **Value Score** = (consensus_count / total_sources) × odds. This prevents the system from only picking obvious favorites. A 3/6 pick at 8/1 (Value: 4.0) is a better bet than a 4/6 pick at 6/5 (Value: 0.8). Horses with Value Score >= 2.0 are flagged as VALUE PLAYs.

### Local Expert Rule
If multiple sources are local experts from the same track (e.g., Nancy Holthus + Matt Dinerman at Oaklawn), they count as ONE combined "Local Expert" source. This prevents artificially inflated consensus from experts who tend to agree.

### Saver Bet Rule
When the #1 pick is a heavy favorite (2/1 or shorter), a $2-3 saver Win bet on the #2 consensus pick is always included. In our March 14 backtest, #2 picks won 2 races (R5 Miracle Worker at $10.60, R8 Goodall at $12.00) when the favorite lost.

### Place/Show Tracking
The system tracks ITM% (In The Money = 1st, 2nd, or 3rd) alongside win rate. Place/Show recommendations are included for each race. ITM% is a better measure of source quality — our March 14 backtest showed top picks finishing 2nd or 3rd frequently even when they didn't win.

**Scratch Handling:** If a source picked a scratched horse, that pick is VOID and does not count toward consensus. Scratched horses are removed from ALL betting recommendations, exotic tickets, and Pick 6 tickets. Consensus scores are recalculated after removing scratches.

### Weather & Track Condition Modifier
The system checks current track conditions before generating picks. On SLOPPY/MUDDY/HEAVY tracks, ALL bet amounts are cut by 50%. Our 9-day backtest showed a **0% win rate on sloppy tracks** (March 7) — track condition is the single biggest risk factor, more important than which horse you pick.

### Confidence-Tiered Betting
Not all picks are equal. Bet sizing scales with consensus strength:
- **GREEN (4+ sources):** Full bet
- **YELLOW (3 sources):** 75% of full bet
- **ORANGE (2 sources):** 50% of full bet, exotics preferred
- **RED (1 source):** Skip Win bet, use in exotics only

### Day-of-Week Adjustments
Our 92-race backtest revealed clear day-of-week patterns:
- **Friday:** Best day (35% win rate, positive ROI) — full bet sizing
- **Saturday:** Good, especially after a hot Friday — full bet sizing
- **Thursday:** Worst day (27.8% win rate) — all bets reduced 30%

## PDF Contents

Each generated cheat card includes:

- **Race-by-race picks** with consensus scores and color coding
- **Results tracking** for completed races (win rate, ROI)
- **All bet types explained** — Win, Place, Show, Exacta, Trifecta, Superfecta, Daily Double, Pick 3/4/5/6
- **Boxing vs Keying vs Wheeling** with cost formulas
- **Exact phrases to say at betting windows** (for first-timers)
- **Payout chart** for all odds levels
- **Budget strategies** — $50, $100, $150+ plans
- **Track bias data** and pro tips
- **Scratches** tracked in real-time
- **Version number and timestamp** so you know it's fresh

## Customizing for Different Tracks

Edit the prompts to change:
- **Track name and location** (e.g., "Churchill Downs, Louisville KY")
- **Race date**
- **Featured stakes races** (e.g., "Kentucky Derby", "Preakness")
- **Email recipients**
- **Local expert sources** (each track has its own beat writers)
- **Auto-stop time** (adjust based on last race post time)

## Tips

- Just message your bot: "Going to [track] today, start the cheat sheets" — it handles everything
- Start **2-3 hours before first post** for best results
- The system gets better as the day goes on — more data, more results to calibrate
- High consensus picks (4+ sources) have the strongest edge
- Value plays at 10/1+ with 3+ source backing are worth saver bets
- **Skip sloppy/muddy days** or halve all bets — track condition is risk #1
- **Fridays are the best day** for our system. Thursdays are the worst.
- The system auto-stops after races end
