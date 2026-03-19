#!/usr/bin/env python3
"""
MEGA BACKTEST — Test every possible betting strategy against real race data.
Uses OTB scraped data (500+ races with exacta/trifecta/superfecta payouts).

Since we don't have ML odds in this data, we use ACTUAL post-time odds
(derived from win payouts) which are MORE accurate than ML odds.

The win payout on a $2 bet tells us the actual odds:
  $2.40 = 1/5 odds (heavy favorite)
  $4.00 = 1/1 (even money)
  $6.00 = 2/1
  $10.00 = 4/1
  $20.00 = 9/1

We rank horses by their finishing position and know the winner's odds.
For the non-winners, we use program number and position to estimate relative
strength, and the exotic payouts give us the REAL return.
"""

import json
import os
import sys
from collections import defaultdict
from itertools import combinations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_data():
    path = os.path.join(SCRIPT_DIR, "otb_race_data.json")
    if not os.path.exists(path):
        print("ERROR: Run scrape_otb.py first!")
        sys.exit(1)
    with open(path) as f:
        data = json.load(f)
    return data


def classify_winner_odds(win_pay):
    """Classify winner by their actual odds (from $2 win payout)."""
    if not win_pay:
        return "unknown"
    odds = (win_pay / 2.0) - 1  # Convert $2 payout to odds
    if odds < 1:
        return "heavy_fav"  # < even money
    elif odds < 2:
        return "fav"  # 1/1 to 2/1
    elif odds < 4:
        return "mid"  # 2/1 to 4/1
    elif odds < 8:
        return "longshot"  # 4/1 to 8/1
    else:
        return "bomb"  # 8/1+


def get_exacta_base_cost(race):
    """Get the base cost for one exacta combo."""
    base = race["exotics"].get("exacta_base", 2)
    return base


def get_trifecta_base_cost(race):
    """Get the base cost for one trifecta combo."""
    base = race["exotics"].get("trifecta_base", 2)
    return base


# =====================================================
# STRATEGY 1: SHOW BETTING ON FAVORITES
# The favorite-longshot bias: favorites are underbet to show
# =====================================================
def strategy_show_favorite(races_by_day, race_types=None):
    """Bet $2 show on the winner IF they were a favorite (low win payout)."""
    total_w, total_r = 0, 0
    daily = {}
    bets, hits = 0, 0

    for day, races in races_by_day.items():
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}
        for race in races:
            if race_types and race["race_type"] not in race_types:
                continue
            # We bet $2 show on EVERY race
            total_w += 2
            daily[day]["w"] += 2
            bets += 1

            # Check if first finisher had show payout
            show_pay = race["wps"].get("show_1", 0)
            if show_pay:
                total_r += show_pay
                daily[day]["r"] += show_pay
                hits += 1

    return calc_result("Show on every winner", total_w, total_r, bets, hits, daily)


# =====================================================
# STRATEGY 2: PLACE BETTING ANALYSIS
# =====================================================
def strategy_place_all(races_by_day, race_types=None):
    """Bet $2 place on every race (to see baseline)."""
    total_w, total_r = 0, 0
    daily = {}
    bets, hits = 0, 0

    for day, races in races_by_day.items():
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}
        for race in races:
            if race_types and race["race_type"] not in race_types:
                continue
            total_w += 2
            daily[day]["w"] += 2
            bets += 1

            place_pay = race["wps"].get("place_1", 0)
            if place_pay:
                total_r += place_pay
                daily[day]["r"] += place_pay
                hits += 1

    return calc_result("Place on winner", total_w, total_r, bets, hits, daily)


# =====================================================
# STRATEGY 3: EXACTA PATTERNS BY FAVORITE STATUS
# Since we know who won and what they paid, we can determine
# if the favorite won and test exacta strategies accordingly.
# =====================================================
def strategy_exacta_fav_wins(races_by_day, race_types=None, max_win_pay=None,
                              min_starters=0):
    """
    Only play exacta in races where the favorite won (low win payout).
    When the favorite wins, the exacta is more likely to be caught because
    the top half of the exacta is resolved.

    This simulates: "If I could tell which races the favorite wins,
    how much would the exacta pay on average?"
    """
    total_w, total_r = 0, 0
    daily = {}
    bets, hits = 0, 0

    for day, races in races_by_day.items():
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}
        for race in races:
            if race_types and race["race_type"] not in race_types:
                continue
            if race["starters"] < min_starters:
                continue
            if not race["exotics"].get("exacta_raw"):
                continue

            win_pay = race["wps"].get("win", 0)
            if max_win_pay and win_pay > max_win_pay:
                continue  # Skip if winner was a longshot

            # We bet exacta base cost
            base = get_exacta_base_cost(race)
            total_w += base
            daily[day]["w"] += base
            bets += 1

            # Since we can't know which exacta combo to play without ML odds,
            # we analyze the average payout
            exacta_pay = race["exotics"]["exacta_raw"]
            total_r += exacta_pay
            daily[day]["r"] += exacta_pay
            hits += 1

    return calc_result(f"Exacta when fav wins (max_pay=${max_win_pay})", total_w, total_r, bets, hits, daily)


# =====================================================
# STRATEGY 4: EXACTA VALUE - Only play races with high exacta payouts
# This is analysis, not a strategy per se, but helps us understand
# what types of races produce profitable exactas.
# =====================================================
def analyze_exacta_by_type(races_by_day):
    """Analyze exacta payouts by race type and winner odds."""
    by_type = defaultdict(list)
    by_odds = defaultdict(list)
    by_starters = defaultdict(list)

    for day, races in races_by_day.items():
        for race in races:
            if not race["exotics"].get("exacta_raw"):
                continue
            exacta = race["exotics"]["exacta_raw"]
            base = get_exacta_base_cost(race)
            normalized = exacta * (2.0 / base)  # Normalize to $2 base

            by_type[race["race_type"]].append(normalized)

            win_pay = race["wps"].get("win", 0)
            category = classify_winner_odds(win_pay)
            by_odds[category].append(normalized)

            if race["starters"] <= 5:
                by_starters["1-5"].append(normalized)
            elif race["starters"] <= 7:
                by_starters["6-7"].append(normalized)
            elif race["starters"] <= 9:
                by_starters["8-9"].append(normalized)
            else:
                by_starters["10+"].append(normalized)

    print("\n=== EXACTA PAYOUT ANALYSIS ===")
    print(f"\n{'Category':<20} {'Count':>6} {'Avg':>8} {'Med':>8} {'Min':>8} {'Max':>8} {'% > $20':>8}")
    print("-" * 72)

    for label, data_dict in [("BY RACE TYPE", by_type), ("BY WINNER ODDS", by_odds), ("BY STARTERS", by_starters)]:
        print(f"\n{label}:")
        for key in sorted(data_dict.keys()):
            vals = sorted(data_dict[key])
            avg = sum(vals) / len(vals)
            med = vals[len(vals) // 2]
            pct_over_20 = 100 * sum(1 for v in vals if v > 20) / len(vals)
            print(f"  {key:<18} {len(vals):>6} ${avg:>7.2f} ${med:>7.2f} ${min(vals):>7.2f} ${max(vals):>7.2f} {pct_over_20:>7.1f}%")


# =====================================================
# STRATEGY 5: SHOW BET GRINDING
# Bet show on every race. Track cumulative profit.
# =====================================================
def strategy_show_grind(races_by_day, race_types=None, min_show_pay=None):
    """
    Bet $2 show on the #1 finisher in every qualifying race.
    This tests the absolute baseline: what if you could always pick the winner?
    Obviously you can't, but it shows the CEILING.
    """
    total_w, total_r = 0, 0
    daily = {}
    bets = 0

    for day, races in races_by_day.items():
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}
        for race in races:
            if race_types and race["race_type"] not in race_types:
                continue
            show_1 = race["wps"].get("show_1", 0)
            if not show_1:
                continue
            if min_show_pay and show_1 < min_show_pay:
                continue

            total_w += 2
            daily[day]["w"] += 2
            total_r += show_1
            daily[day]["r"] += show_1
            bets += 1

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["r"] > d["w"])
    return {
        "name": f"Show grind (types={race_types})",
        "wagered": total_w, "returned": total_r, "net": net, "roi": roi,
        "bets": bets, "hits": bets,
        "profitable_days": profitable_days, "total_days": len(daily),
    }


# =====================================================
# STRATEGY 6: TRIFECTA VALUE ANALYSIS
# =====================================================
def analyze_trifecta_value(races_by_day):
    """Analyze trifecta payouts by race characteristics."""
    by_type = defaultdict(list)
    by_starters = defaultdict(list)

    for day, races in races_by_day.items():
        for race in races:
            if not race["exotics"].get("trifecta_raw"):
                continue
            tri = race["exotics"]["trifecta_raw"]
            base = get_trifecta_base_cost(race)
            normalized = tri * (2.0 / base)

            by_type[race["race_type"]].append(normalized)

            if race["starters"] <= 5:
                by_starters["1-5"].append(normalized)
            elif race["starters"] <= 7:
                by_starters["6-7"].append(normalized)
            elif race["starters"] <= 9:
                by_starters["8-9"].append(normalized)
            else:
                by_starters["10+"].append(normalized)

    print("\n=== TRIFECTA PAYOUT ANALYSIS ===")
    print(f"\n{'Category':<20} {'Count':>6} {'Avg':>8} {'Med':>8} {'Min':>8} {'Max':>10} {'% > $100':>9}")
    print("-" * 75)

    for label, data_dict in [("BY RACE TYPE", by_type), ("BY STARTERS", by_starters)]:
        print(f"\n{label}:")
        for key in sorted(data_dict.keys()):
            vals = sorted(data_dict[key])
            avg = sum(vals) / len(vals)
            med = vals[len(vals) // 2]
            pct_over = 100 * sum(1 for v in vals if v > 100) / len(vals)
            print(f"  {key:<18} {len(vals):>6} ${avg:>7.2f} ${med:>7.2f} ${min(vals):>7.2f} ${max(vals):>9.2f} {pct_over:>8.1f}%")


# =====================================================
# STRATEGY 7: SUPERFECTA LONGSHOT PLAY
# =====================================================
def analyze_superfecta_value(races_by_day):
    """Analyze superfecta payouts."""
    by_type = defaultdict(list)

    for day, races in races_by_day.items():
        for race in races:
            if not race["exotics"].get("superfecta_raw"):
                continue
            sup = race["exotics"]["superfecta_raw"]
            base = race["exotics"].get("superfecta_base", 2)
            normalized = sup * (2.0 / base)

            by_type[race["race_type"]].append(normalized)

    print("\n=== SUPERFECTA PAYOUT ANALYSIS ===")
    print(f"\n{'Race Type':<10} {'Count':>6} {'Avg':>10} {'Med':>10} {'Min':>8} {'Max':>12}")
    print("-" * 60)

    for key in sorted(by_type.keys()):
        vals = sorted(by_type[key])
        avg = sum(vals) / len(vals)
        med = vals[len(vals) // 2]
        print(f"  {key:<8} {len(vals):>6} ${avg:>9.2f} ${med:>9.2f} ${min(vals):>7.2f} ${max(vals):>11.2f}")


# =====================================================
# KEY ANALYSIS: What % of exactas involve the top finishers by odds?
# Since we know the winner's actual odds (from win payout),
# we can analyze correlation between favorites and exotic hits.
# =====================================================
def analyze_favorite_in_exotics(races_by_day):
    """
    For each race, determine if the winner was a favorite (low win payout)
    and what the exacta/trifecta paid. This tells us:
    - How often do favorites hit the exacta?
    - What do exactas pay when favorites are involved?
    - Where is the value?
    """
    categories = {
        "fav_wins": [],     # Win pay <= $5 (0/1 to 3/2)
        "mid_wins": [],     # Win pay $5-$10 (3/2 to 4/1)
        "longshot_wins": [],  # Win pay > $10 (4/1+)
    }

    for day, races in races_by_day.items():
        for race in races:
            win_pay = race["wps"].get("win", 0)
            exacta = race["exotics"].get("exacta_raw", 0)
            trifecta = race["exotics"].get("trifecta_raw", 0)

            if not exacta:
                continue

            if win_pay <= 5:
                categories["fav_wins"].append({"ex": exacta, "tri": trifecta, "win": win_pay})
            elif win_pay <= 10:
                categories["mid_wins"].append({"ex": exacta, "tri": trifecta, "win": win_pay})
            else:
                categories["longshot_wins"].append({"ex": exacta, "tri": trifecta, "win": win_pay})

    print("\n=== FAVORITE INVOLVEMENT IN EXOTICS ===")
    print(f"\n{'Category':<20} {'Count':>6} {'% of All':>8} {'Avg Ex':>10} {'Med Ex':>10} {'Avg Tri':>10}")
    print("-" * 68)

    total = sum(len(v) for v in categories.values())
    for cat, data in categories.items():
        if not data:
            continue
        pct = 100 * len(data) / total
        avg_ex = sum(d["ex"] for d in data) / len(data)
        exs = sorted(d["ex"] for d in data)
        med_ex = exs[len(exs) // 2]
        tris = [d["tri"] for d in data if d["tri"] > 0]
        avg_tri = sum(tris) / len(tris) if tris else 0
        print(f"  {cat:<18} {len(data):>6} {pct:>7.1f}% ${avg_ex:>9.2f} ${med_ex:>9.2f} ${avg_tri:>9.2f}")


# =====================================================
# REALISTIC STRATEGY TEST: What can you actually bet?
# Since we can't pick winners in advance, we need strategies
# that don't require knowing who wins.
# =====================================================

def strategy_all_exacta_box_2(races_by_day, n_horses, race_types=None, min_starters=0):
    """
    Simulate boxing the top N favorites (by program number as proxy).
    Since we don't have pre-race odds, we simulate random selection.

    But actually, what we CAN test is: given the actual exacta payout,
    what's the probability of hitting if we box N horses out of S starters?

    Probability of hitting exacta with N picks from S starters:
    P(hit) = N*(N-1) / (S*(S-1))

    Expected value = P(hit) * exacta_payout - cost
    Cost = N*(N-1) * base_bet (for a box)
    """
    total_ev = 0
    total_cost = 0
    daily = {}
    races_tested = 0

    for day, races in races_by_day.items():
        if day not in daily:
            daily[day] = {"ev": 0, "cost": 0}
        for race in races:
            if race_types and race["race_type"] not in race_types:
                continue
            if race["starters"] < min_starters:
                continue
            if race["starters"] < n_horses:
                continue
            if not race["exotics"].get("exacta_raw"):
                continue

            S = race["starters"]
            base = get_exacta_base_cost(race)
            combos = n_horses * (n_horses - 1)
            cost = combos * base
            p_hit = combos / (S * (S - 1))
            exacta_pay = race["exotics"]["exacta_raw"]
            ev = p_hit * exacta_pay

            total_ev += ev
            total_cost += cost
            daily[day]["ev"] += ev
            daily[day]["cost"] += cost
            races_tested += 1

    roi = ((total_ev - total_cost) / total_cost * 100) if total_cost > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["ev"] > d["cost"])
    return {
        "name": f"Exacta box {n_horses} (EV analysis, types={race_types})",
        "cost": total_cost, "expected_return": total_ev,
        "expected_net": total_ev - total_cost, "roi": roi,
        "races": races_tested,
        "profitable_days": profitable_days, "total_days": len(daily),
    }


def strategy_trifecta_box_ev(races_by_day, n_horses, race_types=None, min_starters=0):
    """
    Expected value analysis for trifecta boxes.
    P(hit) = N*(N-1)*(N-2) / (S*(S-1)*(S-2))
    """
    total_ev = 0
    total_cost = 0
    daily = {}
    races_tested = 0

    for day, races in races_by_day.items():
        if day not in daily:
            daily[day] = {"ev": 0, "cost": 0}
        for race in races:
            if race_types and race["race_type"] not in race_types:
                continue
            if race["starters"] < max(min_starters, n_horses):
                continue
            if not race["exotics"].get("trifecta_raw"):
                continue

            S = race["starters"]
            base = get_trifecta_base_cost(race)
            combos = n_horses * (n_horses - 1) * (n_horses - 2)
            cost = combos * base
            p_hit = combos / (S * (S - 1) * (S - 2))
            tri_pay = race["exotics"]["trifecta_raw"]
            ev = p_hit * tri_pay

            total_ev += ev
            total_cost += cost
            daily[day]["ev"] += ev
            daily[day]["cost"] += cost
            races_tested += 1

    roi = ((total_ev - total_cost) / total_cost * 100) if total_cost > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["ev"] > d["cost"])
    return {
        "name": f"Trifecta box {n_horses} (EV, types={race_types})",
        "cost": total_cost, "expected_return": total_ev,
        "expected_net": total_ev - total_cost, "roi": roi,
        "races": races_tested,
        "profitable_days": profitable_days, "total_days": len(daily),
    }


def strategy_superfecta_box_ev(races_by_day, n_horses, race_types=None, min_starters=0):
    """
    Expected value analysis for superfecta boxes.
    P(hit) = N*(N-1)*(N-2)*(N-3) / (S*(S-1)*(S-2)*(S-3))
    """
    total_ev = 0
    total_cost = 0
    races_tested = 0

    for day, races in races_by_day.items():
        for race in races:
            if race_types and race["race_type"] not in race_types:
                continue
            if race["starters"] < max(min_starters, n_horses):
                continue
            if not race["exotics"].get("superfecta_raw"):
                continue

            S = race["starters"]
            base = race["exotics"].get("superfecta_base", 2)
            combos = n_horses * (n_horses - 1) * (n_horses - 2) * (n_horses - 3)
            cost = combos * base
            p_hit = combos / (S * (S - 1) * (S - 2) * (S - 3))
            sup_pay = race["exotics"]["superfecta_raw"]
            ev = p_hit * sup_pay

            total_ev += ev
            total_cost += cost
            races_tested += 1

    roi = ((total_ev - total_cost) / total_cost * 100) if total_cost > 0 else 0
    return {
        "name": f"Superfecta box {n_horses} (EV, types={race_types})",
        "cost": total_cost, "expected_return": total_ev,
        "expected_net": total_ev - total_cost, "roi": roi,
        "races": races_tested,
    }


def calc_result(name, wagered, returned, bets, hits, daily):
    net = returned - wagered
    roi = (net / wagered * 100) if wagered > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["r"] > d["w"])
    return {
        "name": name,
        "wagered": wagered, "returned": returned, "net": net, "roi": roi,
        "bets": bets, "hits": hits,
        "profitable_days": profitable_days, "total_days": len(daily),
    }


def print_ev_result(r):
    marker = " *** PROFITABLE ***" if r["roi"] > 0 else ""
    print(f"  {r['name']:<55} Cost:${r['cost']:>8.0f} EV:${r['expected_return']:>8.0f} "
          f"Net:${r['expected_net']:>+8.0f} ROI:{r['roi']:>+6.1f}% Races:{r['races']}{marker}")


def print_result(r):
    marker = " ***" if r["roi"] > 0 else ""
    hit_rate = r["hits"] / r["bets"] * 100 if r["bets"] else 0
    print(f"  {r['name']:<55} W:${r['wagered']:>7.0f} R:${r['returned']:>7.0f} "
          f"Net:${r['net']:>+7.0f} ROI:{r['roi']:>+6.1f}% "
          f"Days:{r['profitable_days']}/{r['total_days']}{marker}")


def main():
    data = load_data()
    races_by_day = data["race_days"]
    meta = data["metadata"]

    print("=" * 100)
    print("MEGA BACKTEST — EXHAUSTIVE STRATEGY SEARCH")
    print("=" * 100)
    print(f"Data: {meta['total_track_days']} track-days, {meta['total_races']} races")
    print(f"Period: {meta['start_date']} to {meta['end_date']}")

    # Count by type
    type_counts = defaultdict(int)
    total_races = 0
    for day, races in races_by_day.items():
        for race in races:
            type_counts[race["race_type"]] += 1
            total_races += 1

    print(f"\nRace types:")
    for rt in sorted(type_counts.keys()):
        print(f"  {rt}: {type_counts[rt]} ({100*type_counts[rt]/total_races:.1f}%)")

    # ============ ANALYSIS PHASE ============
    analyze_exacta_by_type(races_by_day)
    analyze_trifecta_value(races_by_day)
    analyze_superfecta_value(races_by_day)
    analyze_favorite_in_exotics(races_by_day)

    # ============ EV ANALYSIS: EXACTA BOXES ============
    print("\n" + "=" * 100)
    print("EXPECTED VALUE ANALYSIS: EXACTA BOXES")
    print("If you randomly pick N horses, what's the expected return?")
    print("=" * 100)

    for n in [2, 3, 4, 5, 6]:
        for types in [None, ["CLM"], ["CLM", "MC"], ["CLM", "MC", "SOC"],
                       ["MSW"], ["ALW", "AOC"], ["STK"]]:
            type_label = str(types) if types else "ALL"
            r = strategy_all_exacta_box_2(races_by_day, n, race_types=types)
            if r["races"] > 10:
                r["name"] = f"Ex box {n} ({type_label})"
                print_ev_result(r)
        print()

    # ============ EV ANALYSIS: TRIFECTA BOXES ============
    print("\n" + "=" * 100)
    print("EXPECTED VALUE ANALYSIS: TRIFECTA BOXES")
    print("=" * 100)

    for n in [3, 4, 5, 6]:
        for types in [None, ["CLM"], ["CLM", "MC"], ["CLM", "MC", "SOC"]]:
            type_label = str(types) if types else "ALL"
            for min_s in [0, 6, 8]:
                r = strategy_trifecta_box_ev(races_by_day, n, race_types=types, min_starters=min_s)
                if r["races"] > 10:
                    r["name"] = f"Tri box {n} ({type_label}, {min_s}+ starters)"
                    print_ev_result(r)
        print()

    # ============ EV ANALYSIS: SUPERFECTA BOXES ============
    print("\n" + "=" * 100)
    print("EXPECTED VALUE ANALYSIS: SUPERFECTA BOXES")
    print("=" * 100)

    for n in [4, 5, 6, 7, 8]:
        for types in [None, ["CLM"], ["CLM", "MC"], ["CLM", "MC", "SOC"]]:
            type_label = str(types) if types else "ALL"
            r = strategy_superfecta_box_ev(races_by_day, n, race_types=types, min_starters=6)
            if r["races"] > 10:
                r["name"] = f"Super box {n} ({type_label})"
                print_ev_result(r)
        print()

    # ============ KEY QUESTION: CAN HANDICAPPING OVERCOME THE TAKEOUT? ============
    print("\n" + "=" * 100)
    print("THE REAL QUESTION: HANDICAPPING EDGE NEEDED")
    print("=" * 100)
    print("""
    Random picking gives negative EV due to the house takeout (15-25%).
    To be profitable, you need a HANDICAPPING EDGE that makes your picks
    better than random.

    If random box-3 exacta has -X% ROI, you need to pick horses that
    finish 1-2 at LEAST (1 + X/100) times more often than random.

    Example: If random 3-horse box has -20% ROI, you need to be 25%
    better than random at picking top-2 finishers to break even.

    The question is: Can handicapping provide that edge?
    Academic research says: YES, but only for the best handicappers,
    and only on specific bet types.
    """)

    # Calculate required edge for each bet type
    for label, func, n_vals in [
        ("EXACTA", strategy_all_exacta_box_2, [2, 3, 4, 5]),
        ("TRIFECTA", strategy_trifecta_box_ev, [3, 4, 5]),
    ]:
        print(f"\n{label} - Required handicapping edge to break even:")
        for n in n_vals:
            r = func(races_by_day, n, race_types=["CLM", "MC", "SOC"])
            if r["races"] > 0 and r["roi"] < 0:
                edge_needed = -r["roi"] / (100 + r["roi"]) * 100
                print(f"  Box {n}: ROI = {r['roi']:+.1f}%, need {edge_needed:.1f}% better than random")

    # ============ BEST OPPORTUNITIES ============
    print("\n" + "=" * 100)
    print("BEST OPPORTUNITIES FOUND")
    print("=" * 100)

    # Find all strategies with closest to positive EV
    all_results = []

    for n in [2, 3, 4, 5, 6]:
        for types in [None, ["CLM"], ["CLM", "MC"], ["CLM", "MC", "SOC"],
                       ["MSW"], ["ALW", "AOC"]]:
            r = strategy_all_exacta_box_2(races_by_day, n, race_types=types)
            if r["races"] > 20:
                type_label = str(types) if types else "ALL"
                r["name"] = f"Exacta box {n} ({type_label})"
                all_results.append(r)

    for n in [3, 4, 5, 6]:
        for types in [None, ["CLM"], ["CLM", "MC"], ["CLM", "MC", "SOC"]]:
            for min_s in [0, 6, 8]:
                r = strategy_trifecta_box_ev(races_by_day, n, race_types=types, min_starters=min_s)
                if r["races"] > 20:
                    type_label = str(types) if types else "ALL"
                    r["name"] = f"Trifecta box {n} ({type_label}, {min_s}+)"
                    all_results.append(r)

    for n in [4, 5, 6, 7, 8]:
        for types in [None, ["CLM"], ["CLM", "MC"]]:
            r = strategy_superfecta_box_ev(races_by_day, n, race_types=types, min_starters=6)
            if r["races"] > 20:
                type_label = str(types) if types else "ALL"
                r["name"] = f"Superfecta box {n} ({type_label})"
                all_results.append(r)

    # Sort by ROI
    all_results.sort(key=lambda x: x["roi"], reverse=True)

    print("\nTop 20 strategies by expected ROI:")
    for r in all_results[:20]:
        print_ev_result(r)

    print("\nBottom 10 (worst strategies):")
    for r in all_results[-10:]:
        print_ev_result(r)

    # Save results
    output = {
        "metadata": meta,
        "total_races_analyzed": total_races,
        "race_type_counts": dict(type_counts),
        "top_strategies": [
            {"name": r["name"], "roi": r["roi"], "races": r["races"],
             "cost": r["cost"], "ev": r["expected_return"]}
            for r in all_results[:20]
        ],
    }

    output_path = os.path.join(SCRIPT_DIR, "mega_backtest_results.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
