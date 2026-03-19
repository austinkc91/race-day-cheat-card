#!/usr/bin/env python3
"""
VALUE SCANNER — Live value bet detection for the Race Day Cheat Card

This module:
1. Fetches live tote board odds from the OTB API
2. Compares against expert consensus picks
3. Identifies VALUE BETS (when experts see something the public doesn't)
4. Returns actionable alerts

Usage:
    from value_scanner import scan_for_value
    alerts = scan_for_value("tampa-bay-downs")

Or standalone:
    python3 value_scanner.py tampa-bay-downs
"""

import json
import math
import os
import sys
import urllib.request
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# OTB API track IDs
OTB_TRACK_IDS = {
    "aqueduct": 1,
    "belmont-park": 10,
    "charles-town": 16,
    "churchill-downs": 17,
    "delta-downs": 21,
    "golden-gate-fields": 34,
    "gulfstream": 36,
    "gulfstream-park": 36,
    "laurel-park": 49,
    "penn-national": 62,
    "parx-racing": 63,
    "parx": 63,
    "remington-park": 73,
    "sam-houston": 79,
    "santa-anita": 80,
    "sunland-park": 91,
    "tampa-bay-downs": 92,
    "turf-paradise": 100,
    "turfway-park": 101,
    "will-rogers-downs": 104,
    "mahoning-valley": 216,
    "oaklawn": 999,  # Need to find correct ID
    "fair-grounds": 999,  # Need to find correct ID
}

# OTB live schedule API
OTB_SCHEDULE_URL = "https://ojlbo7v5hb.execute-api.us-west-2.amazonaws.com/current_races/v2"
OTB_RACE_URL = "https://json.offtrackbetting.com/tracks/v2/{track_id}/{date}.json"


def fetch_json(url, timeout=15):
    """Fetch JSON from URL."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.load(resp)
    except Exception as e:
        return None


def parse_num(val):
    """Parse MongoDB-style number."""
    if isinstance(val, dict):
        return float(val.get("$numberDouble", val.get("$numberInt", 0)))
    return float(val) if val else 0


def tote_odds_to_probability(win_pool_share):
    """
    Convert tote board odds to implied probability.
    Win pool share = amount bet on this horse / total pool
    Probability = pool_share (before takeout adjustment)
    """
    return win_pool_share


def win_payout_to_implied_prob(payout_on_2):
    """
    Convert $2 win payout to implied probability.
    e.g., $6.00 payout = 2/1 odds = ~33% probability
    Includes takeout, so actual probability is higher.
    """
    if payout_on_2 <= 2.0:
        return 0.90
    odds = (payout_on_2 - 2.0) / 2.0
    # Raw implied probability (includes takeout)
    return 1.0 / (1.0 + odds)


def expert_consensus_to_probability(num_sources, total_sources=6, is_top_pick=True):
    """
    Convert expert consensus to estimated probability.

    Based on analysis: when N out of 6 expert sources pick a horse:
    - 6/6: The horse wins ~40-45% of the time
    - 5/6: ~30-35%
    - 4/6: ~22-28%
    - 3/6: ~15-20%
    - 2/6: ~10-12%
    - 1/6: ~5-8%

    These are calibrated estimates based on expert accuracy research.
    """
    if is_top_pick:
        prob_map = {6: 0.42, 5: 0.32, 4: 0.24, 3: 0.17, 2: 0.11, 1: 0.07, 0: 0.03}
    else:
        # If horse is experts' 2nd or 3rd choice, lower probabilities
        prob_map = {6: 0.25, 5: 0.20, 4: 0.15, 3: 0.10, 2: 0.06, 1: 0.04, 0: 0.02}

    return prob_map.get(num_sources, 0.03)


def calculate_value(expert_prob, tote_implied_prob, takeout=0.17):
    """
    Calculate the value (edge) of a bet.

    edge = (true_prob * payout - 1) / 1
    Simplified: edge = expert_prob / tote_implied_prob - 1

    Positive edge = value bet.
    We also account for the track takeout.
    """
    if tote_implied_prob <= 0:
        return 0

    # Adjust tote probability for takeout
    # The tote odds already include takeout, so the "true" implied prob is lower
    adjusted_tote = tote_implied_prob * (1 - takeout)

    # Edge = our probability estimate vs market
    edge = (expert_prob - adjusted_tote) / adjusted_tote

    return edge


def fetch_live_tote_odds(track_slug):
    """
    Fetch live tote board odds for a track.
    Returns dict of {race_num: {horse_name: odds}} or None.

    NOTE: The OTB API may not have live odds for in-progress races.
    For upcoming races, odds pools may be available.
    """
    track_id = OTB_TRACK_IDS.get(track_slug)
    if not track_id or track_id == 999:
        return None

    date_str = datetime.now().strftime("%Y%m%d")
    url = OTB_RACE_URL.format(track_id=track_id, date=date_str)
    data = fetch_json(url)

    if not data or not data.get("events"):
        return None

    result = {}
    for event in data["events"]:
        race_num = int(parse_num(event.get("eventNo", 0)))
        runners = event.get("runners", [])

        # If runners are populated (live data), parse odds
        if runners:
            race_odds = {}
            for runner in runners:
                name = runner.get("runnerName", "")
                ml_odds = runner.get("morningLineOdds", "")
                # If live odds available:
                live_odds = runner.get("currentOdds", ml_odds)
                if name and ml_odds:
                    race_odds[name] = {
                        "ml_odds": ml_odds,
                        "live_odds": live_odds,
                        "program": runner.get("programNumber", ""),
                    }
            if race_odds:
                result[race_num] = race_odds

        # If results are in (race completed), get actual payouts
        results_data = event.get("results", {})
        finishers = results_data.get("finisher", [])
        if finishers and race_num not in result:
            race_results = {}
            for f in finishers:
                name = f.get("runnerName", "")
                pos = int(parse_num(f.get("finishPosition", 99)))
                win_p = float(f.get("winAmount", 0) or 0)
                race_results[name] = {
                    "position": pos,
                    "win_payout": win_p,
                    "program": f.get("programNumber", ""),
                }
            result[race_num] = {"status": "completed", "finishers": race_results}

    return result


def load_cheat_card_data(track_slug):
    """Load the current cheat card data for a track."""
    data_path = f"/tmp/race_day_data/{track_slug}.json"
    try:
        with open(data_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def scan_for_value(track_slug, cheat_card_data=None):
    """
    Scan for value bets by comparing expert consensus vs tote odds.

    Returns list of value bet alerts:
    [{
        "race_num": int,
        "horse": str,
        "expert_sources": int,
        "expert_prob": float,
        "tote_implied_prob": float,
        "edge": float,
        "bet_type": "WIN" or "PLACE",
        "suggested_amount": float,
        "reason": str,
    }]
    """
    alerts = []

    # Load cheat card data if not provided
    if cheat_card_data is None:
        cheat_card_data = load_cheat_card_data(track_slug)

    if not cheat_card_data:
        return alerts

    races = cheat_card_data.get("races", [])

    # Fetch live tote odds
    live_odds = fetch_live_tote_odds(track_slug)

    for race in races:
        race_num = race.get("race_number", 0)
        race_type = race.get("race_type", "")
        status = race.get("status", "PENDING")

        if status == "COMPLETED":
            continue

        horses = race.get("horses", [])

        for horse_data in horses:
            horse_name = horse_data.get("name", "")
            consensus = horse_data.get("consensus", {})
            sources_picking = consensus.get("sources_count", 0)
            total_sources = consensus.get("total_sources", 6)
            ml_odds_str = horse_data.get("morning_line", "")
            is_top_pick = consensus.get("is_top_pick", False)

            # Calculate expert probability
            expert_prob = expert_consensus_to_probability(
                sources_picking, total_sources, is_top_pick
            )

            # Get tote/ML odds
            ml_odds = None
            if ml_odds_str:
                try:
                    if "/" in str(ml_odds_str):
                        parts = str(ml_odds_str).split("/")
                        ml_odds = float(parts[0]) / float(parts[1])
                    elif "-" in str(ml_odds_str):
                        parts = str(ml_odds_str).split("-")
                        ml_odds = float(parts[0]) / float(parts[1])
                    else:
                        ml_odds = float(ml_odds_str)
                except (ValueError, ZeroDivisionError):
                    pass

            # Try live odds first, fall back to ML
            tote_implied = None
            if live_odds and race_num in live_odds:
                race_odds = live_odds[race_num]
                if isinstance(race_odds, dict) and horse_name in race_odds:
                    horse_odds = race_odds[horse_name]
                    # Parse live odds to probability
                    try:
                        odds_val = float(str(horse_odds.get("live_odds", "")).replace("/1", ""))
                        tote_implied = 1.0 / (1.0 + odds_val)
                    except (ValueError, TypeError):
                        pass

            if tote_implied is None and ml_odds is not None:
                tote_implied = 1.0 / (1.0 + ml_odds)

            if tote_implied is None or expert_prob < 0.10:
                continue

            # Calculate edge
            edge = calculate_value(expert_prob, tote_implied)

            # Only alert on significant edges
            if edge >= 0.15 and sources_picking >= 3:
                alert = {
                    "race_num": race_num,
                    "horse": horse_name,
                    "race_type": race_type,
                    "expert_sources": sources_picking,
                    "expert_prob": round(expert_prob, 3),
                    "tote_implied_prob": round(tote_implied, 3),
                    "edge": round(edge, 3),
                    "edge_pct": f"{edge*100:.0f}%",
                    "bet_type": "WIN",
                    "suggested_amount": 5.0 if edge >= 0.30 else 2.0,
                    "reason": (
                        f"{sources_picking} of {total_sources} experts pick {horse_name} "
                        f"but tote odds suggest only {tote_implied*100:.0f}% chance. "
                        f"Expert estimate: {expert_prob*100:.0f}%. Edge: {edge*100:.0f}%."
                    ),
                }
                alerts.append(alert)

    # Sort by edge (best value first)
    alerts.sort(key=lambda x: -x["edge"])

    # Limit to top 3 per day
    return alerts[:3]


def format_alerts(alerts):
    """Format value alerts for display."""
    if not alerts:
        return "No value bets identified. Skip this card."

    lines = ["VALUE BETS DETECTED:"]
    for i, a in enumerate(alerts, 1):
        lines.append(
            f"\n{i}. R{a['race_num']} - {a['horse']} ({a['race_type']})"
        )
        lines.append(f"   Expert consensus: {a['expert_sources']}/6 sources")
        lines.append(f"   Expert probability: {a['expert_prob']*100:.0f}%")
        lines.append(f"   Tote implied: {a['tote_implied_prob']*100:.0f}%")
        lines.append(f"   Edge: +{a['edge_pct']}")
        lines.append(f"   Bet: ${a['suggested_amount']:.0f} {a['bet_type']}")
        lines.append(f"   {a['reason']}")

    lines.append("\nRULES:")
    lines.append("- Max 3 value bets per day")
    lines.append("- WIN bets only (lower takeout)")
    lines.append("- $2-5 per bet based on edge size")
    lines.append("- Skip days with 0 value bets")

    return "\n".join(lines)


if __name__ == "__main__":
    track = sys.argv[1] if len(sys.argv) > 1 else "tampa-bay-downs"
    print(f"Scanning {track} for value bets...")

    alerts = scan_for_value(track)
    print(format_alerts(alerts))

    if alerts:
        # Save alerts
        output_path = os.path.join(SCRIPT_DIR, "value_alerts.json")
        with open(output_path, "w") as f:
            json.dump(alerts, f, indent=2)
        print(f"\nAlerts saved to {output_path}")
