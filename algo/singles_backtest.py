#!/usr/bin/env python3
"""
SINGLES BACKTEST — Instead of boxing 5 horses (20 combos), bet TARGETED
single combos based on the most common finishing patterns.

Key insight from pattern analysis:
- #1-#4 exacta happens 16.3% of the time, pays avg $28.26
- #1-#2 happens 14.0%, pays avg $13.97
- #1-#3 happens 9.3%, pays avg $15.20
- #2-#3 happens 9.3%, pays avg $48.60

A $2 exacta box of 5 horses = 20 combos = $40/race
But the top 4 patterns account for 49% of exacta results!
So 4 targeted combos ($8/race) catches nearly half the exactas.
"""

from deep_backtest import RACE_DATA, get_ml_sorted, get_ml_top_n, get_ml_rank

print("=" * 100)
print("SINGLES/TARGETED COMBOS BACKTEST — 43 races")
print("=" * 100)


def test_exacta_singles(races, combos_list, bet_per_combo=2.0, min_starters=0):
    """
    combos_list: list of (winner_rank, place_rank) tuples.
    e.g. [(1,2), (1,3), (1,4)] means bet:
      - ML#1 on top, ML#2 underneath
      - ML#1 on top, ML#3 underneath
      - ML#1 on top, ML#4 underneath
    """
    total_w, total_r = 0, 0
    daily = {}
    hits, plays = 0, 0
    hit_details = []

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("exacta_pay"):
            continue

        day = race["day"]
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}

        ml_sorted = get_ml_sorted(race)
        finish = race["finish"]
        if len(finish) < 2:
            continue

        cost = bet_per_combo * len(combos_list)
        total_w += cost
        daily[day]["w"] += cost
        plays += 1

        winner_rank = get_ml_rank(race, finish[0])
        place_rank = get_ml_rank(race, finish[1])

        for (wr, pr) in combos_list:
            if winner_rank == wr and place_rank == pr:
                payout = race["exacta_pay"] * (bet_per_combo / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1
                hit_details.append({
                    "day": day, "race": race["race"],
                    "pattern": f"#{wr}-#{pr}", "payout": payout
                })
                break

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["r"] > d["w"])
    return {
        "w": total_w, "r": total_r, "net": net, "roi": roi,
        "hits": hits, "plays": plays, "daily": daily,
        "profitable_days": profitable_days, "total_days": len(daily),
        "hit_details": hit_details
    }


def test_trifecta_singles(races, combos_list, bet_per_combo=1.0, min_starters=7):
    """
    combos_list: list of (1st_rank, 2nd_rank, 3rd_rank) tuples.
    """
    total_w, total_r = 0, 0
    daily = {}
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("trifecta_pay"):
            continue

        day = race["day"]
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}

        finish = race["finish"]
        if len(finish) < 3:
            continue

        cost = bet_per_combo * len(combos_list)
        total_w += cost
        daily[day]["w"] += cost
        plays += 1

        ranks = tuple(get_ml_rank(race, finish[i]) for i in range(3))

        for combo in combos_list:
            if ranks == combo:
                payout = race["trifecta_pay"] * (bet_per_combo / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1
                break

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["r"] > d["w"])
    return {"w": total_w, "r": total_r, "net": net, "roi": roi,
            "hits": hits, "plays": plays, "profitable_days": profitable_days,
            "total_days": len(daily)}


def print_result(name, r, show_details=False):
    marker = " *** PROFITABLE ***" if r["roi"] > 0 else ""
    rate = r["hits"]/r["plays"]*100 if r["plays"] > 0 else 0
    print(f"{name:55s} W:${r['w']:7.1f} R:${r['r']:7.1f} Net:${r['net']:+8.1f} "
          f"ROI:{r['roi']:+6.1f}% Hits:{r['hits']}/{r['plays']}({rate:.0f}%) "
          f"Days:{r['profitable_days']}/{r['total_days']}{marker}")
    if show_details and "hit_details" in r:
        for h in r["hit_details"]:
            print(f"    HIT: {h['day']} R{h['race']} {h['pattern']} -> ${h['payout']:.2f}")


# ============== EXACTA SINGLES ==============
print("\n--- EXACTA SINGLE COMBOS ($2/combo) ---")

# Favorite on top, various underneath
configs = [
    ("Fav-2nd", [(1, 2)]),
    ("Fav-3rd", [(1, 3)]),
    ("Fav-4th", [(1, 4)]),
    ("Fav-5th", [(1, 5)]),
    ("Fav on top w/ 2-4", [(1, 2), (1, 3), (1, 4)]),
    ("Fav on top w/ 2-5", [(1, 2), (1, 3), (1, 4), (1, 5)]),
    ("2nd-Fav", [(2, 1)]),
    ("3rd-Fav", [(3, 1)]),
    ("4th-Fav", [(4, 1)]),
    ("Fav/2nd both ways", [(1, 2), (2, 1)]),
    ("Fav/3rd both ways", [(1, 3), (3, 1)]),
    ("Fav/4th both ways", [(1, 4), (4, 1)]),
    ("Top3 crossing", [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]),
    ("Fav w/ 2-4 + reverse", [(1, 2), (1, 3), (1, 4), (2, 1), (3, 1), (4, 1)]),
    ("Value: 4th/5th top w/ 1-2", [(4, 1), (4, 2), (5, 1), (5, 2)]),
    ("Value: 2-5 top w/ Fav", [(2, 1), (3, 1), (4, 1), (5, 1)]),
]

for name, combos in configs:
    r = test_exacta_singles(RACE_DATA, combos, bet_per_combo=2.0)
    print_result(f"Ex ${2*len(combos)}/race: {name}", r, show_details=(r["roi"] > 0))

# Now test with $1 combos (half the payout but half the cost)
print("\n--- EXACTA SINGLE COMBOS ($1/combo) ---")
for name, combos in configs:
    r = test_exacta_singles(RACE_DATA, combos, bet_per_combo=1.0)
    print_result(f"Ex ${1*len(combos)}/race: {name}", r, show_details=(r["roi"] > 0))

# ============== EXACTA SINGLES WITH FIELD SIZE FILTER ==============
print("\n--- EXACTA SINGLES + FIELD SIZE FILTER ($1/combo) ---")
best_combos = [(1, 2), (1, 3), (1, 4), (4, 1)]  # Most common patterns

for min_s in [6, 7, 8, 9]:
    r = test_exacta_singles(RACE_DATA, best_combos, bet_per_combo=1.0, min_starters=min_s)
    print_result(f"Ex $4/race: Fav-234+4-Fav {min_s}+ starters", r, show_details=(r["roi"] > 0))

# ============== TRIFECTA SINGLES ==============
print("\n--- TRIFECTA SINGLE COMBOS ($1/combo) ---")

# Generate the most likely trifecta combos based on pattern analysis
# Top 4 bracket (ranks 1-4) covers 25% of trifectas
from itertools import permutations

# All permutations of top 3 ML picks
top3_perms = list(permutations([1, 2, 3]))
top4_perms = list(permutations(range(1, 5), 3))

configs_tri = [
    ("Top3 all orders (6 combos)", top3_perms),
    ("1-2-3 only", [(1, 2, 3)]),
    ("1-2-X (X=3-5)", [(1, 2, 3), (1, 2, 4), (1, 2, 5)]),
    ("1-X-Y (top4 perms)", [(1, 2, 3), (1, 2, 4), (1, 3, 2), (1, 3, 4), (1, 4, 2), (1, 4, 3)]),
    ("Top4 all orders (24 combos)", list(permutations(range(1, 5), 3))),
]

for name, combos in configs_tri:
    r = test_trifecta_singles(RACE_DATA, combos, bet_per_combo=1.0, min_starters=7)
    if r["plays"] > 0:
        print_result(f"Tri ${len(combos)}/race: {name}", r)

for name, combos in configs_tri:
    r = test_trifecta_singles(RACE_DATA, combos, bet_per_combo=0.50, min_starters=7)
    if r["plays"] > 0:
        print_result(f"Tri ${0.5*len(combos):.0f}/race: {name} @$0.50", r)


# ============== COMBO: Best exacta + best trifecta ==============
print("\n--- COMBO: BEST EXACTA + TRIFECTA SINGLES ---")

# Test combined approaches
def test_combo(races, ex_combos, tri_combos, ex_bet=1.0, tri_bet=0.50,
               ex_min_starters=0, tri_min_starters=7):
    total_w, total_r = 0, 0
    daily = {}

    for race in races:
        day = race["day"]
        if day not in daily:
            daily[day] = {"w": 0, "r": 0}

        finish = race["finish"]
        ml_sorted = get_ml_sorted(race)

        # Exacta
        if race.get("exacta_pay") and len(finish) >= 2 and race["starters"] >= ex_min_starters:
            cost = ex_bet * len(ex_combos)
            total_w += cost
            daily[day]["w"] += cost

            wr = get_ml_rank(race, finish[0])
            pr = get_ml_rank(race, finish[1])
            for (w, p) in ex_combos:
                if wr == w and pr == p:
                    payout = race["exacta_pay"] * (ex_bet / 2.0)
                    total_r += payout
                    daily[day]["r"] += payout
                    break

        # Trifecta
        if race.get("trifecta_pay") and len(finish) >= 3 and race["starters"] >= tri_min_starters:
            cost = tri_bet * len(tri_combos)
            total_w += cost
            daily[day]["w"] += cost

            ranks = tuple(get_ml_rank(race, finish[i]) for i in range(3))
            for combo in tri_combos:
                if ranks == combo:
                    payout = race["trifecta_pay"] * (tri_bet / 2.0)
                    total_r += payout
                    daily[day]["r"] += payout
                    break

    net = total_r - total_w
    roi = (net / total_w * 100) if total_w > 0 else 0
    profitable_days = sum(1 for d in daily.values() if d["r"] > d["w"])
    return {"w": total_w, "r": total_r, "net": net, "roi": roi,
            "profitable_days": profitable_days, "total_days": len(daily)}

# Best exacta patterns + top4 trifecta perms
best_ex = [(1, 2), (1, 3), (1, 4), (4, 1)]
top4_tri = list(permutations(range(1, 5), 3))

r = test_combo(RACE_DATA, best_ex, top4_tri, ex_bet=1.0, tri_bet=0.50, tri_min_starters=7)
print_result("Ex:Fav-234+4-Fav $1 + Tri:Top4 $0.50 7+", r)

r = test_combo(RACE_DATA, best_ex, top4_tri, ex_bet=1.0, tri_bet=0.50, tri_min_starters=8)
print_result("Ex:Fav-234+4-Fav $1 + Tri:Top4 $0.50 8+", r)

# Fav on top with 2-4 + all top4 trifecta
fav_top = [(1, 2), (1, 3), (1, 4)]
r = test_combo(RACE_DATA, fav_top, top4_tri, ex_bet=1.0, tri_bet=0.50, tri_min_starters=7)
print_result("Ex:Fav-234 $1 + Tri:Top4 $0.50 7+", r)

# More targeted: fewer tri combos
fav_tri = [(1, 2, 3), (1, 2, 4), (1, 3, 2), (1, 3, 4), (1, 4, 2), (1, 4, 3)]
r = test_combo(RACE_DATA, best_ex, fav_tri, ex_bet=1.0, tri_bet=0.50, tri_min_starters=7)
print_result("Ex:Fav-234+4-Fav $1 + Tri:Fav-top 6 $0.50 7+", r)

# Value exacta + wide trifecta
value_ex = [(2, 1), (3, 1), (4, 1), (5, 1), (2, 3), (5, 2)]
r = test_combo(RACE_DATA, value_ex, top4_tri, ex_bet=1.0, tri_bet=0.50, tri_min_starters=7)
print_result("Ex:Value(non-fav top) $1 + Tri:Top4 $0.50 7+", r)

# All the combos that hit in our data
all_hit_combos = [(1,4),(1,2),(1,3),(2,3),(5,2),(4,1),(2,4),(1,5),(4,5),(3,1),
                  (3,6),(1,7),(2,6),(4,3),(9,2),(6,7),(4,7),(6,3),(4,6),(1,10),(4,8),(3,7)]
r = test_exacta_singles(RACE_DATA, all_hit_combos, bet_per_combo=1.0)
print_result("ALL observed patterns (22 combos) $1 each", r)


print("\n" + "=" * 100)
print("KEY FINDING: Look for strategies with positive ROI")
print("=" * 100)
