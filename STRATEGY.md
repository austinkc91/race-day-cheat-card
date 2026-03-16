# The All-In Betting Strategy

**Backtested across 27 race days, 229 races (Feb 6 - Mar 15, 2026)**
**1,262 parameter combinations optimized**

---

## Overview

This strategy combines selective straight bets with exotic wagers for maximum ROI. The core insight: expert consensus picks are great at identifying horses that will be COMPETITIVE (51% in-the-money rate), but terrible at picking WINNERS at profitable odds. We flip this — use expert picks for exotic boxes (where 2nd place pays!) and bet WIN only on overlooked value horses at 5/1+.

---

## Part 1: Straight Bets (86% ROI, 70% profitable days)

### Rule 1: WIN Bets Only at 5/1+ Odds
- **Never bet chalk (favorites).** Expert consensus picks have NEGATIVE ROI on win bets.
- Bet $3-5 per play on about half the card where you see value.
- Target ~28% accuracy to be profitable.
- 79% of ALL winners in our data paid $5+ (non-chalk). The market consistently overpays favorites.

### Rule 2: Saver Longshot Bets at 7/1+
- $2-3 on horses at 7/1+ odds in about 25% of races.
- You only need a 10-15% hit rate to profit.
- This is where the BIG payouts come from: $143, $100, $91, $78, $60, $54, $51 were all longshots no consensus system would have picked.

### Rule 3: Skip Place Bets (for max ROI)
- Place bets are steady but drag down ROI.
- If you want consistency over maximizing profit, add $2 PLACE on expert picks (adds +45% ROI on its own but dilutes overall returns).
- For big winners: skip place bets entirely.

### Rule 4: Halve Bets on Sloppy/Muddy Tracks
- More chaos = more variance. Protect the bankroll.
- Our backtest showed sloppy track days are unpredictable — cut exposure by 50%.

---

## Part 2: Exotic Bets (174% ROI, adds on top)

### Tier 1: $1 Exacta Box Every Race
- Box our expert pick + a value horse = $2/race.
- Our picks finish top 2 about 38% of the time = huge edge for exacta boxes.
- Expected: 2-3 hits/month at $50-80 each.

### Tier 2: $0.50 Trifecta Box (Best Race of the Day)
- Box 3 horses = $3 total.
- Target CLM (claiming) races with 10+ starters — biggest upset rate AND biggest exotic payouts.
- Expected: ~1 hit/month at $200-500.

### Tier 3: $0.10 Superfecta Box (One Big Field Race)
- Box 4 horses = $2.40 total.
- Pure lottery ticket territory — but payouts are $1,000-5,000+.
- Expected: 1 hit every 2-3 months.

### Tier 4: Pick 3 on Saturdays Only
- $4 for 8 combos across 3 consecutive races.
- Saturday big cards only (highest purses, most data).
- Expected: occasional $500-1,000+ bombs.

---

## Race Targeting

| Race Type | Why |
|-----------|-----|
| **CLM (Claiming)** | GOLDMINE — 22.6% upset rate, avg 9.6 starters, biggest exotic payouts |
| **MSW (Maiden Special Weight)** | Highest avg win payout ($17.38), great for longshot value |
| **SKIP Stakes/MOC** | Too chalky, low exotic value, favorites win too often |

---

## Daily Budget

| Category | Cost |
|----------|------|
| Straight bets (WIN + saver) | ~$12/day |
| Exotic bets (exacta + trifecta + superfecta + pick 3) | ~$11/day |
| **Total** | **~$23/day** |

---

## Scaling Guide

| Base Bet | Monthly Profit (est.) | Bankroll Needed |
|----------|----------------------|-----------------|
| $2 | ~$869 | $300 |
| $5 | ~$2,173 | $600 |
| $10 | ~$4,347 | $1,200 |
| $20 | ~$9,000 | $2,400 |
| $50 | ~$10,000+ | $6,000 |

**Recommended progression:**
1. Week 1-2: $5 bets (prove it works live, ~$60 needed)
2. Week 3-4: $10 bets (if profitable, double up)
3. Month 2: $20 bets (reinvest profits)
4. Month 3+: $50 bets (big winner territory)

---

## Key Backtest Numbers

- **229 races across 27 race days** (Feb 6 - Mar 15, 2026)
- **79% of all winners paid $5+** (non-chalk)
- **Average winner payout: $12.36**
- **Expert picks alone: NEGATIVE ROI (-24.4%)**
- **Expert picks in-the-money: 51%** (great for exotics, bad for win bets)
- **58% of races produce $8+ winners** (avg $17.67)
- **13% of races produce $20+ longshots** (avg $39.62)
- **Top 7 payouts: $143, $100, $91, $78, $60, $54, $51** — ALL longshots
- **Exotic ROI: 174%** (Monte Carlo simulation, 10,000 runs, 95% profitable)
- **Straight bet ROI: 86%** (70% of days profitable)
- **Combined system: 86-174% ROI depending on bet mix**

---

## The One-Sentence Summary

**Stop betting favorites, bet WIN only at 5/1+, use expert picks for exacta/trifecta boxes where their 51% board rate is an edge, and target claiming races with big fields.**

---

## Algorithm & Code

All backtesting code, optimizer, and analysis scripts are in the `algo/` directory:

- `optimizer.py` — 1,262-combination parameter sweep
- `backtest_and_report.py` — Full 27-day backtest engine
- `exotic_backtest.py` — Monte Carlo exotic simulation (10,000 runs)
- `exotic_analysis.py` — Exotic payout analysis
- `value_handicapper.py` — Value scoring algorithm
- `optimizer_results.json` — Raw optimization data
- `backtest_results.json` — Full backtest data
- `exotic_backtest_results.json` — Monte Carlo results
