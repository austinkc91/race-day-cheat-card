#!/usr/bin/env python3
"""
Scrape race data WITH morning line odds from Horse Racing Nation.
This gives us the ML odds we need for realistic strategy testing.
"""

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TRACKS = [
    "tampa-bay-downs",
    "gulfstream-park",
    "parx-racing",
    "laurel-park",
    "santa-anita",
    "aqueduct",
    "penn-national",
    "charles-town",
    "turfway-park",
    "mahoning-valley",
    "turf-paradise",
    "sam-houston",
    "sunland-park",
    "delta-downs",
    "remington-park",
    "golden-gate-fields",
    "will-rogers-downs",
    "oaklawn-park",
    "fair-grounds",
]

BASE_URL = "https://entries.horseracingnation.com/entries-results/{track}/{date}"


def fetch_page(url):
    """Fetch a page and return its text content."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def parse_ml_odds(odds_str):
    """Convert fractional odds string to decimal. e.g. '5/2' -> 2.5, '1/1' -> 1.0"""
    odds_str = odds_str.strip().replace(" ", "")
    if "/" in odds_str:
        parts = odds_str.split("/")
        try:
            return float(parts[0]) / float(parts[1])
        except (ValueError, ZeroDivisionError):
            return None
    try:
        return float(odds_str)
    except ValueError:
        return None


def scrape_with_webfetch(track, date_str):
    """
    We'll use the WebFetch approach - fetch page and parse HTML.
    Returns list of races with ML odds and results.
    """
    url = BASE_URL.format(track=track, date=date_str)
    html = fetch_page(url)
    if not html:
        return []

    # Check if page has results
    if "No entries" in html or "no results" in html.lower():
        return []
    if "entries-results" not in html.lower() and "race " not in html.lower():
        return []

    # We need to parse the HTML for race data
    # This is complex - let's save the HTML and parse it
    return html


def main():
    output_path = os.path.join(SCRIPT_DIR, "hrn_pages.json")

    # Dates to scrape
    start = datetime(2026, 2, 15)
    end = datetime(2026, 3, 18)

    pages = {}
    current = start
    total = 0

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        for track in TRACKS:
            key = f"{date_str}_{track}"
            url = BASE_URL.format(track=track, date=date_str)

            html = fetch_page(url)
            if html and len(html) > 5000 and "Race 1" in html:
                pages[key] = url
                total += 1
                print(f"  Found: {key}")
                time.sleep(0.5)

        current += timedelta(days=1)

    print(f"\nFound {total} track-days with results")

    # Save URLs for WebFetch processing
    with open(output_path, "w") as f:
        json.dump(pages, f, indent=2)

    print(f"URLs saved to {output_path}")


if __name__ == "__main__":
    main()
