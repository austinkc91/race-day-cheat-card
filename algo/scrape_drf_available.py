#!/usr/bin/env python3
"""
Scrape ALL available DRF race results for Oaklawn Park and Fair Grounds.
Uses the DRF tracks API to get known race dates, then fetches each one.
"""

import json
import re
import time
import os
import sys
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.drf.com/results",
}

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "drf_real_data.json")


def classify_race_type(race_class: str) -> str:
    rc = race_class.upper().strip()
    if "MAIDEN SPECIAL" in rc or "MAIDEN SP" in rc:
        return "MSW"
    elif "MAIDEN" in rc and ("CLAIM" in rc or "OPTIONAL" in rc):
        return "MC"
    elif "MAIDEN" in rc:
        return "MSW"
    elif "STARTER" in rc and "ALLOWANCE" in rc:
        return "SA"
    elif "STARTER" in rc:
        return "SA"
    elif "ALLOWANCE" in rc and "OPTIONAL" in rc:
        return "AOC"
    elif "ALLOWANCE" in rc:
        return "ALW"
    elif any(g in rc for g in ["G1 ", "G2 ", "G3 ", "GRADE"]):
        return "GST"
    elif "STAKES" in rc or " S." in rc:
        return "STK"
    elif "CLAIM" in rc:
        return "CLM"
    else:
        return "OTH"


def count_starters(race: dict) -> int:
    runners = len(race.get("runners", []))
    also_ran = race.get("alsoRan", "") or ""
    if also_ran.strip():
        names = re.split(r',\s*(?:and\s+)?|\s+and\s+', also_ran.strip())
        names = [n.strip() for n in names if n.strip()]
        return runners + len(names)
    return runners


def get_available_dates():
    """Get all available race dates from DRF tracks API."""
    r = requests.get("https://www.drf.com/results/raceTracks/country/USA", headers=HEADERS, timeout=15)
    data = r.json()

    dates = []
    for key in data["raceTracks"]:
        tracks = data["raceTracks"][key]
        if not isinstance(tracks, list):
            continue
        for track in tracks:
            if not isinstance(track, dict):
                continue
            if track.get("trackId") not in ("OP", "FG"):
                continue
            track_id = track["trackId"]
            for card in track.get("cards", []):
                rd = card["raceDate"]
                # DRF months are 0-indexed (Java Calendar)
                month = rd["month"] + 1
                date_str = f"{month:02d}-{rd['day']:02d}-{rd['year']}"
                dates.append({
                    "track_id": track_id,
                    "date_str": date_str,
                    "race_count": len(card.get("raceList", [])),
                    "final": card.get("final", False),
                })

    # Only get completed races
    dates = [d for d in dates if d["final"]]
    return dates


def fetch_results(track_id: str, date_str: str) -> list:
    url = f"https://www.drf.com/results/resultDetails/id/{track_id}/country/USA/date/{date_str}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        data = resp.json()
        races = data.get("races", [])
        if not races:
            return []

        results = []
        for r in races:
            runners = r.get("runners", [])
            if not runners:
                continue
            winner = runners[0]
            win_pay = winner.get("winPayoff", 0) or 0
            place_pay = winner.get("placePayoff", 0) or 0
            show_pay = winner.get("showPayoff", 0) or 0
            if win_pay <= 0:
                continue

            race_class = (r.get("raceClass", "") or "").strip()
            race_type = classify_race_type(race_class)
            starters = count_starters(r)
            track_cond = (r.get("trackConditionDescription", "") or "").strip()
            surface = (r.get("surfaceDescription", "") or "").strip()

            # Get 2nd and 3rd place info
            place_horse = runners[1]["horseName"].strip() if len(runners) > 1 else ""
            show_horse = runners[2]["horseName"].strip() if len(runners) > 2 else ""

            results.append({
                "race_num": r["raceKey"]["raceNumber"],
                "winner": winner["horseName"].strip(),
                "win_pay": round(win_pay, 2),
                "place_pay": round(place_pay, 2),
                "show_pay": round(show_pay, 2),
                "race_type": race_type,
                "race_class": race_class,
                "starters": starters,
                "surface": surface,
                "track_condition": track_cond,
                "distance": (r.get("distanceDescription", "") or "").strip(),
                "purse": (r.get("totalPurse", "") or ""),
                "place_horse": place_horse,
                "show_horse": show_horse,
            })

        return results
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        return []


def main():
    print("=" * 60)
    print("DRF RACE DATA SCRAPER - ALL AVAILABLE DATES")
    print("=" * 60)

    # Get available dates
    available = get_available_dates()
    print(f"\nFound {len(available)} available race dates for OP + FG")

    all_data = {}
    total_races = 0

    for i, entry in enumerate(available):
        track_id = entry["track_id"]
        date_str = entry["date_str"]

        time.sleep(0.3)
        results = fetch_results(track_id, date_str)

        if results:
            track_name = "Oaklawn Park" if track_id == "OP" else "Fair Grounds"
            cond = results[0].get("track_condition", "")
            day_key = f"{date_str} {track_name}"
            if cond.lower() not in ("fast", "firm", "good", ""):
                day_key += f" ({cond})"

            all_data[day_key] = results
            total_races += len(results)
            print(f"[{i+1}/{len(available)}] {day_key}: {len(results)} races (Total: {len(all_data)} days, {total_races} races)")
        else:
            print(f"[{i+1}/{len(available)}] {track_id} {date_str}: no results")

    # Save
    output = {
        "metadata": {
            "total_race_days": len(all_data),
            "total_races": total_races,
            "source": "DRF",
        },
        "race_days": all_data,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"DONE! {len(all_data)} race days, {total_races} races")
    print(f"Saved to: {OUTPUT_FILE}")

    # Compute stats
    all_payouts = []
    type_counts = {}
    for day_races in all_data.values():
        for race in day_races:
            all_payouts.append(race["win_pay"])
            rt = race["race_type"]
            type_counts[rt] = type_counts.get(rt, 0) + 1

    if all_payouts:
        avg = sum(all_payouts) / len(all_payouts)
        non_chalk = sum(1 for p in all_payouts if p >= 5.0)
        print(f"\nAvg win payout: ${avg:.2f}")
        print(f"Non-chalk winners (>=$5): {non_chalk}/{len(all_payouts)} ({100*non_chalk/len(all_payouts):.1f}%)")
        print(f"Race types: {json.dumps(type_counts, indent=2)}")


if __name__ == "__main__":
    main()
