# Race Day Cheat Card

AI-powered horse racing handicapping system that generates professional PDF cheat cards with multi-source consensus picks, live updates during race day, and automatic email/Telegram delivery.

## What It Does

When you're heading to the track, this system:

1. **Researches** every race — entries, scratches, odds, expert picks from 5-8 independent sources
2. **Builds a consensus algorithm** — scores each horse by how many sources back them (e.g., 6/8 = strong pick)
3. **Generates a professional PDF** — color-coded picks, betting guide, budget strategies, payout charts
4. **Auto-updates every 10 minutes** during race day — incorporates results, odds changes, new scratches
5. **Delivers via email and Telegram** — you get fresh PDFs all day without checking anything

### Results from Oaklawn Park (March 14, 2026)

- **75% win rate** (3-for-4 on the day)
- **High consensus picks: 2-for-2 (100%)**
- 22 versions generated throughout the day with live updates
- Winners: C McGriff (R1), Hicko (R3 Best Bet), Raymond (R4)

## Requirements

This system runs on [linux-mini-agent](https://github.com/austinkc91/linux-mini-agent) — a Linux desktop automation platform that gives AI agents full control of GUI + terminal.

You need:
- Linux machine with linux-mini-agent installed and running
- `ANTHROPIC_API_KEY` in your `.env`
- `GOOGLE_APP_PASSWORD` in your `.env` (for email delivery)
- `TELEGRAM_BOT_TOKEN` in your `.env` (for Telegram delivery)

## Quick Start

### 1. Initial Cheat Card (run the morning of race day)

Send this as a job to your linux-mini-agent. Edit the track name, date, and email addresses:

```bash
cd /path/to/linux-mini-agent

just send "$(cat /path/to/race-day-cheat-card/prompts/initial-research.md)"
```

Or via Telegram, just send the prompt text as a message to your bot.

This will:
- Research all races, entries, scratches, odds, expert picks
- Generate a multi-page PDF cheat card
- Email it to your specified addresses
- Send it back via Telegram

### 2. Live Updates (start when races begin)

Create a cron job that auto-updates the cheat card every 10 minutes:

```bash
# Via the listen API:
curl -X POST http://localhost:7600/cron \
  -H "Content-Type: application/json" \
  -d @/path/to/race-day-cheat-card/crons/live-update-cron.json
```

Or via Telegram:
```
/cron add */10 * * * * | Race Day Live Updates | <paste prompt from prompts/live-update.md>
```

### 3. Stop Updates (when you leave)

```bash
# Via Telegram:
/cron del <cron-id>

# Or via API:
curl -X DELETE http://localhost:7600/cron/<cron-id>
```

## Project Structure

```
race-day-cheat-card/
├── README.md                    # This file
├── prompts/
│   ├── initial-research.md      # First cheat card generation prompt
│   └── live-update.md           # Auto-improvement loop prompt
├── crons/
│   └── live-update-cron.json    # Cron job definition for live updates
├── examples/
│   └── oaklawn-2026-03-14.md    # Example output from first use
└── config.example.env           # Environment variables needed
```

## How the Consensus Algorithm Works

The system pulls picks from multiple independent handicapping sources:

1. **Sports From The Basement (SFTB)** — algorithmic model
2. **Racing Dudes** — 78% ITM rate
3. **Ultimate Capper** — expert picks
4. **FanDuel Research** — data-driven analysis
5. **Today's Racing Digest** — traditional handicapping
6. **Rick Lee (Arkansas Democrat-Gazette)** — local expert (track-specific)
7. **Additional sources** as available for the specific track

Each horse is scored by consensus count:
- **6/8+ sources** = BEST BET (green) — highest confidence
- **4-5/8 sources** = STRONG PLAY (yellow) — good value
- **2-3/8 sources** = MODERATE (orange) — consider in exotics
- **1/8 source** = LONGSHOT (red) — only at big odds

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

- Start the initial research **2-3 hours before first post** for best results
- The system gets better as the day goes on — more data, more results to calibrate against
- High consensus picks (5+ sources agreeing) have been the most reliable
- Value plays at 10/1+ with 3+ source backing are worth small bets
- The system auto-stops after races end (configurable time)
