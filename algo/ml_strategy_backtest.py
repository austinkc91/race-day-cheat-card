#!/usr/bin/env python3
"""
Morning Line Driven Strategy Backtester
========================================
Key insight: The track handicapper who sets morning lines watches workouts
and knows the horses. Top 4-5 by ML catches 60-100% of exactas.
Expert consensus catches only 30-40%.

This backtester tests ML-driven strategies against all available race data.
"""

import json
import os
import re

DATA_DIR = "/tmp/race_day_data"


def ml_val(h):
    ml = h.get('ml', '')
    if '/' in ml:
        parts = ml.split('/')
        try:
            return float(parts[0]) / float(parts[1])
        except:
            return 99
    try:
        return float(ml)
    except:
        return 99


def pick_count(h):
    p = h.get('picks', '0/0')
    try:
        return int(p.split('/')[0])
    except:
        return 0


def parse_payout(result_str, ptype):
    if not result_str:
        return 0
    patterns = {
        "exacta": r"Exacta.*?\$(\d+\.?\d*)",
        "trifecta": r"Trifecta.*?\$(\d+\.?\d*)",
        "superfecta": r"Super.*?\$(\d+\.?\d*)",
    }
    m = re.search(patterns.get(ptype, ""), result_str)
    return float(m.group(1)) if m else 0


def parse_win_payout(result_str):
    if not result_str:
        return 0
    m = re.search(r"\(\$(\d+\.?\d*)/", result_str)
    return float(m.group(1)) if m else 0


def load_race_day(filepath):
    with open(filepath) as f:
        data = json.load(f)

    races = []
    for r in data.get("races", []):
        if r.get("status") != "COMPLETED":
            continue
        horses = r.get("horses", [])
        if not horses:
            continue

        active = [h for h in horses if "SCR" not in h.get("name", "")]
        if len(active) < 3:
            continue  # Skip races with too few horses (biased data)

        winner_pp = place_pp = show_pp = fourth_pp = None
        for h in active:
            name = h.get("name", "")
            if "(WON)" in name:
                winner_pp = h["pp"]
            elif "(2nd)" in name:
                place_pp = h["pp"]
            elif "(3rd)" in name:
                show_pp = h["pp"]
            elif "(4th)" in name:
                fourth_pp = h["pp"]

        if winner_pp is None:
            continue

        result_str = r.get("result", "")
        races.append({
            "number": r["number"],
            "type": r.get("type", "OTH"),
            "starters": len(active),
            "horses": active,
            "winner_pp": winner_pp,
            "place_pp": place_pp,
            "show_pp": show_pp,
            "fourth_pp": fourth_pp,
            "win_payout": parse_win_payout(result_str),
            "exacta_payout": parse_payout(result_str, "exacta"),
            "trifecta_payout": parse_payout(result_str, "trifecta"),
            "superfecta_payout": parse_payout(result_str, "superfecta"),
        })

    return {
        "track": data.get("track", "Unknown"),
        "date": data.get("date", "Unknown"),
        "races": races,
    }


def select_horses_ml(horses, n):
    """Select top N horses by morning line odds (lowest = best)."""
    return sorted(horses, key=ml_val)[:n]


def select_horses_picks(horses, n):
    """Select top N horses by expert picks."""
    return sorted(horses, key=pick_count, reverse=True)[:n]


def select_horses_blend(horses, n_ml, n_picks):
    """Select unique union of top N by ML and top N by picks."""
    ml_set = set(h['pp'] for h in select_horses_ml(horses, n_ml))
    pick_set = set(h['pp'] for h in select_horses_picks(horses, n_picks))
    combined = ml_set | pick_set
    return [h for h in horses if h['pp'] in combined]


def run_strategy(race_day, config, verbose=False):
    """
    Run a betting strategy on a race day.

    Config keys:
    - exacta_method: "ml", "picks", "blend"
    - exacta_n: number of horses to box (for ml/picks)
    - exacta_ml_n: ML portion for blend
    - exacta_picks_n: picks portion for blend
    - exacta_bet: cost per combo
    - win_method: "ml_value", "picks_value", "both"
    - win_min_ml: minimum ML odds for win bet
    - win_bet: amount per win bet
    - win_max_per_race: max win bets per race
    - tri_method: "ml", "picks", "blend"
    - tri_n: number of horses for trifecta
    - tri_bet: cost per combo
    - tri_min_starters: min field size for tri
    - use_place: add place bets on strong picks
    - place_bet: amount per place bet
    """
    total_w = 0
    total_r = 0
    race_results = []

    for race in race_day["races"]:
        horses = race["horses"]
        rw = 0
        rr = 0
        details = []

        # ---- EXACTA BETS ----
        if config.get("exacta_method") == "ml":
            ex_horses = select_horses_ml(horses, config.get("exacta_n", 4))
        elif config.get("exacta_method") == "picks":
            ex_horses = select_horses_picks(horses, config.get("exacta_n", 3))
        elif config.get("exacta_method") == "blend":
            ex_horses = select_horses_blend(
                horses, config.get("exacta_ml_n", 3), config.get("exacta_picks_n", 2)
            )
        else:
            ex_horses = select_horses_ml(horses, 4)

        ex_pps = [h['pp'] for h in ex_horses]
        n_ex = len(ex_pps)
        ex_bet = config.get("exacta_bet", 1.0)
        ex_cost = n_ex * (n_ex - 1) * ex_bet
        rw += ex_cost

        if race["winner_pp"] in ex_pps and race["place_pp"] in ex_pps:
            payout = race["exacta_payout"] * ex_bet  # payout per $1 combo
            rr += payout
            details.append(f"  EXACTA HIT {ex_pps} = ${payout:.2f} (cost ${ex_cost:.2f})")
        else:
            details.append(f"  EXACTA MISS {ex_pps} (cost ${ex_cost:.2f})")

        # ---- WIN BETS ----
        win_method = config.get("win_method", "ml_value")
        win_min_ml = config.get("win_min_ml", 4.0)
        win_max_ml = config.get("win_max_ml", 12.0)
        win_bet = config.get("win_bet", 5.0)
        win_max = config.get("win_max_per_race", 2)
        win_min_picks = config.get("win_min_picks", 0)

        win_candidates = []
        for h in horses:
            mv = ml_val(h)
            pc = pick_count(h)
            if win_min_ml <= mv <= win_max_ml and pc >= win_min_picks:
                win_candidates.append(h)

        # Sort by ML (shorter odds = more likely to win)
        win_candidates.sort(key=ml_val)
        win_bets = win_candidates[:win_max]

        for h in win_bets:
            rw += win_bet
            if h['pp'] == race["winner_pp"]:
                payout = race["win_payout"] * (win_bet / 2.0)
                rr += payout
                details.append(f"  WIN HIT #{h['pp']} ({h['ml']}) = ${payout:.2f}")
            else:
                details.append(f"  WIN MISS #{h['pp']} ({h['ml']})")

        # ---- TRIFECTA BETS ----
        tri_min = config.get("tri_min_starters", 7)
        if race["starters"] >= tri_min and config.get("use_tri", True):
            tri_method = config.get("tri_method", "ml")
            tri_n = config.get("tri_n", 4)
            tri_bet = config.get("tri_bet", 0.50)

            if tri_method == "ml":
                tri_horses = select_horses_ml(horses, tri_n)
            elif tri_method == "blend":
                tri_horses = select_horses_blend(
                    horses, config.get("tri_ml_n", tri_n), config.get("tri_picks_n", 2)
                )
            else:
                tri_horses = select_horses_picks(horses, tri_n)

            tri_pps = [h['pp'] for h in tri_horses]
            n_tri = len(tri_pps)
            tri_cost = n_tri * (n_tri-1) * (n_tri-2) * tri_bet
            rw += tri_cost

            if (race["winner_pp"] in tri_pps and
                race["place_pp"] in tri_pps and
                race["show_pp"] in tri_pps):
                payout = race["trifecta_payout"] * tri_bet
                rr += payout
                details.append(f"  TRIFECTA HIT {tri_pps} = ${payout:.2f} (cost ${tri_cost:.2f})")
            else:
                details.append(f"  TRIFECTA MISS {tri_pps} (cost ${tri_cost:.2f})")

        # ---- PLACE BETS ----
        if config.get("use_place", False):
            place_bet = config.get("place_bet", 3.0)
            # Place bet on top ML pick
            top_ml = select_horses_ml(horses, 1)[0]
            rw += place_bet
            if top_ml['pp'] in [race["winner_pp"], race["place_pp"]]:
                # Estimate place payout as ~40% of win payout
                payout = max(2.20, race["win_payout"] * 0.5) * (place_bet / 2.0)
                rr += payout
                details.append(f"  PLACE HIT #{top_ml['pp']} ~${payout:.2f}")
            else:
                details.append(f"  PLACE MISS #{top_ml['pp']}")

        profit = rr - rw
        marker = "+" if profit > 0 else ""
        race_results.append({
            "race": race["number"],
            "type": race["type"],
            "starters": race["starters"],
            "wagered": rw,
            "returned": rr,
            "profit": profit,
            "details": details,
        })

        total_w += rw
        total_r += rr

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0

    if verbose:
        print(f"\n{race_day['track']} ({race_day['date']}):")
        for rr_item in race_results:
            marker = "+" if rr_item["profit"] > 0 else ""
            print(f"  R{rr_item['race']} ({rr_item['type']} {rr_item['starters']}st): "
                  f"W=${rr_item['wagered']:.0f} R=${rr_item['returned']:.0f} "
                  f"P/L {marker}${rr_item['profit']:.0f}")
            for d in rr_item["details"]:
                print(d)

    return {
        "wagered": total_w,
        "returned": total_r,
        "net": net,
        "roi": roi,
        "races": race_results,
    }


def main():
    # Load all race days
    race_days = []
    for f in ["parx.json", "fair-grounds.json"]:
        path = os.path.join(DATA_DIR, f)
        if os.path.exists(path):
            rd = load_race_day(path)
            if rd["races"]:
                race_days.append(rd)
                print(f"Loaded {rd['track']}: {len(rd['races'])} races (full field)")

    # Skip Oaklawn - only 3 horses per race = biased
    print("\nSkipping Oaklawn (only 3 horses per race in data = biased)")

    total_races = sum(len(rd["races"]) for rd in race_days)
    print(f"Total: {len(race_days)} days, {total_races} races with full fields\n")

    # ================================================================
    # STRATEGY CONFIGURATIONS TO TEST
    # ================================================================
    strategies = {
        # --- EXACTA APPROACHES ---
        "ML Top 4 Exacta Only": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 1.0,
            "win_method": None, "win_max_per_race": 0,
            "use_tri": False, "use_place": False,
        },
        "ML Top 5 Exacta Only": {
            "exacta_method": "ml", "exacta_n": 5, "exacta_bet": 1.0,
            "win_method": None, "win_max_per_race": 0,
            "use_tri": False, "use_place": False,
        },
        "ML Top 4 Exacta ($0.50)": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 0.50,
            "win_method": None, "win_max_per_race": 0,
            "use_tri": False, "use_place": False,
        },
        "Picks Top 3 Exacta Only": {
            "exacta_method": "picks", "exacta_n": 3, "exacta_bet": 1.0,
            "win_method": None, "win_max_per_race": 0,
            "use_tri": False, "use_place": False,
        },
        "Blend 3ML+2Picks Exacta": {
            "exacta_method": "blend", "exacta_ml_n": 3, "exacta_picks_n": 2, "exacta_bet": 1.0,
            "win_method": None, "win_max_per_race": 0,
            "use_tri": False, "use_place": False,
        },
        "Blend 4ML+2Picks Exacta": {
            "exacta_method": "blend", "exacta_ml_n": 4, "exacta_picks_n": 2, "exacta_bet": 1.0,
            "win_method": None, "win_max_per_race": 0,
            "use_tri": False, "use_place": False,
        },

        # --- ML EXACTA + WIN ---
        "ML4 Exacta + ML Win 4/1-10/1": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 1.0,
            "win_min_ml": 4.0, "win_max_ml": 10.0, "win_bet": 5.0,
            "win_max_per_race": 1, "win_min_picks": 0,
            "use_tri": False, "use_place": False,
        },
        "ML4 Exacta + ML Win 3/1-8/1": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 1.0,
            "win_min_ml": 3.0, "win_max_ml": 8.0, "win_bet": 5.0,
            "win_max_per_race": 1, "win_min_picks": 0,
            "use_tri": False, "use_place": False,
        },

        # --- ML EXACTA + TRIFECTA ---
        "ML4 Exacta + ML4 Tri (7+st)": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 1.0,
            "win_max_per_race": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": False,
        },
        "ML4 Exacta + ML5 Tri (7+st)": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 1.0,
            "win_max_per_race": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 5, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": False,
        },
        "ML5 Exacta + ML5 Tri (7+st)": {
            "exacta_method": "ml", "exacta_n": 5, "exacta_bet": 0.50,
            "win_max_per_race": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 5, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": False,
        },

        # --- FULL COMBO STRATEGIES ---
        "ML4 All-In (exacta+tri+win)": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 1.0,
            "win_min_ml": 4.0, "win_max_ml": 10.0, "win_bet": 5.0,
            "win_max_per_race": 1, "win_min_picks": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": False,
        },
        "ML5 Conservative ($0.50 bets)": {
            "exacta_method": "ml", "exacta_n": 5, "exacta_bet": 0.50,
            "win_min_ml": 5.0, "win_max_ml": 10.0, "win_bet": 3.0,
            "win_max_per_race": 1, "win_min_picks": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 5, "tri_bet": 0.20, "tri_min_starters": 7,
            "use_place": False,
        },
        "Blend Full (3ML+2P exacta, ML tri, ML win)": {
            "exacta_method": "blend", "exacta_ml_n": 3, "exacta_picks_n": 2, "exacta_bet": 1.0,
            "win_min_ml": 4.0, "win_max_ml": 10.0, "win_bet": 5.0,
            "win_max_per_race": 1, "win_min_picks": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": False,
        },

        # --- WITH PLACE BETS ---
        "ML4 Exacta + Place on #1 ML": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 1.0,
            "win_max_per_race": 0,
            "use_tri": False, "use_place": True, "place_bet": 4.0,
        },

        # --- SCALED UP (BUDGET ~$125/day) ---
        "ML4 Scaled ($2 exacta, $10 win, $1 tri)": {
            "exacta_method": "ml", "exacta_n": 4, "exacta_bet": 2.0,
            "win_min_ml": 4.0, "win_max_ml": 10.0, "win_bet": 10.0,
            "win_max_per_race": 1, "win_min_picks": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 4, "tri_bet": 1.0, "tri_min_starters": 7,
            "use_place": False,
        },
        "ML5 Scaled ($1 exacta, $8 win, $0.50 tri)": {
            "exacta_method": "ml", "exacta_n": 5, "exacta_bet": 1.0,
            "win_min_ml": 4.0, "win_max_ml": 10.0, "win_bet": 8.0,
            "win_max_per_race": 1, "win_min_picks": 0,
            "use_tri": True, "tri_method": "ml", "tri_n": 5, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": False,
        },
    }

    # Run all strategies
    print("=" * 90)
    print(f"{'Strategy':<45} {'Wagered':>8} {'Returned':>9} {'Net':>9} {'ROI':>7}")
    print("=" * 90)

    results = []
    for name, config in strategies.items():
        total_w = 0
        total_r = 0
        for rd in race_days:
            res = run_strategy(rd, config, verbose=False)
            total_w += res["wagered"]
            total_r += res["returned"]
        net = total_r - total_w
        roi = (net / total_w * 100) if total_w > 0 else 0
        marker = "+" if net > 0 else ""
        print(f"{name:<45} ${total_w:>7.0f} ${total_r:>8.0f} {marker}${net:>7.0f} {roi:>6.1f}%")
        results.append((name, config, total_w, total_r, net, roi))

    # Sort by ROI
    results.sort(key=lambda x: x[5], reverse=True)

    print(f"\n{'='*90}")
    print("TOP 5 STRATEGIES BY ROI:")
    print(f"{'='*90}")
    for i, (name, config, tw, tr, net, roi) in enumerate(results[:5]):
        marker = "+" if net > 0 else ""
        print(f"\n{i+1}. {name}")
        print(f"   Wagered: ${tw:.0f} | Returned: ${tr:.0f} | Net: {marker}${net:.0f} | ROI: {roi:.1f}%")
        print(f"   Daily avg: ~${tw/len(race_days):.0f} wagered, {marker}${net/len(race_days):.0f} profit")

    # Show detailed results for best strategy
    best_name, best_config = results[0][0], results[0][1]
    print(f"\n{'='*90}")
    print(f"DETAILED RESULTS: {best_name}")
    print(f"{'='*90}")

    for rd in race_days:
        run_strategy(rd, best_config, verbose=True)

    # Now find the BEST strategy per track to see consistency
    print(f"\n{'='*90}")
    print("PER-TRACK BREAKDOWN (top strategy):")
    print(f"{'='*90}")
    for rd in race_days:
        print(f"\n--- {rd['track']} ---")
        track_results = []
        for name, config, _, _, _, _ in results:
            res = run_strategy(rd, config, verbose=False)
            track_results.append((name, res))
        track_results.sort(key=lambda x: x[1]["roi"], reverse=True)
        for name, res in track_results[:3]:
            m = "+" if res["net"] > 0 else ""
            print(f"  {name}: W=${res['wagered']:.0f} R=${res['returned']:.0f} {m}${res['net']:.0f} ({res['roi']:.1f}%)")

    # Save best strategy
    best = results[0]
    output = {
        "winning_strategy": best[0],
        "config": best[1],
        "totals": {
            "wagered": best[2],
            "returned": best[3],
            "net": best[4],
            "roi": best[5],
        },
        "all_strategies_ranked": [
            {"name": name, "roi": roi, "net": net}
            for name, _, _, _, net, roi in results
        ],
    }

    with open("/home/austin/race-day-cheat-card/algo/ml_strategy_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to ml_strategy_results.json")


if __name__ == "__main__":
    main()
