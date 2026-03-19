# Race Day Cheat Card -- VALUE BETTING Strategy

**UPDATED March 18, 2026 -- Validated with 8,500+ real races (Oct 2025 - Mar 2026)**
**Previous mechanical strategies (ML rank combos, jockey-only betting) all FAILED out-of-sample validation**
**This strategy is based on Bill Benter's proven methodology: find VALUE, not winners**

---

## THE CORE PRINCIPLE: VALUE BETTING

**You don't need to pick winners. You need to find horses the public is UNDERVALUING.**

A horse with a 25% chance of winning at 5/1 odds is a VALUE BET (expected value: $1.50 per $1 bet).
A horse with a 50% chance of winning at even money is a BAD BET (expected value: $0.83 after takeout).

The cheat card's 6-source expert consensus IS the model. When multiple independent experts agree on a horse but the betting public hasn't caught on, that's where the money is.

---

## THE STRATEGY: Expert Consensus vs Tote Board Odds

### How It Works

1. **Gather expert consensus** (already done by the cheat card's 6 sources)
2. **Check the live tote board odds** before each race
3. **Compare**: Do the experts see something the public doesn't?
4. **Only bet when there's a MISMATCH** (experts love a horse, public is sleeping on it)

### Expert Consensus Probability Estimates

| Sources Agreeing | Estimated Win Probability | Minimum Tote Odds for Value |
|-----------------|--------------------------|----------------------------|
| 6 of 6 | ~42% | Must be 2/1 or higher |
| 5 of 6 | ~32% | Must be 5/2 or higher |
| 4 of 6 | ~24% | Must be 3/1 or higher |
| 3 of 6 | ~17% | Must be 4/1 or higher |
| 2 or fewer | No bet | — |

### The Decision Rule

**BET when**: Expert probability > Tote implied probability x 1.15 (15% minimum edge)

Example:
- 5 of 6 experts pick Horse A → estimated 32% win probability
- Tote board shows Horse A at 4/1 → implied probability = 20%
- Edge = (32% - 20%) / 20% = 60% → **STRONG VALUE BET**

Another example:
- 4 of 6 experts pick Horse B → estimated 24% win probability
- Tote board shows Horse B at 2/1 → implied probability = 33%
- Edge = (24% - 33%) / 33% = -27% → **NO BET** (public already agrees)

---

## BETTING RULES

### What to Bet
- **WIN bets ONLY** — $2 to $5 per bet
  - Win bets have 15-17% takeout (vs 20-25% for exotics)
  - Easier to find value on win bets
  - No need to get exacta order right
- **$2 on 15-25% edge** (marginal value)
- **$5 on 30%+ edge** (strong value)

### Race Type Filter
- **BET**: CLM, MC, SOC — these have the most predictable form
- **CAUTION**: ALW, AOC — bet only with 5+ source consensus
- **SKIP**: MSW (too unpredictable), STK (too much public action, no value)

### Daily Limits
- **Maximum 3 bets per day** — being selective IS the edge
- **Skip days with 0 value bets** — not betting is a valid decision
- **Daily budget: $6-15** (3 bets x $2-5 each)

### When to Check Odds
- Check tote board odds **5-10 minutes before post time**
- Earlier odds are less reliable (not enough money in the pools)
- If the horse's odds drop below the value threshold before post, **don't bet**

---

## HOW TO USE THE CHEAT CARD

### For Each Race:

1. **Look at the consensus tier**:
   - GREEN (4+ sources) → Potential value bet candidate
   - YELLOW (3 sources) → Only bet if odds are generous (4/1+)
   - ORANGE/RED → No bet

2. **Check the Value Score**:
   - Value Score = (consensus_count / total_sources) x morning_line_odds
   - Score >= 2.0 = FLAG as potential value play
   - Score >= 3.0 = STRONG value candidate

3. **Before post time, check live tote board odds**:
   - If tote odds are LONGER than the Value Score suggests → BET
   - If tote odds are SHORTER (public caught on) → SKIP
   - If the horse is the clear favorite at low odds → SKIP (no value)

4. **Place your bet**:
   - "$[amount] to WIN on number [program number] in race [X]"
   - That's it. One bet, one horse, one race.

### What NOT to Do
- Do NOT bet every race
- Do NOT box exactas/trifectas (house edge is too high)
- Do NOT chase losses
- Do NOT bet on a horse just because it's the favorite
- Do NOT bet when you don't see clear value
- Do NOT increase bet size after a loss

---

## BANKROLL MANAGEMENT

| Item | Amount |
|------|--------|
| Daily budget | $6-15 |
| Weekly expected bets | 10-15 |
| Weekly expected cost | $20-75 |
| 20-day bankroll | $150-300 |

### The Math
- At 15-25% edge on value bets, expected return per $1 bet = $1.15-$1.25
- Over 100 value bets at $3 average = $300 wagered, ~$345-375 returned
- Expected profit: $45-75 per 100 bets (~15-25% ROI)
- This assumes DISCIPLINE — only betting true value spots

---

## WHY THIS WORKS (AND WHY MECHANICAL STRATEGIES DON'T)

### What We Proved (8,500+ races backtested):
1. **ML rank combos fail**: Every combination of morning line rankings (#1-#2, #2-#3, #4-#1, etc.) loses money out-of-sample. The ML is stale info the public already knows.
2. **Jockey-only betting fails**: Blindly betting "profitable" jockeys from training data produces -90% ROI on test data. Past jockey performance doesn't predict future wins.
3. **All mechanical strategies overfit**: Any fixed rule that looks great on old data fails on new data. The market adapts.

### What DOES Work:
1. **Multiple independent expert opinions** provide a better probability estimate than any single factor
2. **Comparing expert estimates vs live tote odds** identifies market inefficiencies
3. **Being selective** (3 bets/day max) avoids the house edge grinding you down
4. **Win bets only** minimize takeout (15% vs 20-25% for exotics)
5. **Discipline** — the edge is real but small, so you need volume AND selectivity

---

## EXPERT SOURCES (6-source consensus system)

1. **SFTB** (Sports From The Basement) — algorithmic speed ratings
2. **Racing Dudes** — expert handicapping
3. **FanDuel Research** — data-driven probabilities
4. **Ultimate Capper** (Reggie Garrett) — free expert picks
5. **Today's Racing Digest** — bias-aware analysis
6. **AllChalk AI** — machine learning predictions

**LOCAL EXPERT RULE**: If 2+ sources are local track experts, count as ONE combined source.

---

## WHAT THE CHEAT CARD SHOULD SHOW

For EVERY race:
1. Expert consensus tier (GREEN/YELLOW/ORANGE/RED)
2. Number of sources picking each horse (e.g., "5/6 sources")
3. Morning line odds
4. **Value Score** = (sources / 6) x ML odds
5. Horses with Value Score >= 2.0 flagged as "VALUE PLAY"
6. Race type clearly marked (CLM/MC/SOC = eligible, MSW/STK = skip)

For VALUE PLAY horses:
- Clear "CHECK LIVE ODDS BEFORE BETTING" warning
- The minimum tote odds needed for the bet to have value
- Exact window phrase: "$[X] to WIN on number [program] in race [Y]"

For non-value races:
- Mark as "NO BET — no value identified"
- Still show research data for information

---

## BACKTESTING & VALIDATION

All code in `algo/`:
- `value_model_v2.py` — Full model with 8,500+ races, time-series validation
- `value_scanner.py` — Live value detection module
- `value_model.py` — Initial model with ML odds calibration
- `jockey_database.json` — Jockey statistics (informational, not for betting)
- `otb_race_data.json` — 3,166 races with actual payouts (Feb-Mar 2026)
