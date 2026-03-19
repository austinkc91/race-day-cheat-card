#!/usr/bin/env python3
"""
DEFINITIVE BACKTEST — Test EVERY strategy variation on 100+ real races
with actual ML odds and exotic payouts across 13 track-days.

This is the final answer on whether a mechanical strategy can be profitable.
"""

import json
import os
import sys
from collections import defaultdict
from itertools import combinations, permutations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from combined_ml_data import RACES, get_ml_rank, get_ml_sorted


def load_otb_payouts():
    """Load OTB exotic payouts to match with our ML data."""
    path = os.path.join(SCRIPT_DIR, "otb_race_data.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        data = json.load(f)
    return data.get("race_days", {})


def match_otb_payout(race, otb_data):
    """Try to find matching OTB data for this race to get exotic payouts."""
    # First check if race already has payouts (from deep_backtest data)
    if race.get("exacta_pay"):
        return race.get("exacta_pay"), race.get("trifecta_pay"), race.get("superfecta_pay")

    # Try to match by day/track and race number
    day = race["day"]
    race_num = race["race"]

    # Map our day format to OTB format
    day_map = {
        "TAM 2026-03-14": "2026-03-14 Tampa Bay Downs",
        "TAM 2026-03-07": "2026-03-07 Tampa Bay Downs",
        "TAM 2026-03-01": "2026-03-01 Tampa Bay Downs",
        "TAM 2026-02-28": "2026-02-28 Tampa Bay Downs",
        "TAM 2026-02-22": "2026-02-22 Tampa Bay Downs",
        "SUN 2026-03-09": "2026-03-09 Sunland Park",
        "SUN 2026-03-02": "2026-03-02 Sunland Park",
        "OAK 2026-03-15": "2026-03-15 Oaklawn Park",
        "Parx Mar 18": "2026-03-18 Parx Racing",
        "Parx Mar 17": "2026-03-17 Parx Racing",
        "Parx Mar 16": "2026-03-16 Parx Racing",
        "FG Mar 16": "2026-03-16 Fair Grounds",
        "FG Mar 15": "2026-03-15 Fair Grounds",
    }

    otb_key = day_map.get(day)
    if not otb_key or otb_key not in otb_data:
        return None, None, None

    otb_races = otb_data[otb_key]
    for otb_race in otb_races:
        if otb_race["race_num"] == race_num:
            ex = otb_race["exotics"].get("exacta_raw")
            tri = otb_race["exotics"].get("trifecta_raw")
            sup = otb_race["exotics"].get("superfecta_raw")
            return ex, tri, sup

    return None, None, None


# =====================================================
# STRATEGY FUNCTIONS
# =====================================================

def test_exacta_strategy(races, combos_func, bet_per_combo=1.0, race_types=None,
                          min_starters=0, name=""):
    """
    Test an exacta strategy.
    combos_func(race) returns list of (winner_rank, placer_rank) tuples to bet.
    """
    total_w, total_r = 0, 0
    daily = {}
    hits, plays = 0, 0
    hit_details = []

    for race in races:
        if race_types and race["type"] not in race_types:
            continue
        if race["starters"] < min_starters:
            continue

        ex_pay = race.get("_exacta_pay")
        if not ex_pay:
            continue

        day = race["day"]
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}

        finish = race["finish"]
        if len(finish) < 2:
            continue

        combos = combos_func(race)
        cost = bet_per_combo * len(combos)
        total_w += cost
        daily[day]["w"] += cost
        plays += 1

        winner_rank = get_ml_rank(race, finish[0])
        placer_rank = get_ml_rank(race, finish[1])

        for (wr, pr) in combos:
            if winner_rank == wr and placer_rank == pr:
                payout = ex_pay * (bet_per_combo / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1
                hit_details.append({
                    "day": day, "race": race["race"],
                    "pattern": f"#{wr}-#{pr}", "payout": payout,
                    "winner": finish[0], "placer": finish[1]
                })
                break

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["r"] > d["w"])
    return {
        "name": name, "wagered": total_w, "returned": total_r, "net": net, "roi": roi,
        "hits": hits, "plays": plays, "hit_rate": (hits/plays*100 if plays else 0),
        "profitable_days": profitable_days, "total_days": len(daily),
        "hit_details": hit_details, "daily": daily,
    }


def test_trifecta_strategy(races, combos_func, bet_per_combo=1.0, race_types=None,
                            min_starters=0, name=""):
    """Test a trifecta strategy."""
    total_w, total_r = 0, 0
    daily = {}
    hits, plays = 0, 0

    for race in races:
        if race_types and race["type"] not in race_types:
            continue
        if race["starters"] < min_starters:
            continue

        tri_pay = race.get("_trifecta_pay")
        if not tri_pay:
            continue

        day = race["day"]
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}

        finish = race["finish"]
        if len(finish) < 3:
            continue

        combos = combos_func(race)
        cost = bet_per_combo * len(combos)
        total_w += cost
        daily[day]["w"] += cost
        plays += 1

        ranks = tuple(get_ml_rank(race, finish[i]) for i in range(3))

        for combo in combos:
            if ranks == combo:
                payout = tri_pay * (bet_per_combo / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1
                break

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["r"] > d["w"])
    return {
        "name": name, "wagered": total_w, "returned": total_r, "net": net, "roi": roi,
        "hits": hits, "plays": plays, "hit_rate": (hits/plays*100 if plays else 0),
        "profitable_days": profitable_days, "total_days": len(daily),
    }


def print_result(r, show_details=False):
    marker = " *** WINNER ***" if r["roi"] > 0 else ""
    print(f"  {r['name']:<60s} W:${r['wagered']:>7.1f} R:${r['returned']:>7.1f} "
          f"Net:${r['net']:>+8.1f} ROI:{r['roi']:>+6.1f}% "
          f"Hit:{r['hits']}/{r['plays']}({r['hit_rate']:.0f}%) "
          f"Days:{r['profitable_days']}/{r['total_days']}{marker}")
    if show_details and r.get("hit_details"):
        for h in r["hit_details"]:
            print(f"      HIT: {h['day']} R{h['race']} {h['pattern']} "
                  f"({h.get('winner','')}/{h.get('placer','')}) -> ${h['payout']:.2f}")


def main():
    print("=" * 120)
    print("DEFINITIVE BACKTEST — 100+ Races, Real ML Odds, Real Exotic Payouts")
    print("=" * 120)

    # Load OTB payouts and match to our ML data
    otb_data = load_otb_payouts()

    # Enrich races with exotic payouts
    matched = 0
    for race in RACES:
        ex, tri, sup = match_otb_payout(race, otb_data)
        race["_exacta_pay"] = ex
        race["_trifecta_pay"] = tri
        race["_superfecta_pay"] = sup
        if ex:
            matched += 1

    print(f"\nTotal races: {len(RACES)}")
    print(f"Races with exotic payouts: {matched}")

    type_counts = defaultdict(int)
    for r in RACES:
        type_counts[r["type"]] += 1
    print(f"By type: {dict(type_counts)}")

    days = sorted(set(r["day"] for r in RACES))
    print(f"Track-days: {len(days)}")
    for d in days:
        day_races = [r for r in RACES if r["day"] == d]
        with_ex = sum(1 for r in day_races if r.get("_exacta_pay"))
        print(f"  {d}: {len(day_races)} races ({with_ex} with exacta payouts)")

    # =====================================================
    # PATTERN ANALYSIS: Where do winners come from by ML rank?
    # =====================================================
    print("\n" + "=" * 120)
    print("PATTERN ANALYSIS: Winner ML Rank Distribution")
    print("=" * 120)

    rank_wins = defaultdict(int)
    rank_places = defaultdict(int)
    rank_combos = defaultdict(int)
    total_counted = 0

    for race in RACES:
        finish = race["finish"]
        if len(finish) < 2:
            continue
        total_counted += 1
        wr = get_ml_rank(race, finish[0])
        pr = get_ml_rank(race, finish[1])
        rank_wins[wr] += 1
        rank_places[pr] += 1
        rank_combos[(wr, pr)] += 1

    print(f"\nWinner by ML rank (n={total_counted}):")
    for rank in range(1, 8):
        pct = 100 * rank_wins.get(rank, 0) / total_counted
        print(f"  ML#{rank}: {rank_wins.get(rank, 0)} wins ({pct:.1f}%)")

    print(f"\n2nd place by ML rank:")
    for rank in range(1, 8):
        pct = 100 * rank_places.get(rank, 0) / total_counted
        print(f"  ML#{rank}: {rank_places.get(rank, 0)} places ({pct:.1f}%)")

    print(f"\nTop exacta combos (winner-placer by ML rank):")
    sorted_combos = sorted(rank_combos.items(), key=lambda x: x[1], reverse=True)
    for (wr, pr), count in sorted_combos[:15]:
        pct = 100 * count / total_counted
        print(f"  #{wr}-#{pr}: {count} ({pct:.1f}%)")

    # Only use races with exacta payouts for strategy testing
    races_with_ex = [r for r in RACES if r.get("_exacta_pay")]
    races_clm = [r for r in races_with_ex if r["type"] in ("CLM", "MC", "SOC")]

    print(f"\n\nRaces available for exacta testing: {len(races_with_ex)} (all types)")
    print(f"CLM/MC/SOC races with exacta data: {len(races_clm)}")

    # =====================================================
    # EXHAUSTIVE EXACTA STRATEGY SEARCH
    # =====================================================
    print("\n" + "=" * 120)
    print("EXHAUSTIVE EXACTA STRATEGY SEARCH ($1/combo)")
    print("=" * 120)

    all_results = []

    # Define combo generators
    def make_combos_fixed(combo_list):
        return lambda race: combo_list

    # Single combos
    single_combos = []
    for wr in range(1, 7):
        for pr in range(1, 7):
            if wr != pr:
                single_combos.append(((wr, pr), f"#{wr}-#{pr}"))

    # Test each single combo
    print("\n--- SINGLE EXACTA COMBOS ($1 each) ---")
    for combos, label in single_combos:
        for types_label, types in [("ALL", None), ("CLM/MC/SOC", ["CLM", "MC", "SOC"]), ("CLM", ["CLM"])]:
            r = test_exacta_strategy(races_with_ex, make_combos_fixed([combos]),
                                      bet_per_combo=1.0, race_types=types,
                                      name=f"Single {label} ({types_label})")
            if r["plays"] > 10:
                all_results.append(r)
                if r["roi"] > 0:
                    print_result(r)

    # Multi-combo strategies
    print("\n--- MULTI-COMBO EXACTA STRATEGIES ($1/combo) ---")

    combo_sets = [
        ("Fav-2nd + Fav-4th + 4th-Fav (CURRENT)", [(1,2), (1,4), (4,1)]),
        ("Fav-2nd + 2nd-Fav", [(1,2), (2,1)]),
        ("Fav on top w/ 2-3-4", [(1,2), (1,3), (1,4)]),
        ("Fav on top w/ 2-3-4-5", [(1,2), (1,3), (1,4), (1,5)]),
        ("Fav/2nd both ways", [(1,2), (2,1)]),
        ("Fav/3rd both ways", [(1,3), (3,1)]),
        ("Fav/4th both ways", [(1,4), (4,1)]),
        ("Fav w/ 2+3+4 both ways", [(1,2),(1,3),(1,4),(2,1),(3,1),(4,1)]),
        ("Top 2 both ways + Fav/4th both ways", [(1,2),(2,1),(1,4),(4,1)]),
        ("2nd on top w/ Fav + 3rd", [(2,1), (2,3)]),
        ("3rd on top w/ Fav + 2nd", [(3,1), (3,2)]),
        ("Non-fav on top w/ Fav", [(2,1),(3,1),(4,1),(5,1)]),
        ("Value: 3rd/4th top w/ 1st/2nd", [(3,1),(3,2),(4,1),(4,2)]),
        ("ALL top-4 combos (12)", list(permutations(range(1,5), 2))),
        ("ALL top-3 combos (6)", list(permutations(range(1,4), 2))),
        ("Fav-2+3 + 2-Fav + 3-Fav (4 combos)", [(1,2),(1,3),(2,1),(3,1)]),
        ("Fav-2+4 + 4-Fav (3 combos, ORIGINAL)", [(1,2),(1,4),(4,1)]),
        ("2nd-Fav + 2nd-3rd + 3rd-2nd", [(2,1),(2,3),(3,2)]),
        ("Top3 cross (6) + 4th-Fav", [(1,2),(1,3),(2,1),(2,3),(3,1),(3,2),(4,1)]),
        ("Fav-ANY (top 5)", [(1,2),(1,3),(1,4),(1,5)]),
        ("ANY-Fav (top 5)", [(2,1),(3,1),(4,1),(5,1)]),
        ("Fav w/ 2-6 top + underneath", [(1,2),(1,3),(1,4),(1,5),(1,6),(2,1),(3,1),(4,1),(5,1),(6,1)]),
    ]

    for label, combos in combo_sets:
        for types_label, types in [("ALL", None), ("CLM/MC/SOC", ["CLM", "MC", "SOC"]), ("CLM", ["CLM"])]:
            r = test_exacta_strategy(races_with_ex, make_combos_fixed(combos),
                                      bet_per_combo=1.0, race_types=types,
                                      name=f"{label} ({types_label})")
            if r["plays"] > 5:
                all_results.append(r)
                print_result(r, show_details=(r["roi"] > 20))

    # =====================================================
    # EXACTA BOX STRATEGIES
    # =====================================================
    print("\n--- EXACTA BOX STRATEGIES ---")

    def make_box_combos(n):
        """Box the top N ML picks."""
        def gen(race):
            return list(permutations(range(1, n+1), 2))
        return gen

    for n in [2, 3, 4, 5]:
        for types_label, types in [("ALL", None), ("CLM/MC/SOC", ["CLM", "MC", "SOC"]), ("CLM", ["CLM"])]:
            for bet in [0.5, 1.0, 2.0]:
                r = test_exacta_strategy(races_with_ex, make_box_combos(n),
                                          bet_per_combo=bet, race_types=types,
                                          name=f"Box top {n} @${bet} ({types_label})")
                if r["plays"] > 5:
                    all_results.append(r)
                    if r["roi"] > 0:
                        print_result(r, show_details=True)

    # =====================================================
    # TRIFECTA STRATEGIES
    # =====================================================
    print("\n" + "=" * 120)
    print("TRIFECTA STRATEGY SEARCH")
    print("=" * 120)

    races_with_tri = [r for r in RACES if r.get("_trifecta_pay")]
    print(f"Races with trifecta data: {len(races_with_tri)}")

    # Trifecta box of top N
    for n in [3, 4, 5]:
        def make_tri_box(n_val):
            def gen(race):
                return list(permutations(range(1, n_val+1), 3))
            return gen

        for types_label, types in [("ALL", None), ("CLM/MC/SOC", ["CLM", "MC", "SOC"]), ("CLM", ["CLM"])]:
            for bet in [0.5, 1.0]:
                for min_s in [0, 6, 8]:
                    r = test_trifecta_strategy(races_with_tri, make_tri_box(n),
                                                bet_per_combo=bet, race_types=types,
                                                min_starters=min_s,
                                                name=f"Tri box {n} @${bet} {min_s}+ ({types_label})")
                    if r["plays"] > 5:
                        all_results.append(r)
                        if r["roi"] > 0:
                            print_result(r)

    # Key trifecta (fav on top with top 4 underneath)
    def make_tri_key_fav(n_under):
        def gen(race):
            combos = []
            for p2 in range(2, n_under+1):
                for p3 in range(2, n_under+1):
                    if p2 != p3:
                        combos.append((1, p2, p3))
            return combos
        return gen

    print("\n--- TRIFECTA KEY (Fav on top) ---")
    for n in [4, 5, 6]:
        for types_label, types in [("ALL", None), ("CLM/MC/SOC", ["CLM", "MC", "SOC"])]:
            for bet in [0.5, 1.0]:
                r = test_trifecta_strategy(races_with_tri, make_tri_key_fav(n),
                                            bet_per_combo=bet, race_types=types,
                                            name=f"Tri key Fav/top{n} @${bet} ({types_label})")
                if r["plays"] > 5:
                    all_results.append(r)
                    if r["roi"] > 0:
                        print_result(r)

    # =====================================================
    # COMBINED STRATEGIES (Exacta + Trifecta)
    # =====================================================
    print("\n" + "=" * 120)
    print("COMBINED STRATEGIES")
    print("=" * 120)

    # Test combined: exacta singles + trifecta box on best races
    best_ex_combos = [(1,2), (1,4), (4,1)]  # Current strategy

    for ex_types, tri_types in [
        (["CLM","MC","SOC"], ["CLM","MC","SOC"]),
        (["CLM"], ["CLM"]),
        (None, None),
    ]:
        ex_r = test_exacta_strategy(races_with_ex, make_combos_fixed(best_ex_combos),
                                     bet_per_combo=1.0, race_types=ex_types,
                                     name="Ex: #1-2/#1-4/#4-1")
        tri_r = test_trifecta_strategy(races_with_tri, make_tri_box(4),
                                        bet_per_combo=0.5, race_types=tri_types,
                                        min_starters=7,
                                        name="Tri: box 4 @$0.50 7+")
        combo_w = ex_r["wagered"] + tri_r["wagered"]
        combo_r = ex_r["returned"] + tri_r["returned"]
        combo_net = combo_r - combo_w
        combo_roi = (combo_net / combo_w * 100) if combo_w > 0 else 0
        types_label = str(ex_types) if ex_types else "ALL"
        print(f"  Combined ({types_label}): W:${combo_w:.0f} R:${combo_r:.0f} "
              f"Net:${combo_net:+.0f} ROI:{combo_roi:+.1f}%")

    # =====================================================
    # FINAL RANKING
    # =====================================================
    print("\n" + "=" * 120)
    print("FINAL RANKING — All strategies sorted by ROI")
    print("=" * 120)

    # Filter to strategies with enough plays
    valid_results = [r for r in all_results if r["plays"] >= 10]
    valid_results.sort(key=lambda x: x["roi"], reverse=True)

    print("\nTOP 30 STRATEGIES:")
    for i, r in enumerate(valid_results[:30], 1):
        marker = " ***" if r["roi"] > 0 else ""
        print(f"  {i:2d}. {r['name']:<60s} ROI:{r['roi']:>+7.1f}% "
              f"Net:${r['net']:>+8.1f} Hit:{r['hits']}/{r['plays']}({r['hit_rate']:.0f}%) "
              f"Days:{r['profitable_days']}/{r['total_days']}{marker}")

    print("\nBOTTOM 10 STRATEGIES:")
    for i, r in enumerate(valid_results[-10:], 1):
        print(f"  {i:2d}. {r['name']:<60s} ROI:{r['roi']:>+7.1f}% "
              f"Net:${r['net']:>+8.1f} Hit:{r['hits']}/{r['plays']}({r['hit_rate']:.0f}%)")

    # Show the current strategy's performance
    print("\n" + "=" * 120)
    print("CURRENT STRATEGY PERFORMANCE (Fav-2nd + Fav-4th + 4th-Fav, CLM/MC/SOC)")
    print("=" * 120)

    current = test_exacta_strategy(races_with_ex,
                                    make_combos_fixed([(1,2),(1,4),(4,1)]),
                                    bet_per_combo=1.0,
                                    race_types=["CLM","MC","SOC"],
                                    name="CURRENT: #1-2/#1-4/#4-1 (CLM/MC/SOC)")
    print_result(current, show_details=True)

    # Day by day for current strategy
    print("\nDay-by-day:")
    if current.get("daily"):
        for day in sorted(current["daily"].keys()):
            d = current["daily"][day]
            net = d["r"] - d["w"]
            result = "WIN" if net > 0 else ("PUSH" if net == 0 else "LOSS")
            print(f"  {day}: W:${d['w']:.0f} R:${d['r']:.1f} Net:${net:+.1f} [{result}]")

    # =====================================================
    # THE HONEST TRUTH
    # =====================================================
    print("\n" + "=" * 120)
    print("THE HONEST TRUTH")
    print("=" * 120)

    profitable_strategies = [r for r in valid_results if r["roi"] > 0]
    losing_strategies = [r for r in valid_results if r["roi"] <= 0]

    print(f"\nStrategies tested: {len(valid_results)}")
    print(f"Profitable: {len(profitable_strategies)} ({100*len(profitable_strategies)/len(valid_results):.1f}%)")
    print(f"Losing: {len(losing_strategies)} ({100*len(losing_strategies)/len(valid_results):.1f}%)")

    if profitable_strategies:
        best = profitable_strategies[0]
        print(f"\nBEST STRATEGY FOUND:")
        print_result(best, show_details=True)
        print(f"\n  This strategy would cost ${best['wagered']/best['total_days']:.1f}/day "
              f"and return ${best['returned']/best['total_days']:.1f}/day "
              f"= ${best['net']/best['total_days']:+.1f}/day profit")

    # Save results
    output = {
        "total_races": len(RACES),
        "races_with_exotics": matched,
        "track_days": len(days),
        "strategies_tested": len(valid_results),
        "profitable_count": len(profitable_strategies),
        "top_20": [
            {"name": r["name"], "roi": round(r["roi"], 1), "net": round(r["net"], 1),
             "hits": r["hits"], "plays": r["plays"], "hit_rate": round(r["hit_rate"], 1),
             "wagered": round(r["wagered"], 1), "returned": round(r["returned"], 1),
             "profitable_days": r["profitable_days"], "total_days": r["total_days"]}
            for r in valid_results[:20]
        ],
    }

    output_path = os.path.join(SCRIPT_DIR, "definitive_backtest_results.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()
