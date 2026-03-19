#!/usr/bin/env python3
"""
Build a comprehensive race dataset by combining:
1. OTB data (3,166 races with finishing orders + exotic payouts)
2. HRN data (ML odds for all horses)

We match races between the two sources to get complete data:
ML odds + finishing order + exotic payouts.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Track name mapping: OTB name -> HRN slug
TRACK_MAP = {
    "Tampa Bay Downs": "tampa-bay-downs",
    "Gulfstream Park": "gulfstream-park",
    "Parx Racing": "parx-racing",
    "Laurel Park": "laurel-park",
    "Santa Anita": "santa-anita",
    "Aqueduct": "aqueduct",
    "Penn National": "penn-national",
    "Charles Town": "charles-town",
    "Turfway Park": "turfway-park",
    "Mahoning Valley": "mahoning-valley",
    "Turf Paradise": "turf-paradise",
    "Sam Houston": "sam-houston",
    "Sunland Park": "sunland-park",
    "Delta Downs": "delta-downs",
    "Remington Park": "remington-park",
    "Golden Gate Fields": "golden-gate-fields",
    "Will Rogers Downs": "will-rogers-downs",
}

HRN_URL = "https://entries.horseracingnation.com/entries-results/{track}/{date}"


def parse_fractional_odds(odds_str):
    """Convert '5/2' to 2.5, '1/1' to 1.0, '15/1' to 15.0"""
    if not odds_str:
        return None
    odds_str = odds_str.strip()
    if "/" in odds_str:
        parts = odds_str.split("/")
        try:
            return float(parts[0]) / float(parts[1])
        except:
            return None
    try:
        return float(odds_str)
    except:
        return None


def load_otb_data():
    """Load the OTB scraped data."""
    path = os.path.join(SCRIPT_DIR, "otb_race_data.json")
    with open(path) as f:
        return json.load(f)


def main():
    otb = load_otb_data()
    print(f"OTB data: {otb['metadata']['total_track_days']} track-days, {otb['metadata']['total_races']} races")

    # Find which track-days we need ML data for
    # Prioritize CLM-heavy cards with 8+ races
    candidates = []
    for day_key, races in otb["race_days"].items():
        # Parse the date and track from the key (format: "2026-03-14 Tampa Bay Downs")
        parts = day_key.split(" ", 1)
        if len(parts) != 2:
            continue
        date_str, track_name = parts
        if track_name not in TRACK_MAP:
            continue

        clm_count = sum(1 for r in races if r["race_type"] in ("CLM", "MC", "SOC"))
        if len(races) >= 6 and clm_count >= 3:
            candidates.append({
                "key": day_key,
                "date": date_str,
                "track": track_name,
                "hrn_slug": TRACK_MAP[track_name],
                "races": len(races),
                "clm_races": clm_count,
            })

    candidates.sort(key=lambda x: x["clm_races"], reverse=True)
    print(f"\nFound {len(candidates)} candidate track-days for ML scraping")
    print("Top 30 by CLM count:")
    for c in candidates[:30]:
        print(f"  {c['key']}: {c['races']} races ({c['clm_races']} CLM/MC/SOC)")

    # Save candidate URLs for manual WebFetch
    urls = []
    for c in candidates[:50]:  # Top 50
        url = HRN_URL.format(track=c["hrn_slug"], date=c["date"])
        urls.append({"key": c["key"], "url": url, "races": c["races"], "clm": c["clm_races"]})

    output = os.path.join(SCRIPT_DIR, "hrn_urls_to_scrape.json")
    with open(output, "w") as f:
        json.dump(urls, f, indent=2)

    print(f"\nSaved {len(urls)} URLs to {output}")
    print("Use WebFetch to scrape these and extract ML odds")


if __name__ == "__main__":
    main()
