#!/usr/bin/env python3
"""
PATTERN ANALYSIS — Dig into WHEN and WHY upsets happen.
Find narrow, high-edge situations to exploit.
"""

from deep_backtest import RACE_DATA, get_ml_sorted, get_ml_rank, get_competitiveness

import json

print("=" * 100)
print("PATTERN ANALYSIS — 43 races, finding where the money is")
print("=" * 100)

# ---- WINNER ANALYSIS ----
print("\n=== WHERE DO WINNERS COME FROM? ===")
ml_rank_wins = {}
for race in RACE_DATA:
    winner = race["finish"][0]
    rank = get_ml_rank(race, winner)
    ml_rank_wins[rank] = ml_rank_wins.get(rank, 0) + 1

print("ML Rank | Wins | %    | Avg Win Pay")
for rank in sorted(ml_rank_wins.keys()):
    # Calculate avg win pay for this rank
    payouts = []
    for race in RACE_DATA:
        winner = race["finish"][0]
        if get_ml_rank(race, winner) == rank:
            payouts.append(race.get("win_pay", 0))
    avg_pay = sum(payouts) / len(payouts) if payouts else 0
    count = ml_rank_wins[rank]
    pct = count / len(RACE_DATA) * 100
    print(f"   #{rank:2d}   | {count:3d}  | {pct:4.1f}% | ${avg_pay:.2f}")

# ---- EXACTA ANALYSIS ----
print("\n=== EXACTA: WHO FINISHES 1-2? ===")
exacta_patterns = {}
for race in RACE_DATA:
    if len(race["finish"]) < 2:
        continue
    r1 = get_ml_rank(race, race["finish"][0])
    r2 = get_ml_rank(race, race["finish"][1])
    key = f"#{r1}-#{r2}"
    if key not in exacta_patterns:
        exacta_patterns[key] = {"count": 0, "payouts": []}
    exacta_patterns[key]["count"] += 1
    if race.get("exacta_pay"):
        exacta_patterns[key]["payouts"].append(race["exacta_pay"])

print(f"{'Pattern':12s} | Count | Avg Exacta Pay ($2) | Break-even bet needed")
for key, val in sorted(exacta_patterns.items(), key=lambda x: -x[1]["count"]):
    avg_pay = sum(val["payouts"]) / len(val["payouts"]) if val["payouts"] else 0
    # Break-even: if you bet $X per combo and this pattern hits Y% of the time,
    # you need avg_pay * (X/$2) * hit_rate > cost
    print(f"{key:12s} | {val['count']:5d} | ${avg_pay:7.2f}            |")

# ---- TRIFECTA ANALYSIS ----
print("\n=== TRIFECTA: TOP 3 FINISH RANKS ===")
tri_patterns = {}
for race in RACE_DATA:
    if len(race["finish"]) < 3 or not race.get("trifecta_pay"):
        continue
    ranks = tuple(get_ml_rank(race, race["finish"][i]) for i in range(3))
    max_rank = max(ranks)
    bracket = "top4" if max_rank <= 4 else "top5" if max_rank <= 5 else "top6" if max_rank <= 6 else "top7" if max_rank <= 7 else "8+"
    if bracket not in tri_patterns:
        tri_patterns[bracket] = {"count": 0, "payouts": []}
    tri_patterns[bracket]["count"] += 1
    tri_patterns[bracket]["payouts"].append(race["trifecta_pay"])

print(f"{'Bracket':10s} | Count | % of tris | Avg Payout | Min    | Max")
total_tris = sum(v["count"] for v in tri_patterns.values())
for bracket in ["top4", "top5", "top6", "top7", "8+"]:
    if bracket in tri_patterns:
        v = tri_patterns[bracket]
        avg = sum(v["payouts"]) / len(v["payouts"])
        pct = v["count"] / total_tris * 100
        print(f"{bracket:10s} | {v['count']:5d} | {pct:7.1f}%  | ${avg:8.2f}  | ${min(v['payouts']):6.2f} | ${max(v['payouts']):8.2f}")

# ---- BIG PAYOUT ANALYSIS ----
print("\n=== BIGGEST PAYOUTS — What races produce them? ===")
big_payouts = []
for race in RACE_DATA:
    for bet_type, key in [("exacta", "exacta_pay"), ("trifecta", "trifecta_pay"), ("superfecta", "superfecta_pay")]:
        if race.get(key) and race[key] > 50:
            winner_rank = get_ml_rank(race, race["finish"][0])
            comp = get_competitiveness(race)
            fav_odds = min(race["ml_odds"].values())
            big_payouts.append({
                "day": race["day"], "race": race["race"], "type": race["type"],
                "starters": race["starters"], "bet": bet_type, "payout": race[key],
                "winner_rank": winner_rank, "fav_odds": fav_odds,
                "competitiveness": comp
            })

big_payouts.sort(key=lambda x: -x["payout"])
print(f"{'Day':15s} R# | Type | St | Bet       | Payout($2) | WinRank | FavOdds | Comp")
for p in big_payouts[:25]:
    print(f"{p['day']:15s} R{p['race']} | {p['type']:4s} | {p['starters']:2d} | {p['bet']:9s} | ${p['payout']:9.2f} | #{p['winner_rank']:2d}     | {p['fav_odds']:5.1f}/1 | {p['competitiveness']:.2f}")

# ---- VULNERABLE FAVORITE ANALYSIS ----
print("\n=== WHEN DO FAVORITES LOSE? ===")
fav_wins = 0
fav_losses = 0
fav_loss_details = []
for race in RACE_DATA:
    fav = get_ml_sorted(race)[0]
    fav_name = fav[0]
    fav_odds = fav[1]
    if race["finish"][0] == fav_name:
        fav_wins += 1
    else:
        fav_losses += 1
        fav_loss_details.append({
            "day": race["day"], "race": race["race"], "type": race["type"],
            "starters": race["starters"], "fav_odds": fav_odds,
            "winner_odds": race["ml_odds"].get(race["finish"][0], 99),
            "winner": race["finish"][0],
            "comp": get_competitiveness(race),
            "exacta_pay": race.get("exacta_pay", 0),
            "trifecta_pay": race.get("trifecta_pay", 0),
        })

print(f"Favorite wins: {fav_wins}/{len(RACE_DATA)} ({fav_wins/len(RACE_DATA)*100:.1f}%)")
print(f"Favorite loses: {fav_losses}/{len(RACE_DATA)} ({fav_losses/len(RACE_DATA)*100:.1f}%)")

print(f"\nWhen fav loses — where does the winner come from?")
for d in sorted(fav_loss_details, key=lambda x: -(x.get("trifecta_pay") or 0)):
    print(f"  {d['day']:15s} R{d['race']} {d['type']:4s} {d['starters']}st | "
          f"Fav={d['fav_odds']}/1 Lost | Winner={d['winner'][:15]:15s} ML={d['winner_odds']}/1 | "
          f"Comp={d['comp']:.2f} | ExPay=${d['exacta_pay']:6.1f} TriPay=${d['trifecta_pay']:7.1f}")

# ---- RACE TYPE PROFITABILITY ----
print("\n=== RACE TYPE: FAVORITE WIN RATE ===")
by_type = {}
for race in RACE_DATA:
    rt = race["type"]
    if rt not in by_type:
        by_type[rt] = {"total": 0, "fav_wins": 0, "avg_tri_pay": [], "avg_ex_pay": []}
    by_type[rt]["total"] += 1
    fav = get_ml_sorted(race)[0][0]
    if race["finish"][0] == fav:
        by_type[rt]["fav_wins"] += 1
    if race.get("trifecta_pay"):
        by_type[rt]["avg_tri_pay"].append(race["trifecta_pay"])
    if race.get("exacta_pay"):
        by_type[rt]["avg_ex_pay"].append(race["exacta_pay"])

print(f"{'Type':5s} | Races | Fav Win% | Avg Ex Pay | Avg Tri Pay")
for rt, v in sorted(by_type.items(), key=lambda x: -x[1]["total"]):
    fav_pct = v["fav_wins"] / v["total"] * 100
    avg_ex = sum(v["avg_ex_pay"]) / len(v["avg_ex_pay"]) if v["avg_ex_pay"] else 0
    avg_tri = sum(v["avg_tri_pay"]) / len(v["avg_tri_pay"]) if v["avg_tri_pay"] else 0
    print(f"{rt:5s} | {v['total']:5d} | {fav_pct:6.1f}%  | ${avg_ex:8.2f} | ${avg_tri:9.2f}")

# ---- FIELD SIZE ANALYSIS ----
print("\n=== FIELD SIZE: FAVORITE WIN RATE + AVG PAYOUTS ===")
by_size = {}
for race in RACE_DATA:
    s = race["starters"]
    if s not in by_size:
        by_size[s] = {"total": 0, "fav_wins": 0, "ex_pays": [], "tri_pays": [], "super_pays": []}
    by_size[s]["total"] += 1
    fav = get_ml_sorted(race)[0][0]
    if race["finish"][0] == fav:
        by_size[s]["fav_wins"] += 1
    if race.get("exacta_pay"):
        by_size[s]["ex_pays"].append(race["exacta_pay"])
    if race.get("trifecta_pay"):
        by_size[s]["tri_pays"].append(race["trifecta_pay"])
    if race.get("superfecta_pay"):
        by_size[s]["super_pays"].append(race["superfecta_pay"])

print(f"Size | Races | Fav% | Avg Ex   | Avg Tri    | Avg Super")
for s in sorted(by_size.keys()):
    v = by_size[s]
    fav_pct = v["fav_wins"] / v["total"] * 100
    avg_ex = sum(v["ex_pays"]) / len(v["ex_pays"]) if v["ex_pays"] else 0
    avg_tri = sum(v["tri_pays"]) / len(v["tri_pays"]) if v["tri_pays"] else 0
    avg_super = sum(v["super_pays"]) / len(v["super_pays"]) if v["super_pays"] else 0
    print(f"  {s:2d}  | {v['total']:5d} | {fav_pct:4.0f}% | ${avg_ex:7.2f} | ${avg_tri:9.2f} | ${avg_super:10.2f}")

# ---- ULTRA-SELECTIVE: What if we only bet the most profitable situations? ----
print("\n=== ULTRA-SELECTIVE STRATEGY ANALYSIS ===")
print("Scenario: What if we ONLY bet trifectas in CLM races with 8+ starters?")
clm_big = [r for r in RACE_DATA if r["type"] == "CLM" and r["starters"] >= 8 and r.get("trifecta_pay")]
print(f"  Qualifying races: {len(clm_big)}")
for r in clm_big:
    ranks = [get_ml_rank(r, r["finish"][i]) for i in range(min(3, len(r["finish"])))]
    print(f"  {r['day']} R{r['race']}: {r['starters']}st, Tri=${r['trifecta_pay']:.2f}, Top3 ranks: {ranks}")

print("\nScenario: CLM/MC 8+ starters, trifecta ML top 6")
for r in RACE_DATA:
    if r["type"] not in ["CLM", "MC"] or r["starters"] < 8 or not r.get("trifecta_pay"):
        continue
    top6 = get_ml_top_n(r)
    from deep_backtest import get_ml_top_n
    top6 = get_ml_top_n(r, 6)
    finish3 = r["finish"][:3]
    hit = all(f in top6 for f in finish3)
    cost_50 = 120 * 0.50  # 6*5*4 combos at $0.50
    payout_50 = r["trifecta_pay"] * 0.25 if hit else 0
    net = payout_50 - cost_50
    marker = "HIT" if hit else "miss"
    print(f"  {r['day']} R{r['race']}: {r['starters']}st, cost=${cost_50:.0f}, pay=${payout_50:.1f}, net=${net:+.1f} [{marker}]")


# ---- MATHEMATICAL EDGE FINDER ----
print("\n=== MATHEMATICAL EDGE: Where does payout exceed expected cost? ===")
print("For each race, calculate: if we bet $0.50 trifecta box ML top 5,")
print("what's the expected value = hit_probability * payout - cost?")
print("(Using historical hit rate of 48% for ML5 tri box in 7+ fields)")

# But we need to be more nuanced — what makes certain races MORE likely to produce
# a top-5 trifecta hit AND pay well?

# Key insight: The payout matters more than the hit rate.
# A race that pays $2661 tri (Parx Mar 17 R6) makes up for 20+ misses.
# We need to identify races most likely to produce BIG payouts when they hit.

print("\n=== BOMB DETECTOR: What predicts big exotic payouts? ===")
for race in RACE_DATA:
    if not race.get("trifecta_pay"):
        continue

    fav_odds = min(race["ml_odds"].values())
    second_odds = sorted(race["ml_odds"].values())[1] if len(race["ml_odds"]) > 1 else 0
    comp = get_competitiveness(race)
    spread = max(race["ml_odds"].values()) - min(race["ml_odds"].values())

    tri_pay = race["trifecta_pay"]
    is_big = "BIG$$$" if tri_pay > 100 else "small "

    print(f"  {is_big} ${tri_pay:8.2f} | {race['day']:15s} R{race['race']} {race['type']:4s} "
          f"| {race['starters']}st | Fav={fav_odds}/1 | 2nd={second_odds}/1 | Comp={comp:.2f} | Spread={spread:.0f}")
