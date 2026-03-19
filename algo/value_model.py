#!/usr/bin/env python3
"""
VALUE BETTING MODEL for Horse Racing

Based on Bill Benter's approach:
1. Estimate true win probability for each horse using multiple factors
2. Compare model probability vs actual tote board odds
3. Only bet when model says horse is undervalued (overlay)
4. Backtest on out-of-sample data

Features used:
- Morning line odds (implied probability)
- Jockey win rate (computed from 3,166 historical races)
- Jockey ROI (does this jockey beat their odds?)
- Field size
- Race type (CLM, MC, SOC, MSW, ALW, STK)
- Post position
- Jockey-track combo win rate
- Favorite status
"""

import json
import math
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data():
    """Load all available race data."""
    # Load OTB data (3,166 races with actual payouts and jockey info)
    with open(os.path.join(SCRIPT_DIR, "otb_race_data.json")) as f:
        otb = json.load(f)

    # Load ML data (races with morning line odds)
    ml_data = {}
    for batch_file in ["ml_batch_1.json", "ml_batch_2.json", "ml_batch_3.json"]:
        path = os.path.join(SCRIPT_DIR, batch_file)
        if os.path.exists(path):
            with open(path) as f:
                batch = json.load(f)
                if "track_days" in batch:
                    ml_data.update(batch["track_days"])
                else:
                    ml_data.update(batch)

    return otb, ml_data


def extract_track_name(key):
    """Extract track name from race day key like '2026-03-14 Tampa Bay Downs'."""
    parts = key.split(" ", 1)
    return parts[1] if len(parts) > 1 else key


def extract_date(key):
    """Extract date from race day key."""
    parts = key.split(" ", 1)
    try:
        return datetime.strptime(parts[0], "%Y-%m-%d")
    except ValueError:
        return None


def ml_odds_to_prob(ml_odds):
    """Convert morning line odds to implied probability."""
    if ml_odds <= 0:
        return 0.5
    return 1.0 / (1.0 + ml_odds)


def win_payout_to_odds(payout):
    """Convert $2 win payout to decimal odds. e.g., $6.00 payout = 2/1 odds."""
    if payout <= 2.0:
        return 0.1  # Even money or less
    return (payout - 2.0) / 2.0


def compute_jockey_stats(otb_data):
    """Compute jockey statistics from 3,166 OTB races."""
    jockey_starts = defaultdict(int)
    jockey_wins = defaultdict(int)
    jockey_roi = defaultdict(float)  # Total return on $2 bets
    jockey_track_starts = defaultdict(int)
    jockey_track_wins = defaultdict(int)

    for key, races in otb_data["race_days"].items():
        track = extract_track_name(key)
        for race in races:
            finish = race.get("finish_order", [])
            wps = race.get("wps", {})
            win_payout = wps.get("win", 0)

            for horse in finish:
                jockey = horse.get("jockey", "Unknown")
                pos = horse.get("position", 99)
                jockey_starts[jockey] += 1
                jockey_track_starts[(jockey, track)] += 1

                if pos == 1:
                    jockey_wins[jockey] += 1
                    jockey_track_wins[(jockey, track)] += 1
                    jockey_roi[jockey] += win_payout - 2.0  # Profit on $2 bet
                else:
                    jockey_roi[jockey] -= 2.0  # Loss on $2 bet

    # Compute rates
    stats = {}
    for jockey in jockey_starts:
        starts = jockey_starts[jockey]
        wins = jockey_wins[jockey]
        roi = jockey_roi[jockey]
        stats[jockey] = {
            "starts": starts,
            "wins": wins,
            "win_rate": wins / starts if starts > 0 else 0,
            "roi": roi / (starts * 2) if starts > 0 else 0,  # ROI per $2 bet
        }

    # Track-specific stats
    track_stats = {}
    for (jockey, track), starts in jockey_track_starts.items():
        wins = jockey_track_wins.get((jockey, track), 0)
        track_stats[(jockey, track)] = {
            "starts": starts,
            "wins": wins,
            "win_rate": wins / starts if starts > 0 else 0,
        }

    return stats, track_stats


def compute_post_position_stats(otb_data):
    """Compute win rates by post position."""
    pp_starts = defaultdict(int)
    pp_wins = defaultdict(int)

    for key, races in otb_data["race_days"].items():
        for race in races:
            for horse in race.get("finish_order", []):
                try:
                    pp = int(horse.get("program", "0"))
                except (ValueError, TypeError):
                    continue
                if pp < 1 or pp > 20:
                    continue
                pp_starts[pp] += 1
                if horse.get("position", 99) == 1:
                    pp_wins[pp] += 1

    stats = {}
    for pp in pp_starts:
        stats[pp] = {
            "starts": pp_starts[pp],
            "wins": pp_wins[pp],
            "win_rate": pp_wins[pp] / pp_starts[pp] if pp_starts[pp] > 0 else 0,
        }
    return stats


def compute_race_type_stats(otb_data):
    """Compute favorite win rates by race type (useful for calibrating confidence)."""
    # For each race type: how often does the tote favorite win?
    type_fav_wins = defaultdict(int)
    type_races = defaultdict(int)

    for key, races in otb_data["race_days"].items():
        for race in races:
            rtype = race.get("race_type", "UNK")
            wps = race.get("wps", {})
            win_payout = wps.get("win", 0)
            type_races[rtype] += 1
            # Low win payout = favorite won
            if 0 < win_payout <= 6.0:
                type_fav_wins[rtype] += 1

    stats = {}
    for rtype in type_races:
        stats[rtype] = {
            "races": type_races[rtype],
            "fav_wins": type_fav_wins[rtype],
            "fav_win_rate": type_fav_wins[rtype] / type_races[rtype] if type_races[rtype] > 0 else 0,
        }
    return stats


def build_value_dataset(otb_data, ml_data, jockey_stats, jockey_track_stats, pp_stats):
    """
    Build dataset for value model.
    Each row = one horse in one race.
    Features: ML odds, jockey stats, field size, race type, post position, etc.
    Target: did this horse win? (0 or 1)

    We can only build this for races where we have ML odds (from ml_data)
    AND actual payouts (from otb_data, matched by track+date+race_num+horse_name).
    """
    dataset = []

    # Index OTB races for lookup
    otb_index = {}
    for key, races in otb_data["race_days"].items():
        for race in races:
            race_key = f"{key}_R{race['race_num']}"
            otb_index[race_key] = race

    # Process ML data races
    for td_key, td_data in ml_data.items():
        track = extract_track_name(td_key)
        date_str = td_key.split(" ", 1)[0]
        races = td_data.get("races", [])

        for race in races:
            race_num = race.get("race_num", 0)
            race_type = race.get("race_type", "UNK")
            horses = race.get("horses", {})
            finish = race.get("finish", [])

            if not horses or not finish:
                continue

            # Try to find matching OTB race for actual payouts
            otb_key = f"{td_key}_R{race_num}"
            otb_race = otb_index.get(otb_key)

            # Get actual win payout from OTB data
            actual_win_payout = None
            if otb_race:
                actual_win_payout = otb_race.get("wps", {}).get("win", 0)
                actual_exacta = otb_race.get("exotics", {}).get("exacta", 0)
            else:
                actual_exacta = 0

            field_size = len(horses)
            if field_size < 3:
                continue

            # Sort horses by ML odds to get rankings
            sorted_horses = sorted(horses.items(), key=lambda x: x[1])

            for rank, (horse_name, ml_odds) in enumerate(sorted_horses):
                # Did this horse win?
                won = 1 if finish and finish[0] == horse_name else 0
                placed_2nd = 1 if len(finish) > 1 and finish[1] == horse_name else 0

                # ML implied probability
                ml_prob = ml_odds_to_prob(ml_odds)

                # Jockey info - try to match from OTB
                jockey = "Unknown"
                program_num = rank + 1  # Approximate
                if otb_race:
                    for h in otb_race.get("finish_order", []):
                        if h.get("name", "").lower() == horse_name.lower():
                            jockey = h.get("jockey", "Unknown")
                            try:
                                program_num = int(h.get("program", rank + 1))
                            except (ValueError, TypeError):
                                program_num = rank + 1
                            break

                # Jockey features
                j_stats = jockey_stats.get(jockey, {"win_rate": 0.1, "roi": -0.1, "starts": 0})
                jt_stats = jockey_track_stats.get((jockey, track), {"win_rate": 0.1, "starts": 0})

                # Post position feature
                pp = pp_stats.get(program_num, {"win_rate": 1.0 / field_size})

                row = {
                    "track_day": td_key,
                    "race_num": race_num,
                    "race_type": race_type,
                    "horse": horse_name,
                    "ml_odds": ml_odds,
                    "ml_prob": ml_prob,
                    "ml_rank": rank + 1,
                    "field_size": field_size,
                    "jockey": jockey,
                    "jockey_win_rate": j_stats["win_rate"],
                    "jockey_roi": j_stats["roi"],
                    "jockey_starts": j_stats["starts"],
                    "jockey_track_win_rate": jt_stats["win_rate"],
                    "jockey_track_starts": jt_stats.get("starts", 0),
                    "post_position": program_num,
                    "pp_win_rate": pp.get("win_rate", 1.0 / field_size),
                    "is_favorite": 1 if rank == 0 else 0,
                    "is_second_choice": 1 if rank == 1 else 0,
                    "won": won,
                    "placed_2nd": placed_2nd,
                    "actual_win_payout": actual_win_payout,
                    "actual_exacta": actual_exacta,
                    "finish_pos": (
                        finish.index(horse_name) + 1 if horse_name in finish else field_size
                    ),
                }
                dataset.append(row)

    return dataset


def train_value_model(dataset):
    """
    Train a simple but effective value model.

    Instead of complex ML, we use a WEIGHTED PROBABILITY approach:
    - Start with ML implied probability
    - Adjust based on jockey quality (jockeys with high win rates vs their odds = value)
    - Adjust based on post position
    - Adjust based on field size

    The key insight: we're not trying to pick winners.
    We're trying to find horses whose TRUE probability > IMPLIED probability from odds.
    """

    # Split by track_day for proper time-series cross-validation
    track_days = sorted(set(row["track_day"] for row in dataset))
    n = len(track_days)

    # Use first 60% for training stats, last 40% for testing
    train_cutoff = int(n * 0.6)
    train_days = set(track_days[:train_cutoff])
    test_days = set(track_days[train_cutoff:])

    train_data = [r for r in dataset if r["track_day"] in train_days]
    test_data = [r for r in dataset if r["track_day"] in test_days]

    print(f"\n{'='*60}")
    print(f"DATASET SPLIT")
    print(f"{'='*60}")
    print(f"Total horses: {len(dataset)}")
    print(f"Train: {len(train_data)} horses across {len(train_days)} track-days")
    print(f"Test:  {len(test_data)} horses across {len(test_days)} track-days")

    # Step 1: Learn calibration factors from training data
    # How much does ML probability need to be adjusted?

    # Group by ML rank and see actual win rates
    rank_wins = defaultdict(int)
    rank_total = defaultdict(int)
    for r in train_data:
        rank = min(r["ml_rank"], 10)
        rank_wins[rank] += r["won"]
        rank_total[rank] += 1

    print(f"\n{'='*60}")
    print(f"TRAINING: ML RANK vs ACTUAL WIN RATE")
    print(f"{'='*60}")
    rank_actual_rate = {}
    for rank in sorted(rank_total.keys()):
        actual_rate = rank_wins[rank] / rank_total[rank] if rank_total[rank] > 0 else 0
        rank_actual_rate[rank] = actual_rate
        print(f"  ML#{rank}: {rank_wins[rank]}/{rank_total[rank]} = {actual_rate:.1%} actual win rate")

    # Group by ML probability bucket and see actual win rates
    prob_buckets = defaultdict(lambda: {"wins": 0, "total": 0})
    for r in train_data:
        bucket = round(r["ml_prob"] * 10) / 10  # Round to nearest 0.1
        prob_buckets[bucket]["wins"] += r["won"]
        prob_buckets[bucket]["total"] += 1

    print(f"\n{'='*60}")
    print(f"TRAINING: ML PROBABILITY CALIBRATION")
    print(f"{'='*60}")
    calibration = {}
    for bucket in sorted(prob_buckets.keys(), reverse=True):
        b = prob_buckets[bucket]
        if b["total"] >= 5:
            actual = b["wins"] / b["total"]
            ratio = actual / bucket if bucket > 0 else 1.0
            calibration[bucket] = ratio
            marker = " <-- OVERVALUED" if ratio < 0.8 else (" <-- UNDERVALUED" if ratio > 1.2 else "")
            print(f"  ML prob {bucket:.0%}: actual {actual:.1%} (ratio: {ratio:.2f}){marker}")

    # Jockey quality tiers
    jockey_tier = {}
    for r in train_data:
        j = r["jockey"]
        if r["jockey_starts"] >= 20:
            if r["jockey_win_rate"] >= 0.20:
                jockey_tier[j] = "elite"
            elif r["jockey_win_rate"] >= 0.15:
                jockey_tier[j] = "good"
            elif r["jockey_win_rate"] >= 0.10:
                jockey_tier[j] = "average"
            else:
                jockey_tier[j] = "below"

    # Step 2: Build the probability model
    def estimate_probability(row):
        """Estimate true win probability for a horse."""
        # Start with ML implied probability
        base_prob = row["ml_prob"]

        # Adjust 1: Calibration based on ML probability bucket
        bucket = round(base_prob * 10) / 10
        cal = calibration.get(bucket, 1.0)
        adjusted = base_prob * cal

        # Adjust 2: Jockey quality
        j = row["jockey"]
        tier = jockey_tier.get(j, "unknown")
        if tier == "elite" and row["jockey_starts"] >= 30:
            adjusted *= 1.15  # Elite jockeys win more than ML suggests
        elif tier == "good" and row["jockey_starts"] >= 30:
            adjusted *= 1.05
        elif tier == "below" and row["jockey_starts"] >= 30:
            adjusted *= 0.90

        # Adjust 3: Jockey ROI (does this jockey beat the odds?)
        if row["jockey_starts"] >= 50 and row["jockey_roi"] > 0:
            adjusted *= 1.10  # Jockey consistently beats odds = real edge

        # Adjust 4: Field size (smaller fields = favorites win more)
        if row["field_size"] <= 5 and row["is_favorite"]:
            adjusted *= 1.10
        elif row["field_size"] >= 9 and row["is_favorite"]:
            adjusted *= 0.95  # Big fields = more chaos

        # Normalize to ensure probabilities sum to ~1 within each race
        return max(0.01, min(0.90, adjusted))

    # Step 3: Backtest value betting on TEST data
    print(f"\n{'='*60}")
    print(f"BACKTESTING VALUE BETTING ON OUT-OF-SAMPLE DATA")
    print(f"({'|'.join(sorted(test_days)[:3])}... {len(test_days)} track-days)")
    print(f"{'='*60}")

    # Group test data by race
    test_races = defaultdict(list)
    for r in test_data:
        race_key = f"{r['track_day']}_R{r['race_num']}"
        test_races[race_key] = test_races.get(race_key, [])
        test_races[race_key].append(r)

    # Add model probability to each horse
    for race_key, horses in test_races.items():
        probs = []
        for h in horses:
            h["model_prob"] = estimate_probability(h)
            probs.append(h["model_prob"])

        # Normalize probabilities to sum to 1
        total_prob = sum(probs)
        if total_prob > 0:
            for h in horses:
                h["model_prob"] = h["model_prob"] / total_prob

    # VALUE BETTING STRATEGIES TO TEST
    strategies = [
        # (name, min_edge, bet_type, max_bets_per_race, bet_amount)
        ("Win: 20% edge, CLM/MC only", 0.20, "win", 1, 2.0, ["CLM", "MC", "SOC"]),
        ("Win: 30% edge, CLM/MC only", 0.30, "win", 1, 2.0, ["CLM", "MC", "SOC"]),
        ("Win: 40% edge, CLM/MC only", 0.40, "win", 1, 2.0, ["CLM", "MC", "SOC"]),
        ("Win: 20% edge, all types", 0.20, "win", 1, 2.0, None),
        ("Win: 30% edge, all types", 0.30, "win", 1, 2.0, None),
        ("Win: 50% edge, CLM/MC only", 0.50, "win", 1, 2.0, ["CLM", "MC", "SOC"]),
        ("Win: 20% edge, top 3 only", 0.20, "win_top3", 1, 2.0, ["CLM", "MC", "SOC"]),
        ("Win: 30% edge, top 3 only", 0.30, "win_top3", 1, 2.0, ["CLM", "MC", "SOC"]),
        ("Place: 20% edge, CLM/MC", 0.20, "place", 1, 2.0, ["CLM", "MC", "SOC"]),
        ("Place: 30% edge, CLM/MC", 0.30, "place", 1, 2.0, ["CLM", "MC", "SOC"]),
    ]

    results = {}
    for strat_name, min_edge, bet_type, max_bets, bet_amt, race_types in strategies:
        total_wagered = 0
        total_returned = 0
        bets_made = 0
        wins = 0
        daily_pnl = defaultdict(float)

        for race_key, horses in test_races.items():
            td = horses[0]["track_day"]
            rtype = horses[0]["race_type"]

            # Filter by race type if specified
            if race_types and rtype not in race_types:
                continue

            # Find value bets in this race
            value_bets = []
            for h in horses:
                model_prob = h["model_prob"]
                ml_implied = h["ml_prob"]

                # Calculate edge
                edge = (model_prob - ml_implied) / ml_implied if ml_implied > 0 else 0

                if bet_type == "win_top3" and h["ml_rank"] > 3:
                    continue

                if edge >= min_edge:
                    value_bets.append((edge, h))

            # Sort by edge (best value first) and take top N
            value_bets.sort(key=lambda x: -x[0])
            for edge, h in value_bets[:max_bets]:
                total_wagered += bet_amt
                bets_made += 1

                if bet_type in ("win", "win_top3"):
                    if h["won"]:
                        wins += 1
                        # Estimate return: use actual payout if available, else estimate from ML odds
                        if h["actual_win_payout"] and h["actual_win_payout"] > 0:
                            payout = h["actual_win_payout"]
                        else:
                            payout = (h["ml_odds"] + 1) * 2  # Approximate $2 payout
                        total_returned += payout
                        daily_pnl[td] += payout - bet_amt
                    else:
                        daily_pnl[td] -= bet_amt
                elif bet_type == "place":
                    # Place bet wins if horse finishes 1st or 2nd
                    if h["won"] or h["placed_2nd"]:
                        wins += 1
                        # Place payout is roughly 40-60% of win payout
                        if h["actual_win_payout"] and h["actual_win_payout"] > 0:
                            payout = max(2.40, h["actual_win_payout"] * 0.5)
                        else:
                            payout = max(2.40, (h["ml_odds"] * 0.5 + 1) * 2)
                        total_returned += payout
                        daily_pnl[td] += payout - bet_amt
                    else:
                        daily_pnl[td] -= bet_amt

        if bets_made == 0:
            continue

        net = total_returned - total_wagered
        roi = net / total_wagered * 100 if total_wagered > 0 else 0
        win_rate = wins / bets_made * 100 if bets_made > 0 else 0
        profitable_days = sum(1 for v in daily_pnl.values() if v > 0)
        total_days = len(daily_pnl)

        results[strat_name] = {
            "bets": bets_made,
            "wins": wins,
            "win_rate": win_rate,
            "wagered": total_wagered,
            "returned": total_returned,
            "net": net,
            "roi": roi,
            "profitable_days": profitable_days,
            "total_days": total_days,
            "daily_pnl": dict(daily_pnl),
        }

    # Print results
    print(f"\n{'='*80}")
    print(f"{'STRATEGY':<40} {'BETS':>5} {'WINS':>5} {'W%':>6} {'WAGER':>8} {'RET':>8} {'NET':>8} {'ROI':>7} {'DAYS':>8}")
    print(f"{'='*80}")

    best_strat = None
    best_roi = -999

    for name, r in sorted(results.items(), key=lambda x: -x[1]["roi"]):
        marker = ""
        if r["roi"] > 0:
            marker = " ***"
        print(f"{name:<40} {r['bets']:>5} {r['wins']:>5} {r['win_rate']:>5.1f}% ${r['wagered']:>6.0f} ${r['returned']:>6.0f} ${r['net']:>+7.0f} {r['roi']:>+6.1f}%  {r['profitable_days']}/{r['total_days']}{marker}")
        if r["roi"] > best_roi and r["bets"] >= 5:
            best_roi = r["roi"]
            best_strat = name

    if best_strat and best_roi > 0:
        print(f"\nBEST STRATEGY: {best_strat} ({best_roi:+.1f}% ROI)")
        r = results[best_strat]
        print(f"\nDAILY BREAKDOWN:")
        for day, pnl in sorted(r["daily_pnl"].items()):
            marker = "WIN" if pnl > 0 else "LOSS"
            print(f"  {day}: ${pnl:+.2f} ({marker})")

    return results, estimate_probability, test_data


def build_expanded_model(otb_data, jockey_stats, pp_stats):
    """
    Build a larger model using ALL 3,166 OTB races.
    Since OTB doesn't have pre-race odds for all horses,
    we use the TOTE ODDS OF THE WINNER to identify value patterns.

    Key insight: When a horse with a high-win-rate jockey wins at long odds,
    that represents a situation where we COULD have found value.
    """

    print(f"\n{'='*60}")
    print(f"EXPANDED ANALYSIS: 3,166 RACES - JOCKEY VALUE PATTERNS")
    print(f"{'='*60}")

    # For each jockey with enough starts, compute:
    # 1. Average odds when they win (from win payout)
    # 2. Whether betting them blindly is profitable
    # 3. Whether they're especially profitable in certain conditions

    jockey_wins_by_type = defaultdict(lambda: {"starts": 0, "wins": 0, "roi_total": 0})

    for key, races in otb_data["race_days"].items():
        track = extract_track_name(key)
        for race in races:
            rtype = race.get("race_type", "UNK")
            wps = race.get("wps", {})
            win_payout = wps.get("win", 0)
            field_size = len(race.get("finish_order", []))

            for horse in race.get("finish_order", []):
                jockey = horse.get("jockey", "Unknown")
                pos = horse.get("position", 99)
                k = (jockey, rtype)
                jockey_wins_by_type[k]["starts"] += 1

                if pos == 1:
                    jockey_wins_by_type[k]["wins"] += 1
                    jockey_wins_by_type[k]["roi_total"] += win_payout - 2.0
                else:
                    jockey_wins_by_type[k]["roi_total"] -= 2.0

    # Find profitable jockey-type combos
    print(f"\nPROFITABLE JOCKEY x RACE TYPE COMBOS (min 20 starts, positive ROI):")
    print(f"{'Jockey':<25} {'Type':>5} {'Starts':>7} {'Wins':>5} {'W%':>6} {'ROI':>8}")
    print(f"{'-'*60}")

    profitable_combos = []
    for (jockey, rtype), stats in sorted(
        jockey_wins_by_type.items(),
        key=lambda x: -x[1]["roi_total"] / max(x[1]["starts"] * 2, 1)
    ):
        if stats["starts"] >= 20:
            roi = stats["roi_total"] / (stats["starts"] * 2) * 100
            win_rate = stats["wins"] / stats["starts"] * 100
            if roi > 0:
                profitable_combos.append((jockey, rtype, stats, roi))
                print(f"  {jockey:<25} {rtype:>5} {stats['starts']:>7} {stats['wins']:>5} {win_rate:>5.1f}% {roi:>+7.1f}%")

    if not profitable_combos:
        print("  (None found)")

    # Also show top jockeys overall
    print(f"\nTOP JOCKEYS BY ROI (min 50 starts):")
    print(f"{'Jockey':<30} {'Starts':>7} {'Wins':>5} {'W%':>6} {'ROI':>8}")
    print(f"{'-'*60}")

    top_jockeys = sorted(
        [(j, s) for j, s in jockey_stats.items() if s["starts"] >= 50],
        key=lambda x: -x[1]["roi"]
    )[:20]

    for jockey, stats in top_jockeys:
        print(f"  {jockey:<30} {stats['starts']:>7} {stats['wins']:>5} {stats['win_rate']*100:>5.1f}% {stats['roi']*100:>+7.1f}%")

    return profitable_combos


def scrape_live_odds_and_value_bet():
    """
    This function describes how the LIVE value betting system will work.
    It integrates with the cheat card's existing expert consensus system.
    """
    print(f"\n{'='*60}")
    print(f"LIVE VALUE BETTING SYSTEM DESIGN")
    print(f"{'='*60}")
    print("""
HOW THE LIVE SYSTEM WORKS:

1. BEFORE EACH RACE (10-15 min before post):
   a. Gather expert consensus picks (6 sources - already done by cheat card)
   b. Scrape live tote board odds from OTB API
   c. For each horse, compute:
      - Expert consensus probability (based on how many sources pick them)
      - Model probability (jockey stats + ML odds + adjustments)
      - Tote implied probability (from live odds)

2. IDENTIFY VALUE:
   If (model_prob + expert_prob) / 2 > tote_implied_prob * (1 + min_edge):
       => THIS IS A VALUE BET

3. BET SIZING:
   - Win bets: $2-5 per value bet
   - Place bets: $2-5 when value horse is in top 3 ML
   - Maximum 1-2 bets per race
   - Skip races with no value

4. EXPERT CONSENSUS SCORING:
   - 6/6 sources agree: 45% estimated prob
   - 5/6 sources agree: 35% estimated prob
   - 4/6 sources agree: 25% estimated prob
   - 3/6 sources agree: 15% estimated prob
   - 2/6 or fewer: no bet

5. LIVE OTB ODDS API:
   https://json.offtrackbetting.com/tracks/v2/{track_id}/{date}.json
   This provides live odds pools. Parse the 'pools' section for win odds.
""")


def generate_strategy_update(results, profitable_combos, jockey_stats):
    """Generate the new STRATEGY.md content based on model findings."""

    # Find best performing strategy
    best = None
    for name, r in results.items():
        if r["roi"] > 0 and r["bets"] >= 5:
            if best is None or r["roi"] > best[1]["roi"]:
                best = (name, r)

    # Get top jockeys for the profitable combos
    top_jockeys = sorted(
        [(j, s) for j, s in jockey_stats.items() if s["starts"] >= 50 and s["roi"] > 0],
        key=lambda x: -x[1]["roi"]
    )[:10]

    return best, top_jockeys, profitable_combos


def main():
    print("=" * 60)
    print("VALUE BETTING MODEL - Horse Racing")
    print("Based on Bill Benter's methodology")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    otb_data, ml_data = load_data()
    print(f"OTB: {len(otb_data['race_days'])} track-days, {otb_data['metadata']['total_races']} races")
    print(f"ML:  {len(ml_data)} track-days with morning line odds")

    # Compute statistics
    print("\nComputing jockey statistics from 3,166 races...")
    jockey_stats, jockey_track_stats = compute_jockey_stats(otb_data)
    print(f"  {len(jockey_stats)} jockeys tracked")

    print("Computing post position statistics...")
    pp_stats = compute_post_position_stats(otb_data)

    print("Computing race type statistics...")
    rt_stats = compute_race_type_stats(otb_data)
    for rt, s in sorted(rt_stats.items(), key=lambda x: -x[1]["races"]):
        print(f"  {rt}: {s['races']} races, favorite wins {s['fav_win_rate']:.0%}")

    # Build value dataset from ML data
    print("\nBuilding value dataset (races with ML odds + results)...")
    dataset = build_value_dataset(otb_data, ml_data, jockey_stats, jockey_track_stats, pp_stats)
    print(f"  {len(dataset)} horse entries across {len(set(r['track_day'] for r in dataset))} track-days")

    # Train and backtest value model
    results, model_fn, test_data = train_value_model(dataset)

    # Expanded analysis using all 3,166 races
    profitable_combos = build_expanded_model(otb_data, jockey_stats, pp_stats)

    # Generate strategy recommendations
    best, top_jockeys, combos = generate_strategy_update(results, profitable_combos, jockey_stats)

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY & RECOMMENDATIONS")
    print(f"{'='*60}")

    if best:
        name, r = best
        print(f"\nBest value betting strategy: {name}")
        print(f"  Bets: {r['bets']}, Wins: {r['wins']} ({r['win_rate']:.0f}%)")
        print(f"  Wagered: ${r['wagered']:.0f}, Returned: ${r['returned']:.0f}")
        print(f"  Net: ${r['net']:+.0f} ({r['roi']:+.1f}% ROI)")
        print(f"  Profitable days: {r['profitable_days']}/{r['total_days']}")
    else:
        print("\nNo profitable value strategy found in out-of-sample test.")
        print("This means our model needs more/better features.")

    print(f"\nTop {len(top_jockeys)} profitable jockeys (50+ starts, positive ROI):")
    for j, s in top_jockeys:
        print(f"  {j}: {s['win_rate']*100:.0f}% wins, {s['roi']*100:+.0f}% ROI ({s['starts']} starts)")

    # Live system design
    scrape_live_odds_and_value_bet()

    # Save results
    output = {
        "model_results": {
            name: {k: v for k, v in r.items() if k != "daily_pnl"}
            for name, r in results.items()
        },
        "top_jockeys": [
            {"name": j, **s} for j, s in top_jockeys
        ],
        "profitable_combos": [
            {"jockey": j, "race_type": rt, "starts": s["starts"],
             "wins": s["wins"], "roi": roi}
            for j, rt, s, roi in profitable_combos[:20]
        ],
    }

    output_path = os.path.join(SCRIPT_DIR, "value_model_results.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {output_path}")

    return results


if __name__ == "__main__":
    main()
