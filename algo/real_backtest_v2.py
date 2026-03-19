#!/usr/bin/env python3
"""
HONEST backtest v2 — Testing alternative approaches to find a winning edge.
Focus on reducing cost and being more selective.
"""

from real_backtest import RACE_DATA, get_ml_top_n, print_results
import itertools


def test_keyed_exacta(races, key_n=1, with_n=4, bet_per_combo=1.0, min_starters=7):
    """KEY the top ML horse on top, box underneath horses.
    Much cheaper than full box: key_n * with_n combos instead of n*(n-1).
    """
    total_wagered = 0
    total_returned = 0
    daily = {}
    hits = 0
    total = 0

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"wagered": 0, "returned": 0}

        if race["starters"] < min_starters:
            continue

        ml_top = get_ml_top_n(race, key_n + with_n)
        key_horses = ml_top[:key_n]
        with_horses = ml_top[key_n:key_n + with_n]
        finish = race["finish"]

        # KEY on top: key horse in 1st, any with_horse in 2nd
        # Also KEY on bottom: any with_horse in 1st, key horse in 2nd
        num_combos = key_n * with_n * 2  # top and bottom
        cost = bet_per_combo * num_combos
        total_wagered += cost
        daily[day]["wagered"] += cost
        total += 1

        if len(finish) >= 2 and race.get("exacta_pay"):
            # Check: key on top (key=1st, with=2nd) OR key on bottom (with=1st, key=2nd)
            if (finish[0] in key_horses and finish[1] in with_horses) or \
               (finish[0] in with_horses and finish[1] in key_horses):
                payout = race["exacta_pay"] * (bet_per_combo / 2.0)
                total_returned += payout
                daily[day]["returned"] += payout
                hits += 1

    net = total_returned - total_wagered
    return {
        "total_wagered": total_wagered, "total_returned": total_returned,
        "net": net, "roi": (net / total_wagered * 100) if total_wagered > 0 else 0,
        "ex_hits": hits, "ex_total": total, "ex_rate": hits/total*100 if total else 0,
        "tri_hits": 0, "tri_total": 0, "tri_rate": 0,
        "show_hits": 0, "show_total": 0, "show_rate": 0,
        "daily": daily,
        "days_profitable": sum(1 for d in daily.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily),
    }


def test_value_exacta(races, ml_range=(3, 12), bet_amount=2.0, min_starters=7):
    """Only play exactas when there's value: skip heavy chalk races.
    Key ML#1 with value horses in the 3/1-12/1 ML range.
    """
    total_wagered = 0
    total_returned = 0
    daily = {}
    hits = 0
    total = 0

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"wagered": 0, "returned": 0}

        if race["starters"] < min_starters:
            continue

        sorted_ml = sorted(race["ml_odds"].items(), key=lambda x: x[1])
        ml1_horse = sorted_ml[0][0]
        ml1_odds = sorted_ml[0][1]

        # Skip if favorite is too short (heavy chalk = low payout)
        if ml1_odds < 2:
            continue

        # Get value horses in the specified range
        value_horses = [h for h, o in sorted_ml[1:] if ml_range[0] <= o <= ml_range[1]]
        if len(value_horses) < 2:
            continue

        # Key ML#1 with value horses (both ways)
        num_combos = len(value_horses) * 2  # key on top + bottom
        cost = bet_amount * num_combos
        total_wagered += cost
        daily[day]["wagered"] += cost
        total += 1

        finish = race["finish"]
        if len(finish) >= 2 and race.get("exacta_pay"):
            if (finish[0] == ml1_horse and finish[1] in value_horses) or \
               (finish[0] in value_horses and finish[1] == ml1_horse):
                payout = race["exacta_pay"] * (bet_amount / 2.0)
                total_returned += payout
                daily[day]["returned"] += payout
                hits += 1

    net = total_returned - total_wagered
    return {
        "total_wagered": total_wagered, "total_returned": total_returned,
        "net": net, "roi": (net / total_wagered * 100) if total_wagered > 0 else 0,
        "ex_hits": hits, "ex_total": total, "ex_rate": hits/total*100 if total else 0,
        "tri_hits": 0, "tri_total": 0, "tri_rate": 0,
        "show_hits": 0, "show_total": 0, "show_rate": 0,
        "daily": daily,
        "days_profitable": sum(1 for d in daily.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily),
    }


def test_upset_tri(races, tri_top_n=5, bet=0.50, min_starters=8, min_ml_spread=3):
    """Only play trifectas when field is competitive (spread in ML odds).
    The theory: trifectas only pay well when the field is wide open.
    """
    total_wagered = 0
    total_returned = 0
    daily = {}
    hits = 0
    total = 0

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"wagered": 0, "returned": 0}

        if race["starters"] < min_starters:
            continue
        if not race.get("trifecta_pay"):
            continue

        sorted_ml = sorted(race["ml_odds"].items(), key=lambda x: x[1])
        # ML spread: difference between #1 and #5 ML odds
        if len(sorted_ml) < tri_top_n:
            continue
        ml_spread = sorted_ml[tri_top_n - 1][1] - sorted_ml[0][1]

        if ml_spread < min_ml_spread:
            continue  # Skip races where top 5 are too bunched (low payouts)

        top = [h for h, o in sorted_ml[:tri_top_n]]
        tri_combos = tri_top_n * (tri_top_n - 1) * (tri_top_n - 2)
        cost = bet * tri_combos
        total_wagered += cost
        daily[day]["wagered"] += cost
        total += 1

        finish = race["finish"]
        if len(finish) >= 3:
            if finish[0] in top and finish[1] in top and finish[2] in top:
                payout = race["trifecta_pay"] * (bet / 2.0)
                total_returned += payout
                daily[day]["returned"] += payout
                hits += 1

    net = total_returned - total_wagered
    return {
        "total_wagered": total_wagered, "total_returned": total_returned,
        "net": net, "roi": (net / total_wagered * 100) if total_wagered > 0 else 0,
        "ex_hits": 0, "ex_total": 0, "ex_rate": 0,
        "tri_hits": hits, "tri_total": total, "tri_rate": hits/total*100 if total else 0,
        "show_hits": 0, "show_total": 0, "show_rate": 0,
        "daily": daily,
        "days_profitable": sum(1 for d in daily.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily),
    }


def test_cold_exacta(races, bet=2.0, min_starters=7):
    """Bet exactas AGAINST the favorite. Key ML#2 and #3 on top with #4-6 underneath.
    Theory: when the favorite loses, exotics pay big.
    """
    total_wagered = 0
    total_returned = 0
    daily = {}
    hits = 0
    total = 0

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"wagered": 0, "returned": 0}

        if race["starters"] < min_starters:
            continue

        sorted_ml = sorted(race["ml_odds"].items(), key=lambda x: x[1])
        # Key horses: ML#2 and ML#3 on top
        key = [sorted_ml[1][0], sorted_ml[2][0]]
        # With horses: ML#4, #5, #6
        with_h = [sorted_ml[i][0] for i in range(3, min(6, len(sorted_ml)))]

        if len(with_h) < 2:
            continue

        # Key on top only (not bottom — we're betting against chalk, so non-fav on top)
        num_combos = len(key) * len(with_h)
        cost = bet * num_combos
        total_wagered += cost
        daily[day]["wagered"] += cost
        total += 1

        finish = race["finish"]
        if len(finish) >= 2 and race.get("exacta_pay"):
            if finish[0] in key and finish[1] in with_h:
                payout = race["exacta_pay"] * (bet / 2.0)
                total_returned += payout
                daily[day]["returned"] += payout
                hits += 1
            elif finish[0] in with_h and finish[1] in key:
                payout = race["exacta_pay"] * (bet / 2.0)
                total_returned += payout
                daily[day]["returned"] += payout
                hits += 1

    net = total_returned - total_wagered
    return {
        "total_wagered": total_wagered, "total_returned": total_returned,
        "net": net, "roi": (net / total_wagered * 100) if total_wagered > 0 else 0,
        "ex_hits": hits, "ex_total": total, "ex_rate": hits/total*100 if total else 0,
        "tri_hits": 0, "tri_total": 0, "tri_rate": 0,
        "show_hits": 0, "show_total": 0, "show_rate": 0,
        "daily": daily,
        "days_profitable": sum(1 for d in daily.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily),
    }


def test_selective_combo(races, ex_bet=1.0, tri_bet=0.50, ex_top=4, tri_top=4,
                         min_starters=7, skip_chalk=True, min_fav_odds=2.0):
    """Selective approach: only play when conditions are favorable."""
    total_wagered = 0
    total_returned = 0
    daily = {}
    ex_hits = 0
    ex_total = 0
    tri_hits = 0
    tri_total = 0

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"wagered": 0, "returned": 0}

        if race["starters"] < min_starters:
            continue

        sorted_ml = sorted(race["ml_odds"].items(), key=lambda x: x[1])
        fav_odds = sorted_ml[0][1]

        # Skip heavy chalk races (favorite < 2/1)
        if skip_chalk and fav_odds < min_fav_odds:
            continue

        ml_top = [h for h, o in sorted_ml[:max(ex_top, tri_top)]]
        finish = race["finish"]

        # Exacta box
        ex_horses = ml_top[:ex_top]
        ex_combos = ex_top * (ex_top - 1)
        ex_cost = ex_bet * ex_combos
        total_wagered += ex_cost
        daily[day]["wagered"] += ex_cost
        ex_total += 1

        if len(finish) >= 2 and race.get("exacta_pay"):
            if finish[0] in ex_horses and finish[1] in ex_horses:
                payout = race["exacta_pay"] * (ex_bet / 2.0)
                total_returned += payout
                daily[day]["returned"] += payout
                ex_hits += 1

        # Trifecta box (8+ starters only)
        if race["starters"] >= 8 and race.get("trifecta_pay"):
            tri_horses = ml_top[:tri_top]
            tri_combos = tri_top * (tri_top - 1) * (tri_top - 2)
            tri_cost = tri_bet * tri_combos
            total_wagered += tri_cost
            daily[day]["wagered"] += tri_cost
            tri_total += 1

            if len(finish) >= 3:
                if finish[0] in tri_horses and finish[1] in tri_horses and finish[2] in tri_horses:
                    payout = race["trifecta_pay"] * (tri_bet / 2.0)
                    total_returned += payout
                    daily[day]["returned"] += payout
                    tri_hits += 1

    net = total_returned - total_wagered
    return {
        "total_wagered": total_wagered, "total_returned": total_returned,
        "net": net, "roi": (net / total_wagered * 100) if total_wagered > 0 else 0,
        "ex_hits": ex_hits, "ex_total": ex_total, "ex_rate": ex_hits/ex_total*100 if ex_total else 0,
        "tri_hits": tri_hits, "tri_total": tri_total, "tri_rate": tri_hits/tri_total*100 if tri_total else 0,
        "show_hits": 0, "show_total": 0, "show_rate": 0,
        "daily": daily,
        "days_profitable": sum(1 for d in daily.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily),
    }


print("=" * 70)
print("REAL BACKTEST V2 — ALTERNATIVE STRATEGIES")
print("5 track-days, 43 races with real ML odds + exotic payouts")
print("=" * 70)

# Keyed exactas (cheaper than full box)
r1 = test_keyed_exacta(RACE_DATA, key_n=1, with_n=3, bet_per_combo=2.0, min_starters=7)
print_results("KEY ML#1 with ML#2-4 ($2 each way, 7+ starters)", r1)

r2 = test_keyed_exacta(RACE_DATA, key_n=1, with_n=4, bet_per_combo=1.0, min_starters=7)
print_results("KEY ML#1 with ML#2-5 ($1 each way, 7+ starters)", r2)

# Value exactas (skip chalk)
r3 = test_value_exacta(RACE_DATA, ml_range=(3, 10), bet_amount=2.0, min_starters=7)
print_results("VALUE EX: ML#1 keyed with 3/1-10/1 value ($2, 7+)", r3)

# Selective trifectas (competitive fields only)
r4 = test_upset_tri(RACE_DATA, tri_top_n=5, bet=0.50, min_starters=8, min_ml_spread=3)
print_results("SELECTIVE TRI: ML5 $0.50, 8+ starters, spread>3", r4)

r5 = test_upset_tri(RACE_DATA, tri_top_n=5, bet=0.50, min_starters=8, min_ml_spread=2)
print_results("SELECTIVE TRI: ML5 $0.50, 8+ starters, spread>2", r5)

# Cold exactas (bet against favorite)
r6 = test_cold_exacta(RACE_DATA, bet=2.0, min_starters=7)
print_results("COLD EX: ML#2-3 keyed with ML#4-6 ($2, 7+)", r6)

# Selective combo: only bet non-chalk races
r7 = test_selective_combo(RACE_DATA, ex_bet=1.0, tri_bet=0.50, ex_top=4, tri_top=4,
                          min_starters=7, skip_chalk=True, min_fav_odds=2.0)
print_results("SELECTIVE: ML4 $1 EX + ML4 $0.50 TRI (skip <2/1 fav)", r7)

r8 = test_selective_combo(RACE_DATA, ex_bet=1.0, tri_bet=0.50, ex_top=4, tri_top=4,
                          min_starters=7, skip_chalk=True, min_fav_odds=2.5)
print_results("SELECTIVE: ML4 $1 EX + ML4 $0.50 TRI (skip <5/2 fav)", r8)

r9 = test_selective_combo(RACE_DATA, ex_bet=2.0, tri_bet=1.0, ex_top=3, tri_top=4,
                          min_starters=8, skip_chalk=True, min_fav_odds=2.5)
print_results("TIGHT: ML3 $2 EX + ML4 $1 TRI (8+, skip <5/2)", r9)

# Deep analysis: what races actually make money?
print("\n" + "=" * 70)
print("DEEP DIVE: Which individual races were profitable?")
print("=" * 70)

for race in RACE_DATA:
    ml_top = get_ml_top_n(race, 5)
    finish = race["finish"]

    # ML5 exacta box cost: 20 combos x $0.50 = $10
    ex_cost = 10.0
    ex_return = 0
    if len(finish) >= 2 and finish[0] in ml_top and finish[1] in ml_top:
        ex_return = race["exacta_pay"] * 0.25  # $0.50/$2 base

    # ML4 tri box cost: 24 combos x $0.50 = $12
    tri_cost = 12.0 if race["starters"] >= 7 and race.get("trifecta_pay") else 0
    tri_return = 0
    ml4 = ml_top[:4]
    if len(finish) >= 3 and finish[0] in ml4 and finish[1] in ml4 and finish[2] in ml4 and race.get("trifecta_pay"):
        tri_return = race["trifecta_pay"] * 0.25

    total_cost = ex_cost + tri_cost
    total_return = ex_return + tri_return
    net = total_return - total_cost

    if abs(net) > 5:  # Only show significant P&L
        winner_ml = race["ml_odds"].get(finish[0], "?")
        marker = "WIN" if net > 0 else "LOSS"
        print(f"  {race['day']} R{race['race']}: {marker} ${net:+.1f} | "
              f"Winner: {finish[0]} ({winner_ml}/1 ML) | "
              f"EX={'+' if ex_return > 0 else 'miss'} TRI={'+' if tri_return > 0 else ('miss' if tri_cost > 0 else 'skip')} | "
              f"Type={race['type']} Starters={race['starters']}")

# Summary stats
print("\n" + "=" * 70)
print("KEY INSIGHT: Average exacta payout when ML5 hits")
print("=" * 70)
hit_payouts = []
miss_races = []
for race in RACE_DATA:
    ml_top = get_ml_top_n(race, 5)
    finish = race["finish"]
    if len(finish) >= 2 and finish[0] in ml_top and finish[1] in ml_top and race.get("exacta_pay"):
        hit_payouts.append(race["exacta_pay"])
    elif race.get("exacta_pay"):
        miss_races.append((race["day"], race["race"], race["exacta_pay"], race["finish"][0],
                          race["ml_odds"].get(race["finish"][0], "?")))

print(f"ML5 exacta hit payouts (${0.50} base = posted/4):")
for p in sorted(hit_payouts):
    print(f"  ${p:.2f} posted = ${p*0.25:.2f} actual return")
print(f"\nAvg hit payout (posted): ${sum(hit_payouts)/len(hit_payouts):.2f}")
print(f"Avg actual return (at $0.50): ${sum(p*0.25 for p in hit_payouts)/len(hit_payouts):.2f}")
print(f"Cost per race ($0.50 x 20 combos): $10.00")
print(f"Break-even payout needed (posted): ${10.0/0.25:.2f}")
print(f"\nML5 exacta MISSES (potential payoffs we missed):")
for day, rn, pay, winner, ml in miss_races:
    print(f"  {day} R{rn}: {winner} ({ml}/1 ML) | Exacta paid ${pay:.2f}")
