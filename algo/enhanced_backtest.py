#!/usr/bin/env python3
"""
Enhanced Horse Racing Strategy Backtester
=========================================
Tests multiple strategy variants against actual race results with full horse-level data.
Iterates through parameter combinations to find the most profitable approach.

Key enhancements over the original:
1. Morning Line Value Score - identifies overlooked horses at good odds
2. Contrarian Picks - horses at 3/1 to 8/1 ML that experts ignored
3. Wider Exacta Coverage - include value horses in exotic bets
4. Dynamic Bet Sizing - scale bets based on confidence + field size
5. Field Size Awareness - bigger fields = more exotic spread
"""

import json
import os
import sys
import re
import itertools
from copy import deepcopy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "/tmp/race_day_data"


def parse_ml_to_decimal(ml_str):
    """Convert morning line odds string (e.g., '5/2', '12/1') to decimal."""
    if not ml_str or ml_str == "":
        return 0
    try:
        if "/" in ml_str:
            num, den = ml_str.split("/")
            return float(num) / float(den)
        return float(ml_str)
    except (ValueError, ZeroDivisionError):
        return 0


def parse_picks(picks_str):
    """Parse picks string like '3/5' to (count, total)."""
    if not picks_str or picks_str == "":
        return 0, 0
    try:
        parts = picks_str.split("/")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return 0, 0


def parse_payout(result_str, bet_type="exacta"):
    """Extract payout from result string."""
    if not result_str:
        return 0
    patterns = {
        "win": r"\$(\d+\.?\d*)/",
        "exacta": r"Exacta.*?\$(\d+\.?\d*)",
        "trifecta": r"Trifecta.*?\$(\d+\.?\d*)",
        "superfecta": r"Super.*?\$(\d+\.?\d*)",
    }
    pattern = patterns.get(bet_type, patterns["exacta"])
    m = re.search(pattern, result_str)
    return float(m.group(1)) if m else 0


def parse_win_payout(result_str):
    """Extract win payout from result string like '$9.00/$5.00/$3.40'."""
    if not result_str:
        return 0
    m = re.search(r"\(\$(\d+\.?\d*)/", result_str)
    return float(m.group(1)) if m else 0


def parse_finish_order(result_str, horses):
    """Parse result string to get finish order (list of PP numbers)."""
    if not result_str:
        return []
    finish = []
    # Pattern: #N Name (position)
    for m in re.finditer(r"#(\d+)\s+\w+", result_str):
        finish.append(int(m.group(1)))
    # Also try to parse from horse names with (WON), (2nd), (3rd), (4th)
    if not finish:
        for h in horses:
            name = h.get("name", "")
            if "(WON)" in name:
                finish.insert(0, h["pp"])
            elif "(2nd)" in name:
                if len(finish) < 1:
                    finish.append(0)
                finish.insert(1, h["pp"])
            elif "(3rd)" in name:
                while len(finish) < 2:
                    finish.append(0)
                finish.insert(2, h["pp"])
            elif "(4th)" in name:
                while len(finish) < 3:
                    finish.append(0)
                finish.insert(3, h["pp"])
    return finish


def get_winner_pp(horses):
    """Get the post position of the winner from horse list."""
    for h in horses:
        if "(WON)" in h.get("name", ""):
            return h["pp"]
    return None


def get_place_pp(horses):
    """Get the PP of the 2nd place horse."""
    for h in horses:
        if "(2nd)" in h.get("name", ""):
            return h["pp"]
    return None


def get_show_pp(horses):
    """Get the PP of the 3rd place horse."""
    for h in horses:
        if "(3rd)" in h.get("name", ""):
            return h["pp"]
    return None


def load_race_day(filepath):
    """Load a race day JSON file and return structured data."""
    with open(filepath) as f:
        data = json.load(f)

    races = []
    for r in data.get("races", []):
        if r.get("status") != "COMPLETED":
            continue
        horses = r.get("horses", [])
        if not horses:
            continue

        # Filter out scratched horses
        active_horses = [h for h in horses if "SCR" not in h.get("name", "")]

        winner_pp = get_winner_pp(active_horses)
        place_pp = get_place_pp(active_horses)
        show_pp = get_show_pp(active_horses)

        if winner_pp is None:
            continue

        # Parse payouts from result string
        result_str = r.get("result", "")
        win_payout = parse_win_payout(result_str)
        exacta_payout = parse_payout(result_str, "exacta")
        trifecta_payout = parse_payout(result_str, "trifecta")
        superfecta_payout = parse_payout(result_str, "superfecta")

        # Build horse info
        horse_info = []
        for h in active_horses:
            picks_count, picks_total = parse_picks(h.get("picks", ""))
            ml = parse_ml_to_decimal(h.get("ml", ""))
            horse_info.append({
                "pp": h["pp"],
                "name": h.get("name", "").replace(" (WON)", "").replace(" (2nd)", "").replace(" (3rd)", "").replace(" (4th)", ""),
                "ml": ml,
                "ml_str": h.get("ml", ""),
                "picks": picks_count,
                "picks_total": picks_total,
                "tier": h.get("tier", "RED"),
                "jockey": h.get("jockey", ""),
                "trainer": h.get("trainer", ""),
                "is_winner": h["pp"] == winner_pp,
                "is_place": h["pp"] == place_pp,
                "is_show": h["pp"] == show_pp,
            })

        races.append({
            "number": r["number"],
            "type": r.get("type", "OTH"),
            "type_label": r.get("type_label", ""),
            "starters": r.get("starters", len(active_horses)),
            "distance": r.get("distance", ""),
            "purse": r.get("purse", ""),
            "horses": horse_info,
            "winner_pp": winner_pp,
            "place_pp": place_pp,
            "show_pp": show_pp,
            "win_payout": win_payout,
            "exacta_payout": exacta_payout,
            "trifecta_payout": trifecta_payout,
            "superfecta_payout": superfecta_payout,
            "result": result_str,
        })

    return {
        "track": data.get("track", "Unknown"),
        "date": data.get("date", "Unknown"),
        "races": races,
    }


# =============================================================================
# HORSE SCORING MODELS
# =============================================================================

def score_consensus_only(horse, race):
    """Original model: expert consensus only."""
    return horse["picks"]


def score_enhanced_v1(horse, race, params=None):
    """
    Enhanced model v1: consensus + morning line value + contrarian detection.

    Scoring:
    - Expert consensus (0-5 picks) weighted by confidence
    - Morning line value: horses at moderate odds (3/1 to 8/1) get a bonus
    - Contrarian bonus: 0-pick horses at 3/1 to 6/1 ML get extra points
      (these are the ones experts overlook that win ~25% of the time)
    - Field size adjustment
    """
    if params is None:
        params = {}

    consensus_weight = params.get("consensus_weight", 2.0)
    ml_value_weight = params.get("ml_value_weight", 1.5)
    contrarian_weight = params.get("contrarian_weight", 1.0)

    score = 0

    # 1. Expert consensus (still matters!)
    score += horse["picks"] * consensus_weight

    # 2. Morning line value zone
    ml = horse["ml"]
    if 2.0 <= ml <= 4.0:
        # Sweet spot: good enough odds to be profitable, short enough to win often
        score += ml_value_weight * 1.5
    elif 4.0 < ml <= 8.0:
        # Value zone: experts often overlook these
        score += ml_value_weight * 2.0
    elif 8.0 < ml <= 15.0:
        # Longshot zone: include in exotics only
        score += ml_value_weight * 0.5

    # 3. Contrarian detection: 0-pick horse at reasonable odds
    if horse["picks"] == 0 and 2.5 <= ml <= 6.0:
        score += contrarian_weight * 2.5

    # 4. Race type bonus (CLM races have more predictable upsets)
    if race["type"] in ("CLM", "MC") and ml >= 3.0:
        score += 0.5

    return score


def score_enhanced_v2(horse, race, params=None):
    """
    Enhanced model v2: adds trainer/jockey patterns + position analysis.
    """
    if params is None:
        params = {}

    consensus_weight = params.get("consensus_weight", 1.5)
    ml_value_weight = params.get("ml_value_weight", 2.0)
    contrarian_weight = params.get("contrarian_weight", 1.5)
    position_weight = params.get("position_weight", 0.5)

    score = 0

    # 1. Expert consensus
    score += horse["picks"] * consensus_weight

    # 2. ML value - wider sweet spot
    ml = horse["ml"]
    if 2.0 <= ml <= 3.0:
        score += ml_value_weight * 1.0
    elif 3.0 < ml <= 5.0:
        score += ml_value_weight * 2.0  # Prime value zone
    elif 5.0 < ml <= 8.0:
        score += ml_value_weight * 1.5
    elif 8.0 < ml <= 12.0:
        score += ml_value_weight * 0.8
    elif ml > 12.0:
        score += ml_value_weight * 0.3

    # 3. Contrarian - more aggressive
    if horse["picks"] == 0 and 2.5 <= ml <= 8.0:
        score += contrarian_weight * 2.0
    elif horse["picks"] == 1 and 3.0 <= ml <= 6.0:
        score += contrarian_weight * 1.0

    # 4. Post position (inner posts slightly favored at Parx dirt sprints)
    if horse["pp"] <= 4 and "Dirt" in race.get("distance", ""):
        score += position_weight

    # 5. Race type
    if race["type"] in ("CLM", "MC"):
        score += 0.5

    return score


def score_ml_contrarian(horse, race, params=None):
    """
    Model v3: ML-dominant contrarian model.
    Hypothesis: Morning line odds are set by the track handicapper who
    actually watches workouts. Experts often just follow each other.
    A horse at 4/1 ML with 0 expert picks is an EDGE.
    """
    if params is None:
        params = {}

    ml = horse["ml"]
    picks = horse["picks"]

    score = 0

    # ML-based scoring (the handicapper knows something)
    if ml <= 1.5:  # Heavy fav
        score += 3.0
    elif ml <= 3.0:  # Fav
        score += 4.0
    elif ml <= 5.0:  # Contender
        score += 5.0  # Highest score - best value zone
    elif ml <= 8.0:  # Price horse
        score += 3.5
    elif ml <= 12.0:  # Longshot
        score += 2.0
    elif ml <= 20.0:  # Big longshot
        score += 1.0
    else:
        score += 0.3

    # Expert consensus as modifier (not driver)
    if picks >= 4:
        score += 1.0  # Small boost for heavy consensus
    elif picks >= 2:
        score += 0.5

    # Contrarian edge: ML says competitive, experts disagree
    if picks == 0 and 2.5 <= ml <= 6.0:
        score += params.get("contrarian_bonus", 2.0)

    return score


# =============================================================================
# BETTING STRATEGIES
# =============================================================================

def strategy_original(race, budget=125):
    """Original strategy: expert consensus picks only."""
    bets = []
    horses = race["horses"]

    # Sort by expert picks
    by_picks = sorted(horses, key=lambda h: h["picks"], reverse=True)

    # Top 2 picks for exacta box
    top2 = [h for h in by_picks if h["picks"] >= 2][:2]
    if len(top2) == 2:
        bets.append({
            "type": "exacta_box",
            "horses": [top2[0]["pp"], top2[1]["pp"]],
            "cost": 4.0,  # $2 box = $4
        })

    # GREEN picks get exacta wheel
    green = [h for h in horses if h["tier"] == "GREEN" or h["picks"] >= 4]
    for g in green[:1]:
        # Key horse with 2-3 value horses
        value_horses = [h for h in by_picks if h["pp"] != g["pp"] and h["picks"] >= 1][:3]
        if value_horses:
            wheel_pps = [h["pp"] for h in value_horses]
            cost = len(wheel_pps) * 2 * 2  # $2 each way
            bets.append({
                "type": "exacta_wheel",
                "key": g["pp"],
                "with": wheel_pps,
                "cost": cost,
            })

    # WIN bets on 5/1+ value plays
    for h in horses:
        if h["ml"] >= 5.0 and h["picks"] >= 1:
            bets.append({
                "type": "win",
                "horse": h["pp"],
                "cost": 10.0,
            })

    # Trifecta box on CLM 7+ starters
    if race["type"] in ("CLM", "MC") and race["starters"] >= 7:
        top3 = [h for h in by_picks if h["picks"] >= 1][:3]
        if len(top3) >= 3:
            bets.append({
                "type": "trifecta_box",
                "horses": [h["pp"] for h in top3],
                "cost": 12.0,  # $2 box of 3 = $12
            })

    return bets


def strategy_enhanced(race, scorer, params=None, budget=125):
    """
    Enhanced strategy using scoring model.

    Key changes:
    - Score ALL horses, not just expert picks
    - Wider exacta coverage (top 3 instead of top 2)
    - Contrarian WIN bets on overlooked value horses
    - Dynamic trifecta coverage based on field size
    """
    if params is None:
        params = {}

    bets = []
    horses = race["horses"]

    # Score all horses
    scored = []
    for h in horses:
        s = scorer(h, race, params)
        scored.append((h, s))
    scored.sort(key=lambda x: x[1], reverse=True)

    top_horses = [h for h, s in scored]
    top_scores = [s for h, s in scored]

    # ---- EXACTA BETS ----

    # Strategy param: how many horses in exacta
    exacta_width = params.get("exacta_width", 3)
    exacta_bet = params.get("exacta_bet", 2.0)

    # Exacta box with top N scored horses
    exacta_horses = [h["pp"] for h in top_horses[:exacta_width]]
    # Cost of boxing N horses: N*(N-1) * bet_amount
    num_combos = len(exacta_horses) * (len(exacta_horses) - 1)
    bets.append({
        "type": "exacta_box",
        "horses": exacta_horses,
        "cost": num_combos * exacta_bet,
    })

    # Exacta wheel on #1 pick with next 2-3
    if params.get("use_wheels", True):
        wheel_width = params.get("wheel_width", 3)
        wheel_bet = params.get("wheel_bet", 2.0)
        key_horse = top_horses[0]["pp"]
        wheel_horses = [h["pp"] for h in top_horses[1:1+wheel_width]]
        cost = len(wheel_horses) * wheel_bet * 2  # Both directions
        bets.append({
            "type": "exacta_wheel",
            "key": key_horse,
            "with": wheel_horses,
            "cost": cost,
        })

    # ---- WIN BETS ----
    win_min_ml = params.get("win_min_ml", 3.0)
    win_max_ml = params.get("win_max_ml", 12.0)
    win_bet = params.get("win_bet", 8.0)
    win_min_score = params.get("win_min_score", 4.0)

    for h, s in scored:
        if win_min_ml <= h["ml"] <= win_max_ml and s >= win_min_score:
            bets.append({
                "type": "win",
                "horse": h["pp"],
                "cost": win_bet,
                "score": s,
            })

    # ---- TRIFECTA BETS ----
    tri_min_starters = params.get("tri_min_starters", 7)
    tri_bet = params.get("tri_bet", 1.0)
    tri_width = params.get("tri_width", 4)

    if race["starters"] >= tri_min_starters:
        tri_horses = [h["pp"] for h in top_horses[:tri_width]]
        num_tri_combos = len(tri_horses) * (len(tri_horses)-1) * (len(tri_horses)-2)
        bets.append({
            "type": "trifecta_box",
            "horses": tri_horses,
            "cost": num_tri_combos * tri_bet,
        })

    # ---- SUPERFECTA on big fields ----
    if race["starters"] >= 9 and params.get("use_supers", True):
        super_horses = [h["pp"] for h in top_horses[:5]]
        bets.append({
            "type": "superfecta_box",
            "horses": super_horses,
            "cost": 0.20 * 120,  # 5 horses = 120 combos * $0.20
        })

    return bets


def evaluate_bets(bets, race):
    """Evaluate all bets against actual results. Return (wagered, returned)."""
    wagered = 0
    returned = 0
    details = []

    winner = race["winner_pp"]
    place = race["place_pp"]
    show = race["show_pp"]

    for bet in bets:
        wagered += bet["cost"]

        if bet["type"] == "win":
            if bet["horse"] == winner:
                # Win payout is per $2, scale to bet size
                payout = race["win_payout"] * (bet["cost"] / 2.0)
                returned += payout
                details.append(f"  WIN HIT #{bet['horse']} = ${payout:.2f}")
            else:
                details.append(f"  WIN MISS #{bet['horse']}")

        elif bet["type"] == "exacta_box":
            horses = bet["horses"]
            if winner in horses and place in horses:
                # Exacta hit! Scale payout based on bet size
                n = len(horses)
                per_combo = bet["cost"] / (n * (n-1))
                payout = race["exacta_payout"] * (per_combo / 1.0)
                returned += payout
                details.append(f"  EXACTA BOX HIT {horses} = ${payout:.2f}")
            else:
                details.append(f"  EXACTA BOX MISS {horses}")

        elif bet["type"] == "exacta_wheel":
            key = bet["key"]
            withs = bet["with"]
            per_combo = bet["cost"] / (len(withs) * 2)

            # Check key on top
            if key == winner and place in withs:
                payout = race["exacta_payout"] * (per_combo / 1.0)
                returned += payout
                details.append(f"  EXACTA WHEEL HIT (key #{key} top) = ${payout:.2f}")
            # Check key on bottom
            elif key == place and winner in withs:
                payout = race["exacta_payout"] * (per_combo / 1.0)
                returned += payout
                details.append(f"  EXACTA WHEEL HIT (key #{key} bottom) = ${payout:.2f}")
            else:
                details.append(f"  EXACTA WHEEL MISS key=#{key} with={withs}")

        elif bet["type"] == "trifecta_box":
            horses = bet["horses"]
            if winner in horses and place in horses and show in horses:
                n = len(horses)
                per_combo = bet["cost"] / (n * (n-1) * (n-2))
                payout = race["trifecta_payout"] * (per_combo / 1.0)
                returned += payout
                details.append(f"  TRIFECTA BOX HIT {horses} = ${payout:.2f}")
            else:
                details.append(f"  TRIFECTA BOX MISS {horses}")

        elif bet["type"] == "superfecta_box":
            horses = bet["horses"]
            fourth_pp = None
            for h in race["horses"]:
                if "(4th)" in h.get("name", ""):
                    fourth_pp = h["pp"]
                    break
            if (winner in horses and place in horses and
                show in horses and fourth_pp and fourth_pp in horses):
                payout = race["superfecta_payout"] * (bet["cost"] / 24.0)
                returned += payout
                details.append(f"  SUPERFECTA HIT = ${payout:.2f}")
            else:
                details.append(f"  SUPERFECTA MISS {horses}")

    return wagered, returned, details


def run_backtest(race_day, strategy_fn, scorer_fn=None, params=None, verbose=True):
    """Run a full backtest on a race day."""
    total_wagered = 0
    total_returned = 0
    all_details = []

    for race in race_day["races"]:
        if scorer_fn:
            bets = strategy_fn(race, scorer_fn, params)
        else:
            bets = strategy_fn(race)

        w, r, details = evaluate_bets(bets, race)
        total_wagered += w
        total_returned += r

        profit = r - w
        marker = "+" if profit > 0 else ""
        if verbose:
            all_details.append(
                f"R{race['number']} ({race['type']} {race['starters']}st): "
                f"Wagered ${w:.2f}, Returned ${r:.2f}, P/L {marker}${profit:.2f}"
            )
            all_details.extend(details)

    net = total_returned - total_wagered
    roi = (net / total_wagered * 100) if total_wagered > 0 else 0

    return {
        "wagered": total_wagered,
        "returned": total_returned,
        "net": net,
        "roi": roi,
        "details": all_details,
    }


def parameter_sweep(race_days, scorer_fn, strategy_fn):
    """
    Sweep through parameter combinations to find the most profitable strategy.
    """
    param_grid = {
        "consensus_weight": [1.0, 1.5, 2.0, 2.5],
        "ml_value_weight": [1.0, 1.5, 2.0, 2.5, 3.0],
        "contrarian_weight": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
        "contrarian_bonus": [1.0, 1.5, 2.0, 2.5, 3.0],
        "exacta_width": [2, 3, 4],
        "exacta_bet": [1.0, 2.0],
        "use_wheels": [True, False],
        "wheel_width": [2, 3],
        "wheel_bet": [1.0, 2.0],
        "win_min_ml": [2.5, 3.0, 4.0, 5.0],
        "win_max_ml": [8.0, 10.0, 12.0, 15.0],
        "win_bet": [5.0, 8.0, 10.0],
        "win_min_score": [3.0, 4.0, 5.0, 6.0],
        "tri_min_starters": [6, 7, 8],
        "tri_bet": [0.50, 1.0, 2.0],
        "tri_width": [3, 4, 5],
        "use_supers": [True, False],
    }

    # Too many combinations for full sweep - use staged optimization
    # Stage 1: Test scoring model weights (most impactful)
    print("Stage 1: Optimizing scoring weights...")
    best_score_params = None
    best_score_roi = -999

    stage1_grid = list(itertools.product(
        param_grid["consensus_weight"],
        param_grid["ml_value_weight"],
        param_grid["contrarian_weight"],
    ))

    for cw, mw, crw in stage1_grid:
        params = {
            "consensus_weight": cw,
            "ml_value_weight": mw,
            "contrarian_weight": crw,
            "contrarian_bonus": 2.0,
            "exacta_width": 3,
            "exacta_bet": 2.0,
            "use_wheels": True,
            "wheel_width": 3,
            "wheel_bet": 2.0,
            "win_min_ml": 3.0,
            "win_max_ml": 10.0,
            "win_bet": 8.0,
            "win_min_score": 4.0,
            "tri_min_starters": 7,
            "tri_bet": 1.0,
            "tri_width": 4,
            "use_supers": True,
        }

        total_net = 0
        total_wagered = 0
        for rd in race_days:
            result = run_backtest(rd, strategy_fn, scorer_fn, params, verbose=False)
            total_net += result["net"]
            total_wagered += result["wagered"]

        roi = (total_net / total_wagered * 100) if total_wagered > 0 else -999
        if roi > best_score_roi:
            best_score_roi = roi
            best_score_params = params.copy()

    print(f"  Best scoring weights: CW={best_score_params['consensus_weight']}, "
          f"MW={best_score_params['ml_value_weight']}, "
          f"CRW={best_score_params['contrarian_weight']} "
          f"(ROI: {best_score_roi:.1f}%)")

    # Stage 2: Optimize bet structure
    print("\nStage 2: Optimizing bet structure...")
    best_bet_params = best_score_params.copy()
    best_bet_roi = best_score_roi

    stage2_grid = list(itertools.product(
        param_grid["exacta_width"],
        param_grid["exacta_bet"],
        [True, False],  # use_wheels
        param_grid["wheel_width"],
        param_grid["win_min_ml"],
        param_grid["win_bet"],
        param_grid["win_min_score"],
    ))

    for ew, eb, uw, ww, wml, wb, wms in stage2_grid:
        params = best_score_params.copy()
        params.update({
            "exacta_width": ew,
            "exacta_bet": eb,
            "use_wheels": uw,
            "wheel_width": ww,
            "win_min_ml": wml,
            "win_bet": wb,
            "win_min_score": wms,
        })

        total_net = 0
        total_wagered = 0
        for rd in race_days:
            result = run_backtest(rd, strategy_fn, scorer_fn, params, verbose=False)
            total_net += result["net"]
            total_wagered += result["wagered"]

        roi = (total_net / total_wagered * 100) if total_wagered > 0 else -999
        if roi > best_bet_roi:
            best_bet_roi = roi
            best_bet_params = params.copy()

    print(f"  Best bet structure: exacta_width={best_bet_params['exacta_width']}, "
          f"exacta_bet=${best_bet_params['exacta_bet']}, "
          f"wheels={best_bet_params['use_wheels']}, "
          f"win_ml>={best_bet_params['win_min_ml']}, "
          f"win_bet=${best_bet_params['win_bet']}, "
          f"min_score={best_bet_params['win_min_score']} "
          f"(ROI: {best_bet_roi:.1f}%)")

    # Stage 3: Optimize trifecta/superfecta
    print("\nStage 3: Optimizing exotic bets...")
    best_final_params = best_bet_params.copy()
    best_final_roi = best_bet_roi

    stage3_grid = list(itertools.product(
        param_grid["tri_min_starters"],
        param_grid["tri_bet"],
        param_grid["tri_width"],
        [True, False],  # use_supers
    ))

    for tms, tb, tw, us in stage3_grid:
        params = best_bet_params.copy()
        params.update({
            "tri_min_starters": tms,
            "tri_bet": tb,
            "tri_width": tw,
            "use_supers": us,
        })

        total_net = 0
        total_wagered = 0
        for rd in race_days:
            result = run_backtest(rd, strategy_fn, scorer_fn, params, verbose=False)
            total_net += result["net"]
            total_wagered += result["wagered"]

        roi = (total_net / total_wagered * 100) if total_wagered > 0 else -999
        if roi > best_final_roi:
            best_final_roi = roi
            best_final_params = params.copy()

    print(f"  Best exotic config: tri_starters>={best_final_params['tri_min_starters']}, "
          f"tri_bet=${best_final_params['tri_bet']}, "
          f"tri_width={best_final_params['tri_width']}, "
          f"supers={best_final_params['use_supers']} "
          f"(ROI: {best_final_roi:.1f}%)")

    return best_final_params, best_final_roi


def main():
    print("=" * 70)
    print("ENHANCED HORSE RACING STRATEGY BACKTESTER")
    print("=" * 70)

    # Load all available race day data
    race_days = []
    data_files = ["parx.json", "fair-grounds.json", "oaklawn.json"]

    for f in data_files:
        path = os.path.join(DATA_DIR, f)
        if os.path.exists(path):
            try:
                rd = load_race_day(path)
                if rd["races"]:
                    race_days.append(rd)
                    print(f"Loaded {rd['track']} ({rd['date']}): {len(rd['races'])} races")
            except Exception as e:
                print(f"Error loading {f}: {e}")

    if not race_days:
        print("No race data found!")
        return

    total_races = sum(len(rd["races"]) for rd in race_days)
    print(f"\nTotal: {len(race_days)} race days, {total_races} races")

    # =================================================================
    # TEST 1: Original strategy (baseline)
    # =================================================================
    print(f"\n{'='*70}")
    print("TEST 1: ORIGINAL STRATEGY (Expert Consensus Only)")
    print(f"{'='*70}")

    for rd in race_days:
        result = run_backtest(rd, strategy_original, verbose=True)
        print(f"\n{rd['track']} ({rd['date']}):")
        for d in result["details"]:
            print(d)
        print(f"\nTOTAL: Wagered ${result['wagered']:.2f}, "
              f"Returned ${result['returned']:.2f}, "
              f"Net {'+'if result['net']>0 else ''}${result['net']:.2f} "
              f"({result['roi']:.1f}% ROI)")

    # =================================================================
    # TEST 2: Enhanced V1 (consensus + ML value + contrarian)
    # =================================================================
    print(f"\n{'='*70}")
    print("TEST 2: ENHANCED V1 (Consensus + ML Value + Contrarian)")
    print(f"{'='*70}")

    default_params = {
        "consensus_weight": 2.0,
        "ml_value_weight": 1.5,
        "contrarian_weight": 1.0,
        "exacta_width": 3,
        "exacta_bet": 2.0,
        "use_wheels": True,
        "wheel_width": 3,
        "wheel_bet": 2.0,
        "win_min_ml": 3.0,
        "win_max_ml": 10.0,
        "win_bet": 8.0,
        "win_min_score": 4.0,
        "tri_min_starters": 7,
        "tri_bet": 1.0,
        "tri_width": 4,
        "use_supers": True,
    }

    for rd in race_days:
        result = run_backtest(rd, strategy_enhanced, score_enhanced_v1, default_params, verbose=True)
        print(f"\n{rd['track']} ({rd['date']}):")
        for d in result["details"]:
            print(d)
        print(f"\nTOTAL: Wagered ${result['wagered']:.2f}, "
              f"Returned ${result['returned']:.2f}, "
              f"Net {'+'if result['net']>0 else ''}${result['net']:.2f} "
              f"({result['roi']:.1f}% ROI)")

    # =================================================================
    # TEST 3: ML Contrarian Model
    # =================================================================
    print(f"\n{'='*70}")
    print("TEST 3: ML CONTRARIAN MODEL")
    print(f"{'='*70}")

    for rd in race_days:
        result = run_backtest(rd, strategy_enhanced, score_ml_contrarian, default_params, verbose=True)
        print(f"\n{rd['track']} ({rd['date']}):")
        for d in result["details"]:
            print(d)
        print(f"\nTOTAL: Wagered ${result['wagered']:.2f}, "
              f"Returned ${result['returned']:.2f}, "
              f"Net {'+'if result['net']>0 else ''}${result['net']:.2f} "
              f"({result['roi']:.1f}% ROI)")

    # =================================================================
    # PARAMETER SWEEP - Find optimal strategy
    # =================================================================
    print(f"\n{'='*70}")
    print("PARAMETER SWEEP: Finding Optimal Strategy")
    print(f"{'='*70}")

    # Test all three scoring models
    models = [
        ("Enhanced V1", score_enhanced_v1),
        ("Enhanced V2", score_enhanced_v2),
        ("ML Contrarian", score_ml_contrarian),
    ]

    best_overall_roi = -999
    best_overall_model = None
    best_overall_params = None

    for name, scorer in models:
        print(f"\n--- Sweeping {name} ---")
        params, roi = parameter_sweep(race_days, scorer, strategy_enhanced)
        print(f"\n  {name} BEST ROI: {roi:.1f}%")

        if roi > best_overall_roi:
            best_overall_roi = roi
            best_overall_model = (name, scorer)
            best_overall_params = params

    # =================================================================
    # FINAL RESULTS with optimal strategy
    # =================================================================
    print(f"\n{'='*70}")
    print(f"WINNING STRATEGY: {best_overall_model[0]}")
    print(f"ROI: {best_overall_roi:.1f}%")
    print(f"{'='*70}")

    print("\nOptimal Parameters:")
    for k, v in sorted(best_overall_params.items()):
        print(f"  {k}: {v}")

    print("\n--- Detailed Results Per Track ---")
    grand_wagered = 0
    grand_returned = 0

    for rd in race_days:
        result = run_backtest(rd, strategy_enhanced, best_overall_model[1],
                            best_overall_params, verbose=True)
        print(f"\n{rd['track']} ({rd['date']}):")
        for d in result["details"]:
            print(d)
        marker = "+" if result["net"] > 0 else ""
        print(f"\n  TOTAL: Wagered ${result['wagered']:.2f}, "
              f"Returned ${result['returned']:.2f}, "
              f"Net {marker}${result['net']:.2f} ({result['roi']:.1f}% ROI)")
        grand_wagered += result["wagered"]
        grand_returned += result["returned"]

    grand_net = grand_returned - grand_wagered
    grand_roi = (grand_net / grand_wagered * 100) if grand_wagered > 0 else 0

    print(f"\n{'='*70}")
    print(f"GRAND TOTAL ACROSS ALL DAYS:")
    print(f"  Wagered: ${grand_wagered:.2f}")
    print(f"  Returned: ${grand_returned:.2f}")
    marker = "+" if grand_net > 0 else ""
    print(f"  Net: {marker}${grand_net:.2f}")
    print(f"  ROI: {grand_roi:.1f}%")
    print(f"{'='*70}")

    # Save results
    output = {
        "winning_model": best_overall_model[0],
        "roi": round(best_overall_roi, 2),
        "params": best_overall_params,
        "grand_total": {
            "wagered": round(grand_wagered, 2),
            "returned": round(grand_returned, 2),
            "net": round(grand_net, 2),
            "roi": round(grand_roi, 2),
        },
    }

    results_path = os.path.join(SCRIPT_DIR, "enhanced_backtest_results.json")
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
