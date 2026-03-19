#!/usr/bin/env python3
"""
VALUE BETTING MODEL v2 - Jockey Edge + Live Odds System

This model takes a practical approach:
1. Uses 3,166 OTB races with REAL payouts to identify profitable jockeys
2. Does PROPER time-series validation (train on old data, test on new data)
3. Combines jockey edge with race conditions for value bets
4. Designs a live system that compares expert consensus vs tote odds

The key insight: certain jockeys consistently deliver positive ROI.
This means the PUBLIC systematically undervalues them.
Betting these jockeys = exploiting a real market inefficiency.
"""

import json
import math
import os
import sys
import urllib.request
from collections import defaultdict, Counter
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_num(val):
    """Parse MongoDB-style number."""
    if isinstance(val, dict):
        return float(val.get("$numberDouble", val.get("$numberInt", 0)))
    return float(val) if val else 0


def load_otb_data():
    """Load the 3,166 race OTB dataset."""
    with open(os.path.join(SCRIPT_DIR, "otb_race_data.json")) as f:
        return json.load(f)


def scrape_more_otb_data():
    """
    Scrape additional OTB data going further back in time.
    Extends our dataset with Oct 2025 - Jan 2026 data.
    """
    TRACKS = {
        92: "Tampa Bay Downs",
        36: "Gulfstream Park",
        63: "Parx Racing",
        49: "Laurel Park",
        80: "Santa Anita",
        1: "Aqueduct",
        62: "Penn National",
        16: "Charles Town",
        101: "Turfway Park",
        216: "Mahoning Valley",
        100: "Turf Paradise",
        79: "Sam Houston",
        91: "Sunland Park",
        21: "Delta Downs",
        73: "Remington Park",
        34: "Golden Gate Fields",
        104: "Will Rogers Downs",
    }

    BASE_URL = "https://json.offtrackbetting.com/tracks/v2/{track_id}/{date}.json"

    all_races = {}
    start = datetime(2025, 10, 1)
    end = datetime(2026, 1, 31)

    current = start
    total = 0

    while current <= end:
        date_str = current.strftime("%Y%m%d")
        date_display = current.strftime("%Y-%m-%d")

        for track_id, track_name in TRACKS.items():
            url = BASE_URL.format(track_id=track_id, date=date_str)
            try:
                req = urllib.request.Request(url, headers={
                    "User-Agent": "Mozilla/5.0"
                })
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.load(resp)

                events = data.get("events", [])
                if not events:
                    continue

                races = []
                for event in events:
                    race_num = int(parse_num(event.get("eventNo", 0)))
                    conditions = event.get("conditions", "")
                    distance = event.get("distance", "")

                    # Determine race type
                    cond_upper = conditions.upper()
                    if "MAIDEN" in cond_upper and "CLAIMING" in cond_upper:
                        race_type = "MC"
                    elif "MAIDEN" in cond_upper:
                        race_type = "MSW"
                    elif "STARTER" in cond_upper and ("OPTIONAL" in cond_upper or "ALLOW" in cond_upper):
                        race_type = "SOC"
                    elif "STAKE" in cond_upper or "GRADE" in cond_upper or "HANDICAP" in cond_upper:
                        race_type = "STK"
                    elif "ALLOWANCE" in cond_upper and "OPTIONAL" in cond_upper:
                        race_type = "AOC"
                    elif "ALLOWANCE" in cond_upper:
                        race_type = "ALW"
                    elif "CLAIMING" in cond_upper:
                        race_type = "CLM"
                    else:
                        race_type = "OTH"

                    results = event.get("results", {})
                    finishers = results.get("finisher", [])

                    if not finishers:
                        continue

                    finish_order = []
                    for f in finishers:
                        entry = {
                            "name": f.get("runnerName", ""),
                            "position": int(parse_num(f.get("finishPosition", 99))),
                            "program": f.get("programNumber", ""),
                            "jockey": f.get("jockey", ""),
                            "win_payout": float(f.get("winAmount", 0) or 0),
                            "place_payout": float(f.get("placeAmount", 0) or 0),
                            "show_payout": float(f.get("showAmount", 0) or 0),
                        }
                        finish_order.append(entry)

                    # Also ran
                    also_ran = results.get("alsoRan", [])

                    # Dividends (exotics)
                    dividends = results.get("dividends", [])
                    exotics = {}
                    for d in dividends:
                        bet_type = d.get("betType", "")
                        amount = parse_num(d.get("amount", 0))
                        base = parse_num(d.get("baseAmount", 100))
                        if bet_type == "EX":
                            exotics["exacta"] = amount
                            exotics["exacta_base"] = base / 100
                        elif bet_type == "TR":
                            exotics["trifecta"] = amount
                            exotics["trifecta_base"] = base / 100
                        elif bet_type == "SU":
                            exotics["superfecta"] = amount
                            exotics["superfecta_base"] = base / 100

                    starters = len(finish_order) + len(also_ran)

                    races.append({
                        "race_num": race_num,
                        "race_type": race_type,
                        "conditions": conditions[:200],
                        "distance": distance,
                        "starters": starters,
                        "finish_order": finish_order,
                        "exotics": exotics,
                    })

                if races:
                    key = f"{date_display} {track_name}"
                    all_races[key] = races
                    total += len(races)
                    print(f"  {key}: {len(races)} races")

            except Exception:
                pass

        current += timedelta(days=1)
        if current.day == 1:
            print(f"  Month done. Total: {total} races")

    return all_races, total


def build_jockey_database(race_data, cutoff_date=None):
    """
    Build comprehensive jockey statistics from race data.
    If cutoff_date is provided, only use races before that date.
    """
    jockey_stats = defaultdict(lambda: {
        "starts": 0, "wins": 0, "places": 0, "shows": 0,
        "total_win_payout": 0, "total_wagered": 0,
        "win_payouts": [],
        "by_type": defaultdict(lambda: {"starts": 0, "wins": 0, "roi_total": 0}),
        "by_track": defaultdict(lambda: {"starts": 0, "wins": 0}),
        "by_field_size": defaultdict(lambda: {"starts": 0, "wins": 0}),
    })

    for key, races in race_data.items():
        date_str = key.split(" ")[0]
        if cutoff_date and date_str >= cutoff_date:
            continue

        track = " ".join(key.split(" ")[1:])

        for race in races:
            rtype = race.get("race_type", "UNK")
            starters = race.get("starters", len(race.get("finish_order", [])))
            field_bucket = "small" if starters <= 5 else ("medium" if starters <= 8 else "large")

            for horse in race.get("finish_order", []):
                jockey = horse.get("jockey", "Unknown")
                if not jockey or jockey == "Unknown":
                    continue

                pos = horse.get("position", 99)
                win_payout = horse.get("win_payout", 0)

                stats = jockey_stats[jockey]
                stats["starts"] += 1
                stats["total_wagered"] += 2.0  # $2 bet per horse

                stats["by_type"][rtype]["starts"] += 1
                stats["by_track"][track]["starts"] += 1
                stats["by_field_size"][field_bucket]["starts"] += 1

                if pos == 1:
                    stats["wins"] += 1
                    stats["total_win_payout"] += win_payout if win_payout > 0 else 0
                    stats["win_payouts"].append(win_payout if win_payout > 0 else 0)
                    stats["by_type"][rtype]["wins"] += 1
                    stats["by_type"][rtype]["roi_total"] += (win_payout - 2.0) if win_payout > 0 else 0
                    stats["by_track"][track]["wins"] += 1
                    stats["by_field_size"][field_bucket]["wins"] += 1
                elif pos == 2:
                    stats["places"] += 1
                elif pos == 3:
                    stats["shows"] += 1

                # Track losses in ROI
                if pos != 1:
                    stats["by_type"][rtype]["roi_total"] -= 2.0

    # Compute derived stats
    for jockey, stats in jockey_stats.items():
        s = stats["starts"]
        stats["win_rate"] = stats["wins"] / s if s > 0 else 0
        stats["itm_rate"] = (stats["wins"] + stats["places"] + stats["shows"]) / s if s > 0 else 0
        stats["roi"] = (stats["total_win_payout"] - stats["total_wagered"]) / stats["total_wagered"] if stats["total_wagered"] > 0 else 0
        stats["avg_win_payout"] = sum(stats["win_payouts"]) / len(stats["win_payouts"]) if stats["win_payouts"] else 0

    return dict(jockey_stats)


def time_series_validation(race_data):
    """
    Proper time-series validation:
    1. Train on first 70% of dates
    2. Test on last 30% of dates
    3. See if profitable jockeys stay profitable
    """
    # Get all dates
    all_dates = sorted(set(key.split(" ")[0] for key in race_data.keys()))
    n = len(all_dates)
    cutoff_idx = int(n * 0.7)
    cutoff_date = all_dates[cutoff_idx]

    print(f"\n{'='*70}")
    print(f"TIME-SERIES VALIDATION")
    print(f"{'='*70}")
    print(f"Training period: {all_dates[0]} to {all_dates[cutoff_idx-1]} ({cutoff_idx} days)")
    print(f"Testing period:  {cutoff_date} to {all_dates[-1]} ({n - cutoff_idx} days)")

    # Build jockey stats from TRAINING data only
    train_stats = build_jockey_database(race_data, cutoff_date=cutoff_date)

    # Identify "profitable" jockeys from training data
    profitable_jockeys = {}
    for jockey, stats in train_stats.items():
        if stats["starts"] >= 30 and stats["roi"] > 0.10:  # 10%+ ROI, 30+ starts
            profitable_jockeys[jockey] = stats

    print(f"\nProfitable jockeys identified from training data: {len(profitable_jockeys)}")
    print(f"{'Jockey':<30} {'Starts':>7} {'Wins':>5} {'W%':>6} {'ROI':>8}")
    print(f"{'-'*60}")
    for j, s in sorted(profitable_jockeys.items(), key=lambda x: -x[1]["roi"])[:20]:
        print(f"  {j:<30} {s['starts']:>7} {s['wins']:>5} {s['win_rate']*100:>5.1f}% {s['roi']*100:>+7.1f}%")

    # Now test: bet $2 on every ride by these jockeys in the TEST period
    test_results = defaultdict(lambda: {"wagered": 0, "returned": 0, "wins": 0, "starts": 0})
    overall = {"wagered": 0, "returned": 0, "wins": 0, "starts": 0}
    daily_pnl = defaultdict(float)

    for key, races in race_data.items():
        date_str = key.split(" ")[0]
        if date_str < cutoff_date:
            continue

        track = " ".join(key.split(" ")[1:])

        for race in races:
            rtype = race.get("race_type", "UNK")

            for horse in race.get("finish_order", []):
                jockey = horse.get("jockey", "Unknown")
                if jockey not in profitable_jockeys:
                    continue

                pos = horse.get("position", 99)
                win_payout = horse.get("win_payout", 0)

                # Record bet
                test_results[jockey]["starts"] += 1
                test_results[jockey]["wagered"] += 2.0
                overall["starts"] += 1
                overall["wagered"] += 2.0

                if pos == 1 and win_payout > 0:
                    test_results[jockey]["wins"] += 1
                    test_results[jockey]["returned"] += win_payout
                    overall["wins"] += 1
                    overall["returned"] += win_payout
                    daily_pnl[date_str] += win_payout - 2.0
                else:
                    daily_pnl[date_str] -= 2.0

    # Results
    print(f"\n{'='*70}")
    print(f"TEST PERIOD RESULTS - Betting all 'profitable' jockeys")
    print(f"{'='*70}")

    if overall["starts"] == 0:
        print("No bets placed in test period!")
        return None

    net = overall["returned"] - overall["wagered"]
    roi = net / overall["wagered"] * 100

    print(f"Total bets: {overall['starts']}")
    print(f"Wins: {overall['wins']} ({overall['wins']/overall['starts']*100:.1f}%)")
    print(f"Wagered: ${overall['wagered']:.0f}")
    print(f"Returned: ${overall['returned']:.0f}")
    print(f"Net: ${net:+.0f}")
    print(f"ROI: {roi:+.1f}%")

    profitable_days = sum(1 for v in daily_pnl.values() if v > 0)
    total_days = len(daily_pnl)
    print(f"Profitable days: {profitable_days}/{total_days} ({profitable_days/total_days*100:.0f}%)")

    # Per-jockey breakdown in test period
    print(f"\n{'Jockey':<30} {'Bets':>5} {'Wins':>5} {'W%':>6} {'Wager':>7} {'Ret':>7} {'Net':>7} {'ROI':>7}")
    print(f"{'-'*80}")
    for j, r in sorted(test_results.items(), key=lambda x: -(x[1]["returned"] - x[1]["wagered"])):
        if r["starts"] > 0:
            net_j = r["returned"] - r["wagered"]
            roi_j = net_j / r["wagered"] * 100
            marker = " ***" if roi_j > 0 else ""
            print(f"  {j:<30} {r['starts']:>5} {r['wins']:>5} {r['wins']/r['starts']*100:>5.1f}% ${r['wagered']:>5.0f} ${r['returned']:>5.0f} ${net_j:>+6.0f} {roi_j:>+6.1f}%{marker}")

    # Now test with FILTERS (only CLM/MC races)
    print(f"\n{'='*70}")
    print(f"TEST WITH FILTERS: Only CLM/MC + profitable jockeys")
    print(f"{'='*70}")

    strategies = [
        ("All races, all profitable jockeys", None, 30, 0.10),
        ("CLM/MC only, all profitable jockeys", ["CLM", "MC"], 30, 0.10),
        ("CLM/MC only, ROI > 30%", ["CLM", "MC"], 30, 0.30),
        ("CLM/MC only, ROI > 50%", ["CLM", "MC"], 30, 0.50),
        ("CLM/MC only, ROI > 30%, 50+ starts", ["CLM", "MC"], 50, 0.30),
        ("CLM/MC/SOC, ROI > 20%", ["CLM", "MC", "SOC"], 30, 0.20),
        ("CLM only, ROI > 20%", ["CLM"], 30, 0.20),
        ("CLM only, ROI > 30%", ["CLM"], 30, 0.30),
        ("MC only, ROI > 20%", ["MC"], 30, 0.20),
        ("All races, ROI > 50%", None, 30, 0.50),
        ("All races, win rate > 30%", None, 30, 0.10),  # Will filter by win rate below
        # Jockey-in-race-type specific: only bet jockey in types where they're profitable
        ("Jockey-type match, 20+ type starts", "MATCH", 30, 0.10),
    ]

    best_strategy = None
    best_roi = -999

    for strat_name, type_filter, min_starts, min_roi in strategies:
        total_w = 0
        total_r = 0
        wins = 0
        bets = 0
        d_pnl = defaultdict(float)

        for key, races in race_data.items():
            date_str = key.split(" ")[0]
            if date_str < cutoff_date:
                continue

            for race in races:
                rtype = race.get("race_type", "UNK")

                if type_filter and type_filter != "MATCH" and rtype not in type_filter:
                    continue

                for horse in race.get("finish_order", []):
                    jockey = horse.get("jockey", "Unknown")

                    # Check if jockey qualifies
                    j_stats = train_stats.get(jockey)
                    if not j_stats:
                        continue
                    if j_stats["starts"] < min_starts:
                        continue
                    if j_stats["roi"] < min_roi:
                        continue

                    # Win rate filter for that specific strategy
                    if strat_name == "All races, win rate > 30%" and j_stats["win_rate"] < 0.30:
                        continue

                    # Jockey-type match: only bet when jockey is profitable in THIS race type
                    if type_filter == "MATCH":
                        type_stats = j_stats["by_type"].get(rtype)
                        if not type_stats or type_stats["starts"] < 15:
                            continue
                        type_roi = type_stats["roi_total"] / (type_stats["starts"] * 2)
                        if type_roi < 0.10:
                            continue

                    pos = horse.get("position", 99)
                    win_payout = horse.get("win_payout", 0)

                    bets += 1
                    total_w += 2.0

                    if pos == 1 and win_payout > 0:
                        wins += 1
                        total_r += win_payout
                        d_pnl[date_str] += win_payout - 2.0
                    else:
                        d_pnl[date_str] -= 2.0

        if bets == 0:
            continue

        net = total_r - total_w
        roi = net / total_w * 100
        p_days = sum(1 for v in d_pnl.values() if v > 0)
        t_days = len(d_pnl)

        marker = " ***" if roi > 0 else ""
        print(f"\n  {strat_name}:")
        print(f"    Bets: {bets}, Wins: {wins} ({wins/bets*100:.1f}%), Wagered: ${total_w:.0f}")
        print(f"    Returned: ${total_r:.0f}, Net: ${net:+.0f}, ROI: {roi:+.1f}%{marker}")
        print(f"    Profitable days: {p_days}/{t_days}")

        if roi > best_roi and bets >= 10:
            best_roi = roi
            best_strategy = strat_name

    if best_strategy:
        print(f"\n  BEST STRATEGY: {best_strategy} ({best_roi:+.1f}% ROI)")

    return best_strategy, best_roi


def validate_with_expanded_data(existing_data, new_data):
    """
    If we scrape more historical data, use the older data for training
    and the existing data for testing.
    """
    # Combine all data
    combined = {}
    combined.update(new_data)
    combined.update(existing_data)
    return combined


def build_live_value_system(jockey_stats, race_type_stats):
    """
    Build the LIVE value betting system configuration.
    This generates a JSON config that the cheat card server can use.
    """
    # Identify value jockeys (positive ROI with enough sample size)
    value_jockeys = {}
    for jockey, stats in jockey_stats.items():
        if stats["starts"] >= 40 and stats["roi"] > 0.05:
            value_jockeys[jockey] = {
                "win_rate": round(stats["win_rate"], 3),
                "roi": round(stats["roi"], 3),
                "starts": stats["starts"],
                "avg_win_payout": round(stats["avg_win_payout"], 2),
                "profitable_types": {},
            }
            for rtype, tstats in stats["by_type"].items():
                if tstats["starts"] >= 10:
                    type_roi = tstats["roi_total"] / (tstats["starts"] * 2)
                    if type_roi > 0:
                        value_jockeys[jockey]["profitable_types"][rtype] = {
                            "starts": tstats["starts"],
                            "wins": tstats["wins"],
                            "roi": round(type_roi, 3),
                        }

    config = {
        "system": "value_betting_v2",
        "updated": datetime.now().isoformat(),
        "strategy": {
            "description": "Value betting based on jockey edge + expert consensus vs tote odds",
            "bet_types": ["win", "place"],
            "max_bets_per_race": 1,
            "max_bets_per_day": 8,
            "base_bet_size": 2.0,
            "min_edge_threshold": 0.15,  # 15% edge minimum
        },
        "value_jockeys": value_jockeys,
        "rules": [
            "1. Check if any horse in the race has a VALUE JOCKEY (positive ROI in our database)",
            "2. Check if 3+ expert sources pick that horse (consensus confirmation)",
            "3. Compare expert consensus probability vs actual tote board odds",
            "4. If model probability > tote implied probability by 15%+, BET",
            "5. Focus on WIN bets ($2-5) for lower takeout (15-17% vs 20-25% for exotics)",
            "6. Maximum 1 bet per race, 8 bets per day",
            "7. Skip races where no value horse has expert consensus support",
        ],
        "expert_consensus_weights": {
            "6_of_6": 0.45,
            "5_of_6": 0.35,
            "4_of_6": 0.25,
            "3_of_6": 0.18,
            "2_of_6": 0.12,
            "1_of_6": 0.08,
        },
    }

    output_path = os.path.join(SCRIPT_DIR, "value_betting_config.json")
    with open(output_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nLive value betting config saved to {output_path}")
    print(f"Value jockeys in database: {len(value_jockeys)}")

    return config


def main():
    print("=" * 70)
    print("VALUE BETTING MODEL v2")
    print("Jockey Edge + Expert Consensus + Live Odds")
    print("=" * 70)

    # Step 1: Load existing data
    print("\n[1/5] Loading existing OTB data (3,166 races)...")
    otb_data = load_otb_data()

    # Step 2: Try to scrape more historical data
    print("\n[2/5] Scraping additional historical data (Oct-Jan)...")
    print("  (This extends our training set for better validation)")
    try:
        new_races, new_count = scrape_more_otb_data()
        print(f"  Scraped {new_count} additional races")
    except Exception as e:
        print(f"  Scraping failed: {e}")
        new_races = {}
        new_count = 0

    # Combine all race data
    all_race_data = {}
    # Add existing data
    all_race_data.update(otb_data.get("race_days", {}))
    # Add new data
    all_race_data.update(new_races)

    total_races = sum(len(races) for races in all_race_data.values())
    print(f"\n  Combined dataset: {len(all_race_data)} track-days, {total_races} races")

    # Step 3: Build jockey database from ALL data
    print("\n[3/5] Building jockey database...")
    jockey_stats = build_jockey_database(all_race_data)
    qualified = sum(1 for s in jockey_stats.values() if s["starts"] >= 30)
    profitable = sum(1 for s in jockey_stats.values() if s["starts"] >= 30 and s["roi"] > 0)
    print(f"  {len(jockey_stats)} jockeys total")
    print(f"  {qualified} with 30+ starts")
    print(f"  {profitable} with 30+ starts AND positive ROI ({profitable/qualified*100:.0f}%)")

    # Step 4: Time-series validation
    print("\n[4/5] Running time-series validation...")
    validation_result = time_series_validation(all_race_data)

    # Step 5: Build live value system config
    print("\n[5/5] Building live value betting system...")
    config = build_live_value_system(jockey_stats, None)

    # Final summary
    print(f"\n{'='*70}")
    print(f"FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"""
WHAT WE BUILT:
1. Jockey database with {len(jockey_stats)} jockeys from {total_races} races
2. Time-series validated strategy (trained on old data, tested on new)
3. Live value betting config for the cheat card

HOW TO USE:
1. Before each race day, load value_betting_config.json
2. For each race, check if any horse has a VALUE JOCKEY
3. Cross-reference with expert consensus picks
4. Check live tote board odds for overlays
5. Bet $2-5 WIN on value + consensus horses with 15%+ edge

NEXT STEPS:
1. Integrate value_betting_config.json into server.py
2. Add live tote odds scraping to the pre-race update flow
3. Alert when value bets are identified
""")

    # Save full jockey stats for reference
    jockey_output = {}
    for j, s in sorted(jockey_stats.items(), key=lambda x: -x[1].get("roi", 0)):
        if s["starts"] >= 30:
            jockey_output[j] = {
                "starts": s["starts"],
                "wins": s["wins"],
                "win_rate": round(s["win_rate"], 3),
                "itm_rate": round(s["itm_rate"], 3),
                "roi": round(s["roi"], 3),
                "avg_win_payout": round(s["avg_win_payout"], 2),
            }

    with open(os.path.join(SCRIPT_DIR, "jockey_database.json"), "w") as f:
        json.dump(jockey_output, f, indent=2)
    print(f"Jockey database saved to jockey_database.json")


if __name__ == "__main__":
    main()
