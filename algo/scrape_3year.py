#!/usr/bin/env python3
"""
3-Year Historical Race Data Scraper
Scrapes Oaklawn Park (OP) and Fair Grounds (FG) results from DRF
for the last 3 years (March 2023 - March 2026).

Output: historical_3year_data.json
"""

import json
import re
import time
import os
import sys
from datetime import datetime, timedelta
import requests

TRACKS = {
    "OP": "Oaklawn Park",
    "FG": "Fair Grounds",
}

# Racing seasons (approximate):
# Oaklawn: Late Dec - Early May (Fri/Sat/Sun typically, some Thu)
# Fair Grounds: Late Nov - Late March (Thu-Sun typically)
# We'll try every day during these windows and skip if no data

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.drf.com/results",
}

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "historical_3year_data.json")
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "scrape_progress.json")


def classify_race_type(race_class: str) -> str:
    """Convert DRF race class string to our shorthand."""
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
        return "GST"  # Graded stakes
    elif "STAKES" in rc or " S." in rc:
        return "STK"
    elif "CLAIM" in rc:
        return "CLM"
    else:
        return "OTH"


def count_starters(race: dict) -> int:
    """Count total starters from runners + alsoRan."""
    runners = len(race.get("runners", []))
    also_ran = race.get("alsoRan", "") or ""
    if also_ran.strip():
        names = re.split(r',\s*(?:and\s+)?|\s+and\s+', also_ran.strip())
        names = [n.strip() for n in names if n.strip()]
        return runners + len(names)
    return runners


def fetch_results(track_id: str, date_str: str) -> list:
    """Fetch race results for a track on a given date.
    date_str format: MM-DD-YYYY
    Returns list of race dicts or empty list if no races.
    """
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

            # Skip if no win payoff (cancelled/no contest)
            if win_pay <= 0:
                continue

            race_class = (r.get("raceClass", "") or "").strip()
            race_type = classify_race_type(race_class)
            starters = count_starters(r)

            track_condition = (r.get("trackConditionDescription", "") or "").strip()
            surface = (r.get("surfaceDescription", "") or "").strip()

            # Get exotic payoffs
            payoffs = r.get("payoffDTOs", []) or r.get("payoffs", []) or []
            exotic_data = {}
            if payoffs:
                for p in payoffs:
                    wager_type = (p.get("wagerType", "") or p.get("type", "") or "").upper()
                    payoff = p.get("payoff", 0) or p.get("amount", 0) or 0
                    base_amount = p.get("baseAmount", 2) or 2
                    if wager_type and payoff > 0:
                        exotic_data[wager_type] = {"payoff": payoff, "base": base_amount}

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
                "track_condition": track_condition,
                "distance": (r.get("distanceDescription", "") or "").strip(),
                "purse": (r.get("totalPurse", "") or ""),
                "exotics": exotic_data,
            })

        return results
    except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
        print(f"  Error fetching {track_id} {date_str}: {e}", file=sys.stderr)
        return []


def generate_date_ranges():
    """Generate all dates to check for the last 3 years.
    Oaklawn: Dec - May each year
    Fair Grounds: Nov - March each year
    """
    dates_to_check = []

    # 3 racing seasons: 2023-24, 2024-25, 2025-26
    for year_start in [2022, 2023, 2024, 2025]:
        # Oaklawn Park (OP): runs ~late Dec to early May
        op_start = datetime(year_start, 12, 15)
        op_end = datetime(year_start + 1, 5, 10)
        d = op_start
        while d <= op_end:
            dates_to_check.append(("OP", d))
            d += timedelta(days=1)

        # Fair Grounds (FG): runs ~late Nov to late March
        fg_start = datetime(year_start, 11, 15)
        fg_end = datetime(year_start + 1, 3, 31)
        d = fg_start
        while d <= fg_end:
            dates_to_check.append(("FG", d))
            d += timedelta(days=1)

    # Don't go past today (March 15, 2026)
    today = datetime(2026, 3, 15)
    dates_to_check = [(t, d) for t, d in dates_to_check if d <= today]

    # Sort by date
    dates_to_check.sort(key=lambda x: (x[1], x[0]))

    return dates_to_check


def load_progress():
    """Load progress from previous run."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed": [], "data": {}}


def save_progress(progress):
    """Save progress to file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


def main():
    print("=" * 60)
    print("3-YEAR HISTORICAL RACE DATA SCRAPER")
    print("Tracks: Oaklawn Park (OP) + Fair Grounds (FG)")
    print("Period: Dec 2022 - March 2026")
    print("=" * 60)

    all_dates = generate_date_ranges()
    print(f"\nTotal date/track combos to check: {len(all_dates)}")

    # Load previous progress
    progress = load_progress()
    completed_keys = set(progress["completed"])
    all_data = progress["data"]

    total_races = sum(len(v) for v in all_data.values())
    total_days = len(all_data)
    skipped = 0
    errors = 0

    print(f"Resuming from: {total_days} race days, {total_races} races already scraped")

    for i, (track_id, date) in enumerate(all_dates):
        date_str = date.strftime("%m-%d-%Y")
        key = f"{track_id}_{date_str}"

        if key in completed_keys:
            skipped += 1
            continue

        # Rate limit: ~0.5 sec between requests
        time.sleep(0.5)

        results = fetch_results(track_id, date_str)

        completed_keys.add(key)
        progress["completed"].append(key)

        if results:
            day_key = f"{date.strftime('%Y-%m-%d')} {TRACKS[track_id]}"
            if track_condition := results[0].get("track_condition", ""):
                if track_condition.lower() not in ("fast", "firm", "good"):
                    day_key += f" ({track_condition})"

            all_data[day_key] = results
            total_races += len(results)
            total_days += 1

            print(f"[{i+1}/{len(all_dates)}] {day_key}: {len(results)} races (Total: {total_days} days, {total_races} races)")

        # Save progress every 20 requests
        if (i - skipped) % 20 == 0 and (i - skipped) > 0:
            progress["data"] = all_data
            save_progress(progress)
            print(f"  ... progress saved ({total_days} days, {total_races} races)")

    # Final save
    progress["data"] = all_data
    save_progress(progress)

    # Write final output
    output = {
        "metadata": {
            "tracks": list(TRACKS.keys()),
            "period": "Dec 2022 - Mar 2026",
            "total_race_days": total_days,
            "total_races": total_races,
            "scraped_at": datetime.now().isoformat(),
        },
        "race_days": all_data,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"SCRAPING COMPLETE!")
    print(f"Total race days: {total_days}")
    print(f"Total races: {total_races}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'=' * 60}")

    # Print summary by track/year
    track_year_counts = {}
    for day_key, races in all_data.items():
        year = day_key[:4]
        track = "OP" if "Oaklawn" in day_key else "FG"
        k = f"{track} {year}"
        if k not in track_year_counts:
            track_year_counts[k] = {"days": 0, "races": 0}
        track_year_counts[k]["days"] += 1
        track_year_counts[k]["races"] += len(races)

    print("\nBreakdown by track/year:")
    for k in sorted(track_year_counts.keys()):
        v = track_year_counts[k]
        print(f"  {k}: {v['days']} days, {v['races']} races")


if __name__ == "__main__":
    main()
