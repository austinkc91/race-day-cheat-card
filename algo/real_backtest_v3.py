#!/usr/bin/env python3
"""
DEEP DIVE into the Cold Exacta strategy (the only profitable approach).
Theory: when the heavy favorite loses, exotics pay big. Focus capital there.
"""

from real_backtest import RACE_DATA, get_ml_top_n


def cold_exacta_detailed(races, key_positions, with_positions, bet=2.0, min_starters=7,
                          race_types=None, both_ways=True):
    """Detailed cold exacta analysis with per-race breakdown."""
    total_wagered = 0
    total_returned = 0
    daily = {}
    hits = []
    misses = []

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"wagered": 0, "returned": 0}

        if race["starters"] < min_starters:
            continue
        if race_types and race["type"] not in race_types:
            continue

        sorted_ml = sorted(race["ml_odds"].items(), key=lambda x: x[1])
        key = [sorted_ml[i][0] for i in key_positions if i < len(sorted_ml)]
        with_h = [sorted_ml[i][0] for i in with_positions if i < len(sorted_ml)]

        if len(key) < 1 or len(with_h) < 1:
            continue

        if both_ways:
            num_combos = len(key) * len(with_h) * 2
        else:
            num_combos = len(key) * len(with_h)
        cost = bet * num_combos
        total_wagered += cost
        daily[day]["wagered"] += cost

        finish = race["finish"]
        hit = False
        if len(finish) >= 2 and race.get("exacta_pay"):
            if both_ways:
                if (finish[0] in key and finish[1] in with_h) or \
                   (finish[0] in with_h and finish[1] in key):
                    hit = True
            else:
                if finish[0] in key and finish[1] in with_h:
                    hit = True

        if hit:
            payout = race["exacta_pay"] * (bet / 2.0)
            total_returned += payout
            daily[day]["returned"] += payout
            hits.append({
                "day": day, "race": race["race"],
                "winner": finish[0], "winner_ml": race["ml_odds"].get(finish[0], "?"),
                "second": finish[1], "second_ml": race["ml_odds"].get(finish[1], "?"),
                "exacta_pay": race["exacta_pay"], "our_return": payout,
                "cost": cost, "type": race["type"]
            })
        else:
            misses.append({
                "day": day, "race": race["race"],
                "winner": finish[0], "winner_ml": race["ml_odds"].get(finish[0], "?"),
                "second": finish[1] if len(finish) > 1 else "?",
                "exacta_pay": race.get("exacta_pay", 0),
                "cost": cost, "type": race["type"]
            })

    net = total_returned - total_wagered
    return {
        "wagered": total_wagered, "returned": total_returned, "net": net,
        "roi": (net / total_wagered * 100) if total_wagered > 0 else 0,
        "hits": hits, "misses": misses, "daily": daily,
        "hit_rate": len(hits) / (len(hits) + len(misses)) * 100 if (hits or misses) else 0,
        "days_profitable": sum(1 for d in daily.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily),
    }


print("=" * 70)
print("COLD EXACTA DEEP DIVE — The Only Profitable Strategy")
print("Theory: Bet AGAINST the favorite. When upsets happen, payoffs are big.")
print("=" * 70)

# Original winning strategy
print("\n>>> STRATEGY A: ML#2-3 keyed with ML#4-6 ($2 both ways, 7+ starters)")
r = cold_exacta_detailed(RACE_DATA, key_positions=[1,2], with_positions=[3,4,5], bet=2.0, min_starters=7)
print(f"  Wagered: ${r['wagered']:.0f} | Returned: ${r['returned']:.0f} | Net: ${r['net']:+.0f} | ROI: {r['roi']:+.1f}%")
print(f"  Hit rate: {r['hit_rate']:.0f}% ({len(r['hits'])}/{len(r['hits'])+len(r['misses'])})")
print(f"  Days profitable: {r['days_profitable']}/{r['total_days']}")
print(f"  Hits:")
for h in r["hits"]:
    print(f"    {h['day']} R{h['race']}: {h['winner']}({h['winner_ml']}/1) / {h['second']}({h['second_ml']}/1) "
          f"= ${h['exacta_pay']:.2f} posted, ${h['our_return']:.2f} return (cost ${h['cost']:.0f}) [{h['type']}]")
print(f"  Per-day:")
for day, d in sorted(r['daily'].items()):
    net = d['returned'] - d['wagered']
    print(f"    {day}: W${d['wagered']:.0f} R${d['returned']:.0f} Net${net:+.0f}")

# Variations
print("\n>>> STRATEGY B: ML#2-4 keyed with ML#5-7 ($1 both ways, 8+ starters)")
r2 = cold_exacta_detailed(RACE_DATA, key_positions=[1,2,3], with_positions=[4,5,6], bet=1.0, min_starters=8)
print(f"  Wagered: ${r2['wagered']:.0f} | Returned: ${r2['returned']:.0f} | Net: ${r2['net']:+.0f} | ROI: {r2['roi']:+.1f}%")
print(f"  Hit rate: {r2['hit_rate']:.0f}% ({len(r2['hits'])}/{len(r2['hits'])+len(r2['misses'])})")
print(f"  Days profitable: {r2['days_profitable']}/{r2['total_days']}")

print("\n>>> STRATEGY C: ML#1-3 keyed with ML#4-6 ($1 both ways, 7+ starters)")
r3 = cold_exacta_detailed(RACE_DATA, key_positions=[0,1,2], with_positions=[3,4,5], bet=1.0, min_starters=7)
print(f"  Wagered: ${r3['wagered']:.0f} | Returned: ${r3['returned']:.0f} | Net: ${r3['net']:+.0f} | ROI: {r3['roi']:+.1f}%")
print(f"  Hit rate: {r3['hit_rate']:.0f}% ({len(r3['hits'])}/{len(r3['hits'])+len(r3['misses'])})")
print(f"  Days profitable: {r3['days_profitable']}/{r3['total_days']}")

print("\n>>> STRATEGY D: ML#2-3 with ML#4-5 ($3 both ways, 7+ starters) — Fewer combos, bigger bets")
r4 = cold_exacta_detailed(RACE_DATA, key_positions=[1,2], with_positions=[3,4], bet=3.0, min_starters=7)
print(f"  Wagered: ${r4['wagered']:.0f} | Returned: ${r4['returned']:.0f} | Net: ${r4['net']:+.0f} | ROI: {r4['roi']:+.1f}%")
print(f"  Hit rate: {r4['hit_rate']:.0f}% ({len(r4['hits'])}/{len(r4['hits'])+len(r4['misses'])})")
print(f"  Days profitable: {r4['days_profitable']}/{r4['total_days']}")

print("\n>>> STRATEGY E: ML#2-3 with ML#3-6 ($1.50 both ways, 7+ starters) — Wider spread")
r5 = cold_exacta_detailed(RACE_DATA, key_positions=[1,2], with_positions=[2,3,4,5], bet=1.50, min_starters=7)
print(f"  Wagered: ${r5['wagered']:.0f} | Returned: ${r5['returned']:.0f} | Net: ${r5['net']:+.0f} | ROI: {r5['roi']:+.1f}%")
print(f"  Hit rate: {r5['hit_rate']:.0f}% ({len(r5['hits'])}/{len(r5['hits'])+len(r5['misses'])})")
print(f"  Days profitable: {r5['days_profitable']}/{r5['total_days']}")

# CLM races only (the supposed "goldmine")
print("\n>>> STRATEGY F: COLD EX on CLM only — ML#2-3 with ML#4-6 ($2, 7+ starters)")
r6 = cold_exacta_detailed(RACE_DATA, key_positions=[1,2], with_positions=[3,4,5], bet=2.0,
                            min_starters=7, race_types=["CLM"])
print(f"  Wagered: ${r6['wagered']:.0f} | Returned: ${r6['returned']:.0f} | Net: ${r6['net']:+.0f} | ROI: {r6['roi']:+.1f}%")
print(f"  Hit rate: {r6['hit_rate']:.0f}% ({len(r6['hits'])}/{len(r6['hits'])+len(r6['misses'])})")

# CLM + MC (claiming races)
print("\n>>> STRATEGY G: COLD EX on CLM+MC — ML#2-3 with ML#4-6 ($2, 7+ starters)")
r7 = cold_exacta_detailed(RACE_DATA, key_positions=[1,2], with_positions=[3,4,5], bet=2.0,
                            min_starters=7, race_types=["CLM", "MC"])
print(f"  Wagered: ${r7['wagered']:.0f} | Returned: ${r7['returned']:.0f} | Net: ${r7['net']:+.0f} | ROI: {r7['roi']:+.1f}%")
print(f"  Hit rate: {r7['hit_rate']:.0f}% ({len(r7['hits'])}/{len(r7['hits'])+len(r7['misses'])})")

# Now combine cold exacta with targeted trifecta
print("\n" + "=" * 70)
print("COMBINED STRATEGIES — Cold Exacta + Selective Trifecta")
print("=" * 70)


def combined_strategy(races, ex_key, ex_with, ex_bet, tri_top, tri_bet,
                      min_starters_ex=7, min_starters_tri=8):
    """Cold exacta + ML trifecta box."""
    total_wagered = 0
    total_returned = 0
    daily = {}

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"wagered": 0, "returned": 0}

        sorted_ml = sorted(race["ml_odds"].items(), key=lambda x: x[1])
        finish = race["finish"]

        # Cold exacta
        if race["starters"] >= min_starters_ex:
            key = [sorted_ml[i][0] for i in ex_key if i < len(sorted_ml)]
            with_h = [sorted_ml[i][0] for i in ex_with if i < len(sorted_ml)]
            num_combos = len(key) * len(with_h) * 2
            cost = ex_bet * num_combos
            total_wagered += cost
            daily[day]["wagered"] += cost

            if len(finish) >= 2 and race.get("exacta_pay"):
                if (finish[0] in key and finish[1] in with_h) or \
                   (finish[0] in with_h and finish[1] in key):
                    payout = race["exacta_pay"] * (ex_bet / 2.0)
                    total_returned += payout
                    daily[day]["returned"] += payout

        # Trifecta on big fields only
        if race["starters"] >= min_starters_tri and race.get("trifecta_pay"):
            top = [sorted_ml[i][0] for i in range(tri_top) if i < len(sorted_ml)]
            tri_combos = tri_top * (tri_top - 1) * (tri_top - 2)
            cost = tri_bet * tri_combos
            total_wagered += cost
            daily[day]["wagered"] += cost

            if len(finish) >= 3:
                if finish[0] in top and finish[1] in top and finish[2] in top:
                    payout = race["trifecta_pay"] * (tri_bet / 2.0)
                    total_returned += payout
                    daily[day]["returned"] += payout

    net = total_returned - total_wagered
    return {
        "wagered": total_wagered, "returned": total_returned, "net": net,
        "roi": (net / total_wagered * 100) if total_wagered > 0 else 0,
        "daily": daily,
        "days_profitable": sum(1 for d in daily.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily),
    }


combos = [
    ("COLD EX($2) + ML5 TRI($0.50, 9+)", [1,2], [3,4,5], 2.0, 5, 0.50, 7, 9),
    ("COLD EX($2) + ML4 TRI($0.50, 8+)", [1,2], [3,4,5], 2.0, 4, 0.50, 7, 8),
    ("COLD EX($2) + ML5 TRI($0.50, 8+)", [1,2], [3,4,5], 2.0, 5, 0.50, 7, 8),
    ("COLD EX($3) + ML4 TRI($1, 9+)", [1,2], [3,4], 3.0, 4, 1.0, 7, 9),
    ("COLD EX($2, 8+) + ML5 TRI($0.50, 9+)", [1,2], [3,4,5], 2.0, 5, 0.50, 8, 9),
]

for name, ek, ew, eb, tt, tb, mse, mst in combos:
    r = combined_strategy(RACE_DATA, ek, ew, eb, tt, tb, mse, mst)
    print(f"\n  {name}")
    print(f"  W${r['wagered']:.0f} R${r['returned']:.0f} Net${r['net']:+.0f} ROI:{r['roi']:+.1f}% | "
          f"Profitable: {r['days_profitable']}/{r['total_days']} days")
    for day, d in sorted(r['daily'].items()):
        net = d['returned'] - d['wagered']
        print(f"    {day}: W${d['wagered']:.0f} R${d['returned']:.0f} Net${net:+.0f}")


# Budget analysis
print("\n" + "=" * 70)
print("DAILY BUDGET ANALYSIS — Cold Exacta Strategy A")
print("=" * 70)
print("\nCold Exacta (ML#2-3 key with ML#4-6, $2 both ways, 7+ starters):")
print("  Cost per race: $2 x 2 key x 3 with x 2 ways = $24/race")
print("  Typical 10-race card with ~7 qualifying races: $168/day")
print("  Average daily P&L from backtest:")
for day, d in sorted(r["daily"].items()):  # Using last combo
    pass
r_a = cold_exacta_detailed(RACE_DATA, key_positions=[1,2], with_positions=[3,4,5], bet=2.0, min_starters=7)
avg_daily_wager = r_a["wagered"] / r_a["total_days"]
avg_daily_return = r_a["returned"] / r_a["total_days"]
print(f"  Avg daily wager: ${avg_daily_wager:.0f}")
print(f"  Avg daily return: ${avg_daily_return:.0f}")
print(f"  Avg daily P&L: ${avg_daily_return - avg_daily_wager:+.0f}")

# Reduced bet size ($1)
print("\n>>> STRATEGY A at $1/combo (halved risk):")
r_half = cold_exacta_detailed(RACE_DATA, key_positions=[1,2], with_positions=[3,4,5], bet=1.0, min_starters=7)
print(f"  W${r_half['wagered']:.0f} R${r_half['returned']:.0f} Net${r_half['net']:+.0f} ROI:{r_half['roi']:+.1f}%")
print(f"  Daily budget: ~${r_half['wagered']/r_half['total_days']:.0f}")
