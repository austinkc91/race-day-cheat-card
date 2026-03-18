#!/usr/bin/env python3
"""
Final Strategy Optimization
============================
Key discovery: Morning Line (ML) odds are far better than expert consensus
for selecting exotic bet horses. Top 4-5 by ML catches 60-100% of exactas
vs 30-40% for expert picks.

This tests budget-constrained ML-driven strategies around $125/day.
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
        if len(active) < 4:
            continue

        winner_pp = place_pp = show_pp = fourth_pp = None
        for h in active:
            name = h.get("name", "")
            if "(WON)" in name: winner_pp = h["pp"]
            elif "(2nd)" in name: place_pp = h["pp"]
            elif "(3rd)" in name: show_pp = h["pp"]
            elif "(4th)" in name: fourth_pp = h["pp"]

        if winner_pp is None:
            continue
        result_str = r.get("result", "")
        races.append({
            "number": r["number"], "type": r.get("type", "OTH"),
            "starters": len(active), "horses": active,
            "winner_pp": winner_pp, "place_pp": place_pp,
            "show_pp": show_pp, "fourth_pp": fourth_pp,
            "win_payout": parse_win_payout(result_str),
            "exacta_payout": parse_payout(result_str, "exacta"),
            "trifecta_payout": parse_payout(result_str, "trifecta"),
            "superfecta_payout": parse_payout(result_str, "superfecta"),
        })
    return {"track": data.get("track", "Unknown"), "date": data.get("date", "Unknown"), "races": races}


def run_strategy(race_day, config, verbose=False):
    total_w = 0
    total_r = 0
    race_details = []

    for race in race_day["races"]:
        horses = race["horses"]
        rw = rr = 0
        details = []
        by_ml = sorted(horses, key=ml_val)

        # EXACTA
        ex_n = config.get("exacta_n", 4)
        ex_bet = config.get("exacta_bet", 1.0)
        # If field is small (<= ex_n), reduce to field-1
        actual_ex_n = min(ex_n, len(horses))
        ex_pps = [h['pp'] for h in by_ml[:actual_ex_n]]
        ex_cost = actual_ex_n * (actual_ex_n - 1) * ex_bet
        rw += ex_cost

        if race["winner_pp"] in ex_pps and race["place_pp"] in ex_pps:
            payout = race["exacta_payout"] * ex_bet
            rr += payout
            details.append(f"  EX HIT {ex_pps} ${payout:.0f} (cost ${ex_cost:.0f})")
        else:
            details.append(f"  EX MISS {ex_pps} (cost ${ex_cost:.0f})")

        # TRIFECTA
        tri_min = config.get("tri_min_starters", 7)
        if config.get("use_tri", False) and race["starters"] >= tri_min and race["show_pp"]:
            tri_n = min(config.get("tri_n", 4), len(horses))
            tri_bet = config.get("tri_bet", 0.50)
            tri_pps = [h['pp'] for h in by_ml[:tri_n]]
            tri_cost = tri_n * (tri_n-1) * (tri_n-2) * tri_bet
            rw += tri_cost

            if (race["winner_pp"] in tri_pps and race["place_pp"] in tri_pps
                and race["show_pp"] in tri_pps):
                payout = race["trifecta_payout"] * tri_bet
                rr += payout
                details.append(f"  TRI HIT {tri_pps} ${payout:.0f} (cost ${tri_cost:.0f})")
            else:
                details.append(f"  TRI MISS {tri_pps} (cost ${tri_cost:.0f})")

        # WIN BETS
        if config.get("use_win", False):
            win_min = config.get("win_min_ml", 4.0)
            win_max = config.get("win_max_ml", 10.0)
            win_bet = config.get("win_bet", 5.0)
            win_n = config.get("win_max", 1)
            candidates = [h for h in by_ml if win_min <= ml_val(h) <= win_max][:win_n]
            for h in candidates:
                rw += win_bet
                if h['pp'] == race["winner_pp"]:
                    payout = race["win_payout"] * (win_bet / 2.0)
                    rr += payout
                    details.append(f"  WIN HIT #{h['pp']} ${payout:.0f}")
                else:
                    details.append(f"  WIN MISS #{h['pp']} ({h['ml']})")

        # PLACE BETS
        if config.get("use_place", False):
            place_bet = config.get("place_bet", 3.0)
            place_n = config.get("place_n", 1)
            for h in by_ml[:place_n]:
                rw += place_bet
                if h['pp'] in [race["winner_pp"], race["place_pp"]]:
                    est_payout = max(2.20, race["win_payout"] * 0.45) * (place_bet / 2.0)
                    rr += est_payout
                    details.append(f"  PLC HIT #{h['pp']} ~${est_payout:.0f}")
                else:
                    details.append(f"  PLC MISS #{h['pp']}")

        # SHOW BETS
        if config.get("use_show", False):
            show_bet = config.get("show_bet", 2.0)
            for h in by_ml[:1]:
                rw += show_bet
                if h['pp'] in [race["winner_pp"], race["place_pp"], race["show_pp"]]:
                    est_payout = max(2.10, race["win_payout"] * 0.3) * (show_bet / 2.0)
                    rr += est_payout
                    details.append(f"  SHW HIT #{h['pp']} ~${est_payout:.0f}")
                else:
                    details.append(f"  SHW MISS #{h['pp']}")

        profit = rr - rw
        race_details.append({
            "race": race["number"], "type": race["type"],
            "starters": race["starters"], "wagered": rw,
            "returned": rr, "profit": profit, "details": details,
        })
        total_w += rw
        total_r += rr

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0

    if verbose:
        print(f"\n{race_day['track']} ({race_day['date']}):")
        for rd in race_details:
            m = "+" if rd["profit"] > 0 else ""
            print(f"  R{rd['race']} ({rd['type']} {rd['starters']}st): "
                  f"W${rd['wagered']:.0f} R${rd['returned']:.0f} {m}${rd['profit']:.0f}")
            for d in rd["details"]:
                print(d)
        m = "+" if net > 0 else ""
        print(f"  TOTAL: W${total_w:.0f} R${total_r:.0f} {m}${net:.0f} ({roi:.1f}%)")

    return {"wagered": total_w, "returned": total_r, "net": net, "roi": roi}


def main():
    race_days = []
    for f in ["parx.json", "fair-grounds.json"]:
        path = os.path.join(DATA_DIR, f)
        if os.path.exists(path):
            rd = load_race_day(path)
            if rd["races"]:
                race_days.append(rd)
                print(f"Loaded {rd['track']}: {len(rd['races'])} races")

    print(f"Total: {sum(len(r['races']) for r in race_days)} races\n")

    # Budget-targeted strategies around $100-150/day
    strategies = {
        # === CORE: ML5 Exacta - the discovery ===
        "A: ML5 $0.50 Exacta (~$100/day)": {
            "exacta_n": 5, "exacta_bet": 0.50,
        },
        "B: ML5 $1 Exacta (~$200/day)": {
            "exacta_n": 5, "exacta_bet": 1.0,
        },
        "C: ML4 $1 Exacta (~$120/day)": {
            "exacta_n": 4, "exacta_bet": 1.0,
        },

        # === ML Exacta + Trifecta ===
        "D: ML4 $1 EX + ML4 $0.50 TRI 7+": {
            "exacta_n": 4, "exacta_bet": 1.0,
            "use_tri": True, "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
        },
        "E: ML5 $0.50 EX + ML4 $0.50 TRI 7+": {
            "exacta_n": 5, "exacta_bet": 0.50,
            "use_tri": True, "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
        },
        "F: ML5 $0.50 EX + ML5 $0.50 TRI 7+": {
            "exacta_n": 5, "exacta_bet": 0.50,
            "use_tri": True, "tri_n": 5, "tri_bet": 0.50, "tri_min_starters": 7,
        },
        "G: ML4 $1 EX + ML5 $0.50 TRI 6+": {
            "exacta_n": 4, "exacta_bet": 1.0,
            "use_tri": True, "tri_n": 5, "tri_bet": 0.50, "tri_min_starters": 6,
        },

        # === Add Place bets for consistent returns ===
        "H: ML5 $0.50 EX + $3 PLC #1 ML": {
            "exacta_n": 5, "exacta_bet": 0.50,
            "use_place": True, "place_bet": 3.0, "place_n": 1,
        },
        "I: ML4 $1 EX + $4 PLC #1 ML + ML4 TRI": {
            "exacta_n": 4, "exacta_bet": 1.0,
            "use_tri": True, "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": True, "place_bet": 4.0, "place_n": 1,
        },
        "J: ML5 $0.50 EX + $3 PLC top2 + ML4 TRI": {
            "exacta_n": 5, "exacta_bet": 0.50,
            "use_tri": True, "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": True, "place_bet": 3.0, "place_n": 2,
        },

        # === Add Show bets (highest hit rate) ===
        "K: ML4 $1 EX + $4 SHW #1 ML + ML4 TRI": {
            "exacta_n": 4, "exacta_bet": 1.0,
            "use_tri": True, "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_show": True, "show_bet": 4.0,
        },

        # === Win bets targeting ML value zone ===
        "L: ML4 EX + $5 WIN 4/1-8/1 + ML4 TRI": {
            "exacta_n": 4, "exacta_bet": 1.0,
            "use_win": True, "win_min_ml": 4.0, "win_max_ml": 8.0, "win_bet": 5.0, "win_max": 1,
            "use_tri": True, "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
        },
        "M: ML5 EX + $5 WIN 5/1-12/1 + ML5 TRI": {
            "exacta_n": 5, "exacta_bet": 0.50,
            "use_win": True, "win_min_ml": 5.0, "win_max_ml": 12.0, "win_bet": 5.0, "win_max": 1,
            "use_tri": True, "tri_n": 5, "tri_bet": 0.20, "tri_min_starters": 7,
        },

        # === Optimized combo ===
        "N: ML5 $0.50 EX + ML4 $0.50 TRI + $3 PLC": {
            "exacta_n": 5, "exacta_bet": 0.50,
            "use_tri": True, "tri_n": 4, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": True, "place_bet": 3.0, "place_n": 1,
        },
        "O: ML5 $0.50 EX + ML4 $1 TRI 8+ + $3 SHW": {
            "exacta_n": 5, "exacta_bet": 0.50,
            "use_tri": True, "tri_n": 4, "tri_bet": 1.0, "tri_min_starters": 8,
            "use_show": True, "show_bet": 3.0,
        },

        # === The Sweet Spot ===
        "P: ML5 $1 EX + ML4 $1 TRI 7+": {
            "exacta_n": 5, "exacta_bet": 1.0,
            "use_tri": True, "tri_n": 4, "tri_bet": 1.0, "tri_min_starters": 7,
        },
        "Q: ML5 $1 EX + ML5 $0.50 TRI 7+ + $3 PLC": {
            "exacta_n": 5, "exacta_bet": 1.0,
            "use_tri": True, "tri_n": 5, "tri_bet": 0.50, "tri_min_starters": 7,
            "use_place": True, "place_bet": 3.0, "place_n": 1,
        },
    }

    print("=" * 95)
    print(f"{'Strategy':<50} {'W/Day':>7} {'R/Day':>7} {'Net/Day':>8} {'ROI':>7} {'Win%':>5}")
    print("=" * 95)

    results = []
    n_days = len(race_days)

    for name, config in strategies.items():
        tw = tr = 0
        days_profitable = 0
        for rd in race_days:
            res = run_strategy(rd, config)
            tw += res["wagered"]
            tr += res["returned"]
            if res["net"] > 0:
                days_profitable += 1

        net = tr - tw
        roi = (net / tw * 100) if tw > 0 else 0
        per_day_w = tw / n_days
        per_day_r = tr / n_days
        per_day_net = net / n_days
        win_pct = days_profitable / n_days * 100

        m = "+" if net > 0 else ""
        print(f"{name:<50} ${per_day_w:>5.0f} ${per_day_r:>5.0f} {m}${per_day_net:>6.0f} {roi:>6.1f}% {win_pct:>4.0f}%")
        results.append((name, config, tw, tr, net, roi, per_day_w, win_pct))

    results.sort(key=lambda x: x[5], reverse=True)

    print(f"\n{'='*95}")
    print("TOP 5 STRATEGIES:")
    print(f"{'='*95}")
    for i, (name, config, tw, tr, net, roi, dpw, wp) in enumerate(results[:5]):
        m = "+" if net > 0 else ""
        print(f"\n{i+1}. {name}")
        print(f"   Total: W${tw:.0f} R${tr:.0f} {m}${net:.0f} ({roi:.1f}% ROI)")
        print(f"   Daily: ~${dpw:.0f}/day, {m}${net/n_days:.0f}/day, {wp:.0f}% days profitable")

    # Detailed output for top 3
    for i in range(min(3, len(results))):
        name, config = results[i][0], results[i][1]
        print(f"\n{'='*95}")
        print(f"#{i+1}: {name}")
        print(f"{'='*95}")
        for rd in race_days:
            run_strategy(rd, config, verbose=True)

    # Final recommendation
    best = results[0]
    print(f"\n{'='*95}")
    print("FINAL RECOMMENDATION")
    print(f"{'='*95}")
    print(f"Strategy: {best[0]}")
    print(f"ROI: {best[5]:.1f}%")
    print(f"Daily budget: ~${best[6]:.0f}")
    print(f"Daily profit: +${best[4]/n_days:.0f}")
    print(f"Win rate: {best[7]:.0f}% of days profitable")
    print(f"\nConfig: {json.dumps(best[1], indent=2)}")

    # Save
    output = {
        "recommendation": best[0],
        "config": best[1],
        "roi": round(best[5], 2),
        "daily_budget": round(best[6], 0),
        "daily_profit": round(best[4]/n_days, 0),
        "all_ranked": [
            {"name": n, "roi": round(r, 1), "daily_spend": round(d, 0), "win_pct": round(w, 0)}
            for n, _, _, _, _, r, d, w in results
        ],
    }
    with open("/home/austin/race-day-cheat-card/algo/final_strategy_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to final_strategy_results.json")


if __name__ == "__main__":
    main()
