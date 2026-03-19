#!/usr/bin/env python3
"""
Scrape massive race dataset from OTB JSON API.
Collects full finishing orders + exacta/trifecta/superfecta payouts.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# US Thoroughbred tracks with OTB IDs
TRACKS = {
    1: "Aqueduct",
    10: "Belmont Park",
    16: "Charles Town",
    21: "Delta Downs",
    34: "Golden Gate Fields",
    36: "Gulfstream Park",
    49: "Laurel Park",
    62: "Penn National",
    63: "Parx Racing",
    73: "Remington Park",
    79: "Sam Houston",
    80: "Santa Anita",
    91: "Sunland Park",
    92: "Tampa Bay Downs",
    100: "Turf Paradise",
    101: "Turfway Park",
    104: "Will Rogers Downs",
    216: "Mahoning Valley",
    13: "Gulfstream Park West",
}

BASE_URL = "https://json.offtrackbetting.com/tracks/v2/{track_id}/{date}.json"


def parse_num(val):
    """Parse MongoDB-style number or plain number."""
    if isinstance(val, dict):
        return float(val.get("$numberDouble", val.get("$numberInt", 0)))
    return float(val) if val else 0


def parse_race(event):
    """Parse a single race event into our format."""
    race_num = int(parse_num(event.get("eventNo", 0)))
    conditions = event.get("conditions", "")
    distance = event.get("distance", "")

    # Determine race type from conditions
    cond_upper = conditions.upper()
    if "MAIDEN" in cond_upper and "CLAIMING" in cond_upper:
        race_type = "MC"
    elif "MAIDEN" in cond_upper and "SPECIAL" in cond_upper:
        race_type = "MSW"
    elif "MAIDEN" in cond_upper and "ALLOWANCE" in cond_upper:
        race_type = "MSW"
    elif "MAIDEN" in cond_upper:
        race_type = "MSW"
    elif "STARTER" in cond_upper and ("OPTIONAL" in cond_upper or "ALLOW" in cond_upper):
        race_type = "SOC"
    elif "STAKE" in cond_upper or "GRADE" in cond_upper or "HANDICAP" in cond_upper:
        race_type = "STK"
    elif "ALLOWANCE" in cond_upper and "OPTIONAL" in cond_upper:
        race_type = "AOC"
    elif "ALLOWANCE" in cond_upper:
        race_type = "ALW"
    elif "CLAIMING" in cond_upper:
        race_type = "CLM"
    elif "STARTER" in cond_upper:
        race_type = "SOC"
    else:
        race_type = "OTH"

    results = event.get("results", {})
    finishers = results.get("finisher", [])
    dividends = results.get("dividends", [])
    scratches = results.get("scratches", [])

    if not finishers:
        return None

    # Count starters (finishers + scratches gives total field, but we want actual starters)
    starters = len(finishers)

    # Build finishing order
    finish_order = []
    wps_data = {}
    for f in sorted(finishers, key=lambda x: parse_num(x.get("finishPosition", 99))):
        name = f.get("runnerName", "Unknown")
        pos = int(parse_num(f.get("finishPosition", 99)))
        prog = f.get("programNumber", "")
        finish_order.append({
            "name": name,
            "position": pos,
            "program": prog,
            "jockey": f.get("jockey", ""),
        })
        if f.get("winAmount"):
            wps_data["win"] = float(f["winAmount"])
        if pos <= 3:
            if f.get("placeAmount"):
                wps_data[f"place_{pos}"] = float(f["placeAmount"])
            if f.get("showAmount"):
                wps_data[f"show_{pos}"] = float(f["showAmount"])

    # Parse exotic payouts
    exotic_pays = {}
    for div in dividends:
        bet_type = div.get("betType", "")
        amount = parse_num(div.get("amount", 0))
        base = parse_num(div.get("baseAmount", 200))
        finisher_str = div.get("finishers", "")

        if bet_type == "EX":
            # Normalize to $2 base
            exotic_pays["exacta"] = amount * (2.0 / (base / 100)) if base else amount
            exotic_pays["exacta_raw"] = amount
            exotic_pays["exacta_base"] = base / 100 if base else 2
        elif bet_type == "TR":
            exotic_pays["trifecta"] = amount * (2.0 / (base / 100)) if base else amount
            exotic_pays["trifecta_raw"] = amount
            exotic_pays["trifecta_base"] = base / 100 if base else 2
        elif bet_type == "SU":
            exotic_pays["superfecta"] = amount * (2.0 / (base / 100)) if base else amount
            exotic_pays["superfecta_raw"] = amount
            exotic_pays["superfecta_base"] = base / 100 if base else 2

    # Skip harness races (TROT/PACE)
    if "TROT" in cond_upper or "PACE:" in cond_upper:
        return None

    return {
        "race_num": race_num,
        "race_type": race_type,
        "conditions": conditions[:200],
        "distance": distance,
        "starters": starters,
        "finish_order": finish_order,
        "wps": wps_data,
        "exotics": exotic_pays,
    }


def scrape_track_date(track_id, date_str):
    """Scrape a single track on a single date. Returns list of races."""
    url = BASE_URL.format(track_id=track_id, date=date_str)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []

    events = data.get("events", [])
    races = []
    for event in events:
        race = parse_race(event)
        if race:
            races.append(race)
    return races


def scrape_all(start_date, end_date, output_path=None):
    """Scrape all tracks for a date range."""
    if output_path is None:
        output_path = os.path.join(SCRIPT_DIR, "otb_race_data.json")

    # Load existing data if present
    existing = {}
    if os.path.exists(output_path):
        with open(output_path) as f:
            existing = json.load(f)

    all_data = existing.get("race_days", {})
    current = start_date
    total_new_races = 0

    while current <= end_date:
        date_str = current.strftime("%Y%m%d")
        date_display = current.strftime("%Y-%m-%d")

        for track_id, track_name in TRACKS.items():
            key = f"{date_display} {track_name}"
            if key in all_data:
                continue  # Already scraped

            races = scrape_track_date(track_id, date_str)
            if races:
                all_data[key] = races
                total_new_races += len(races)
                print(f"  {key}: {len(races)} races")
                time.sleep(0.3)  # Be polite

        current += timedelta(days=1)

    # Save
    output = {
        "metadata": {
            "scraped_at": datetime.now().isoformat(),
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_track_days": len(all_data),
            "total_races": sum(len(v) for v in all_data.values()),
        },
        "race_days": all_data,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=1)

    print(f"\nSaved {len(all_data)} track-days, {sum(len(v) for v in all_data.values())} races to {output_path}")
    print(f"New races this run: {total_new_races}")
    return output


if __name__ == "__main__":
    # Scrape Feb 1 through March 18, 2026
    start = datetime(2026, 2, 1)
    end = datetime(2026, 3, 18)
    print(f"Scraping {len(TRACKS)} tracks from {start.date()} to {end.date()}...")
    scrape_all(start, end)
