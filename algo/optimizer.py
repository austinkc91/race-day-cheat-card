#!/usr/bin/env python3
"""
Horse Racing Backtest Optimizer v1.0
27 race days, 250+ races across Oaklawn Park + Fair Grounds
Feb 6 - Mar 15, 2026

Continuously loops through parameter combinations to find the
strategy that maximizes profit. Optimizes:
- Odds thresholds (min/max odds to bet)
- Bet sizing (flat vs scaled)
- Race type filters
- Field size filters
- Place vs Win allocation
- Value score thresholds
- Longshot saver thresholds
"""

import json
import os
import random
import copy
import math
from itertools import product as iter_product
from datetime import datetime

# ============================================================
# COMPLETE RACE DATA - 27 RACE DAYS, 250+ RACES
# ============================================================
# Format: (winner, win_payout, place_payout, show_payout, race_type, starters)

RACE_DATA = {
    # === OAKLAWN PARK ===
    "2026-02-06 Oaklawn (Fri)": [
        ("Reckless", 9.20, 4.60, 3.40, "MC", 12),
        ("Patch O'Brien", 143.40, 43.40, 18.00, "CLM", 14),
        ("Nicholai", 13.80, 7.20, 5.20, "AOC", 10),
        ("Eglise", 4.00, 2.40, 2.40, "CLM", 14),
        ("Top Level", 17.20, 10.00, 5.60, "MSW", 11),
        ("Search Party", 10.20, 5.80, 4.40, "STK", 8),
    ],
    "2026-02-07 Oaklawn (Sat)": [
        ("Frack Baby", 14.60, 7.20, 4.20, "CLM", 9),
        ("Little Steven", 91.00, 37.00, 15.40, "CLM", 13),
        ("Horse of the Sea", 10.40, 3.60, 2.60, "SA", 11),
        ("San Siro", 17.40, 6.40, 4.60, "AOC", 9),
        ("Gowells Delight", 20.40, 9.00, 5.80, "ALW", 14),
        ("Severe Clear", 13.00, 6.60, 4.80, "CLM", 14),
    ],
    "2026-02-08 Oaklawn (Sun)": [
        ("Personal Jet", 7.00, 3.80, 3.00, "MC", 14),
        ("Brilliant Man", 3.40, 2.20, 2.20, "CLM", 14),
        ("Tiz in Sight", 8.40, 4.80, 3.00, "SA", 11),
        ("Honey's to Blame", 7.20, 4.20, 2.60, "AOC", 8),
        ("Miss Arlington", 16.00, 7.00, 4.60, "CLM", 14),
        ("Take Charge Macy", 13.40, 5.80, 4.80, "MSW", 9),
        ("Itsinmyblood", 8.00, 4.00, 3.00, "CLM", 10),
    ],
    "2026-02-13 Oaklawn (Fri)": [
        ("Tell Me When", 7.20, 4.20, 3.00, "SA", 7),
        ("Coastal Breeze", 10.40, 5.40, 3.20, "MC", 12),
        ("Tizntshelovely", 20.80, 8.60, 5.00, "CLM", 9),
        ("Ninja Warrior", 11.60, 6.40, 3.40, "HDC", 9),
        ("Handsome Herb", 10.80, 5.20, 4.20, "CLM", 12),
        ("Ravin's Town", 11.80, 6.00, 4.40, "CLM", 13),
        ("Majestic Oops", 7.00, 4.40, 3.40, "CLM", 12),
    ],
    "2026-02-14 Oaklawn (Sat)": [
        ("Trouble Ahead", 9.60, 5.00, 3.20, "MC", 7),
        ("Lil Trick", 9.00, 5.40, 4.40, "MC", 12),
        ("Proprietary Trade", 5.80, 3.80, 3.00, "SA", 8),
        ("Ducat", 8.20, 5.00, 3.80, "MC", 13),
        ("Hot Gunner", 49.00, 17.40, 9.40, "CLM", 14),
        ("Classy Socks", 12.60, 5.80, 4.40, "CLM", 14),
    ],
    "2026-02-15 Oaklawn (Sun)": [
        ("Mo Sense", 9.00, 4.80, 2.80, "CLM", 10),
        ("Publisher", 3.40, 2.60, 2.10, "MSW", 7),
        ("More Money Mo", 49.00, 15.80, 9.60, "MC", 9),
        ("C. C. Harbor", 14.60, 5.80, 4.60, "CLM", 12),
        ("Jackman", 4.00, 3.20, 2.60, "CLM", 14),
        ("Ludwig", 7.40, 4.20, 3.40, "CLM", 13),
        ("Legal Empress", 15.20, 4.60, 3.20, "AOC", 6),
    ],
    "2026-02-20 Oaklawn (Fri)": [
        ("Getoutyourwallet", 9.20, 5.20, 3.20, "MC", 9),
        ("Wowsers", 26.20, 8.20, 4.20, "MC", 12),
        ("Gee No Hollander", 32.00, 10.60, 6.60, "CLM", 8),
        ("Goodasiwonswas", 9.20, 4.00, 2.60, "CLM", 8),
        ("Timberline", 4.20, 2.60, 2.20, "MC", 10),
        ("Cur Non", 12.60, 6.60, 5.60, "CLM", 9),
        ("R Pretty Kitty", 11.80, 5.20, 3.60, "ALW", 9),
        ("Haulin Ice", 2.40, 2.10, 2.10, "STK", 9),
        ("Musical Prayer", 14.20, 7.00, 4.20, "CLM", 10),
        ("Markansas", 14.40, 5.00, 3.80, "MC", 12),
    ],
    "2026-02-21 Oaklawn (Sat)": [
        ("Special Ops", 10.40, 5.20, 3.20, "MOC", 8),
        ("Tis Charming", 8.60, 4.40, 2.40, "CLM", 9),
        ("Stephanie Starfish", 25.80, 11.40, 7.20, "CLM", 11),
        ("Khozy My Boy", 11.60, 5.40, 3.20, "CLM", 9),
        ("What's the Tea", 8.80, 6.00, 3.80, "MC", 14),
        ("Shepherd", 12.20, 6.20, 3.80, "CLM", 8),
        ("Lady Dreamer", 47.60, 19.20, 11.60, "CLM", 8),
        ("Touchdown Arkansas", 10.00, 6.00, 4.00, "STK", 8),
        ("Miss Arlington", 8.60, 5.20, 4.40, "HDC", 10),
        ("Manfredi", 6.80, 4.80, 4.00, "CLM", 11),
    ],
    "2026-02-22 Oaklawn (Sun)": [
        ("Feasible", 5.00, 2.80, 2.40, "SA", 7),
        ("Coal Fired", 8.60, 4.20, 3.60, "MC", 8),
        ("Coastal Breeze", 5.80, 3.60, 2.60, "CLM", 10),
        ("Tap Me a Song", 8.20, 3.40, 2.80, "SA", 7),
        ("El Diablo Rojo", 9.80, 5.00, 3.00, "CLM", 9),
        ("Black Powder", 7.20, 3.80, 3.20, "CLM", 9),
        ("Front Runnin", 28.60, 12.20, 6.20, "AOC", 8),
        ("Spring Dancer", 11.80, 7.20, 4.60, "AOC", 8),
        ("Two Dollar Eddie", 12.00, 6.20, 4.80, "CLM", 12),
    ],
    "2026-02-26 Oaklawn (Thu)": [
        ("Lightning Struck", 13.40, 6.20, 3.40, "CLM", 8),
        ("Talkin in Cursive", 8.80, 4.80, 3.00, "CLM", 7),
        ("Western Warrior", 9.40, 4.60, 3.60, "SA", 9),
        ("Thea", 5.20, 3.20, 2.40, "CLM", 9),
        ("Bigwrigdude", 3.80, 2.60, 2.40, "MC", 12),
        ("Mad About Marie", 51.00, 22.60, 9.80, "ALW", 9),
        ("Brienz", 9.60, 5.40, 3.40, "MSW", 7),
        ("Sticker Shock", 5.00, 2.80, 2.20, "AOC", 8),
    ],
    "2026-02-27 Oaklawn (Fri)": [
        ("Only After Midnite", 9.20, 4.60, 3.80, "MC", 9),
        ("Personal Jet", 3.40, 2.40, 2.10, "CLM", 10),
        ("Grand Oracle", 2.60, 2.10, 2.10, "MC", 7),
        ("Trouble Ahead", 6.00, 3.60, 2.60, "CLM", 7),
        ("Balladry", 13.40, 8.20, 4.60, "CLM", 9),
        ("Big Red Machine", 3.80, 2.40, 2.10, "CLM", 8),
        ("Beautiful Twice", 8.40, 4.40, 3.40, "ALW", 8),
        ("Nerazurri", 2.60, 2.10, 2.10, "STK", 5),
        ("Patton's Tizzy", 4.60, 3.20, 2.40, "CLM", 8),
    ],
    "2026-02-28 Oaklawn (Sat)": [
        ("Legally Lucky", 9.60, 8.40, 5.40, "CLM", 7),
        ("Chica Arma", 18.60, 7.20, 4.60, "CLM", 9),
        ("Race Ready", 4.80, 3.20, 2.40, "MOC", 9),
        ("Super Cruise", 6.20, 3.00, 2.20, "AOC", 7),
        ("Top Gun Tommy", 4.00, 2.80, 2.20, "CLM", 9),
        ("Dick Best", 25.40, 12.00, 7.20, "CLM", 13),
        ("Hero's Medal", 13.00, 5.80, 3.80, "CLM", 10),
        ("One Way Or Another", 9.80, 3.60, 3.00, "AOC", 11),
        ("Exosome", 14.80, 6.00, 4.60, "AOC", 8),
        ("Magnitude", 3.60, 2.80, 2.10, "STK", 7),
        ("Appealing Addie", 11.60, 5.60, 3.40, "AOC", 11),
    ],
    "2026-03-01 Oaklawn (Sun)": [
        ("Gewurztraminer", 4.40, 2.40, 2.10, "SA", 9),
        ("Sharp Swinger", 5.20, 3.60, 2.60, "ALW", 10),
        ("Tejano Twist", 4.40, 2.20, 2.10, "AOC", 5),
        ("Zero Sugar", 13.60, 4.80, 3.20, "ALW", 8),
        ("Batten Down", 4.80, 3.00, 2.40, "STK", 7),
        ("Carbone", 7.60, 4.40, 3.40, "HDC", 10),
        ("Bossofmi", 8.40, 3.20, 2.20, "MSW", 12),
        ("Fancy Fairlane", 9.00, 4.20, 2.80, "MSW", 9),
        ("Explora", 4.00, 2.80, 2.20, "STK", 10),
        ("Gethsemane", 9.80, 4.60, 3.80, "MSW", 11),
        ("Class President", 19.00, 9.00, 5.00, "STK", 9),
        ("She's My Last Call", 100.60, 48.80, 18.60, "MSW", 14),
    ],
    "2026-03-05 Oaklawn (Thu)": [
        ("Al's Romeo", 6.40, 3.80, 2.60, "CLM", 9),
        ("Eleven Bravo", 9.80, 4.40, 3.20, "CLM", 8),
        ("Right On Right On", 5.20, 3.40, 2.60, "CLM", 10),
        ("Mr. Goodtime", 4.00, 2.60, 2.20, "CLM", 9),
        ("Stradale", 3.00, 2.40, 2.10, "ALW", 7),
        ("Jolly Jolene", 30.60, 10.20, 5.40, "CLM", 10),
        ("Saudi Crown", 2.80, 2.20, 2.10, "STK", 6),
        ("Second I D", 10.40, 4.60, 3.20, "CLM", 9),
        ("Taken On the Run", 5.20, 3.00, 2.40, "CLM", 10),
    ],
    "2026-03-06 Oaklawn (Fri)": [
        ("Trick of the Light", 9.00, 4.20, 3.00, "CLM", 8),
        ("Alas", 6.60, 3.40, 2.60, "CLM", 9),
        ("Papa Yo", 6.00, 3.20, 2.40, "CLM", 8),
        ("Runamileinmyshoes", 5.40, 3.00, 2.20, "CLM", 9),
        ("Hello Angel", 3.80, 2.60, 2.10, "CLM", 10),
        ("Expect the Best", 5.00, 3.00, 2.40, "CLM", 8),
        ("Easy Kiss", 18.40, 7.20, 4.60, "CLM", 9),
        ("She's a Gemma", 5.20, 3.40, 2.60, "CLM", 8),
        ("Asternia", 3.80, 2.60, 2.10, "CLM", 9),
        ("Zippy Mark", 8.00, 4.20, 3.00, "CLM", 10),
    ],
    "2026-03-07 Oaklawn SLOPPY (Sat)": [
        ("Colonel Caliente", 11.40, 5.20, 3.40, "CLM", 9),
        ("Kissin Cash", 6.20, 3.40, 2.60, "CLM", 10),
        ("Strollsmischief", 54.60, 18.20, 9.40, "CLM", 11),
        ("First Bid", 6.80, 3.60, 2.60, "CLM", 9),
        ("Pahoehoe d'Oro", 5.00, 3.20, 2.40, "CLM", 10),
        ("Midnight Menace", 30.40, 12.60, 6.80, "CLM", 8),
        ("Konteekee", 47.80, 16.40, 8.20, "CLM", 10),
        ("Gun Fire", 12.80, 5.40, 3.60, "CLM", 9),
        ("Majestic Oops", 20.60, 8.40, 4.80, "CLM", 11),
        ("Publisher", 3.40, 2.40, 2.10, "CLM", 8),
        ("Steel Link", 14.80, 6.20, 4.00, "CLM", 10),
    ],
    "2026-03-08 Oaklawn (Sun)": [
        ("Taptastic", 3.60, 2.40, 2.10, "CLM", 8),
        ("Pride's Prince", 7.20, 4.20, 3.00, "CLM", 9),
        ("Auntie Vodka", 12.80, 5.60, 3.80, "CLM", 10),
        ("Nasty Habit", 8.20, 4.40, 3.20, "CLM", 9),
        ("Devils Fork", 7.20, 3.80, 2.60, "CLM", 8),
        ("Laura Branigan", 36.60, 14.20, 7.40, "CLM", 10),
        ("Fireball Birdie", 7.20, 3.60, 2.80, "ALW", 9),
        ("Stars and Stripes", 3.60, 2.40, 2.10, "CLM", 8),
        ("Caroom's Croupier", 4.20, 2.80, 2.20, "CLM", 9),
    ],
    "2026-03-12 Oaklawn (Thu)": [
        ("Sicilian Grandma", 12.20, 5.40, 3.60, "CLM", 9),
        ("Balls in Ur Court", 7.80, 4.20, 3.00, "CLM", 8),
        ("Always Spiteful", 6.80, 3.60, 2.80, "CLM", 10),
        ("Luv to Win", 7.80, 4.00, 3.00, "CLM", 9),
        ("Crushed Ice", 13.40, 5.80, 3.60, "CLM", 10),
        ("Butch", 12.80, 5.60, 3.80, "CLM", 8),
        ("Montauk Point", 15.80, 6.40, 4.20, "CLM", 9),
        ("Ervadean", 17.00, 7.20, 4.60, "CLM", 10),
        ("Arky Road", 9.00, 4.40, 3.20, "CLM", 9),
    ],
    "2026-03-13 Oaklawn (Fri)": [
        ("Big Tech", 5.20, 3.00, 2.40, "CLM", 8),
        ("Jackman", 6.20, 3.40, 2.60, "CLM", 9),
        ("Miwoman", 78.80, 28.40, 12.60, "CLM", 10),
        ("Unauthorized", 4.20, 2.80, 2.20, "CLM", 8),
        ("Skyler", 12.20, 5.60, 3.80, "CLM", 9),
        ("Miranda's Rocky", 27.00, 10.40, 5.60, "CLM", 10),
        ("Spoiler", 10.20, 4.80, 3.20, "CLM", 8),
        ("Unload", 11.80, 5.20, 3.40, "CLM", 9),
        ("Delacina", 60.20, 22.40, 10.20, "CLM", 10),
        ("Wildwood Queen", 9.00, 4.20, 3.00, "CLM", 9),
    ],
    "2026-03-14 Oaklawn (Sat)": [
        ("C McGriff", 4.20, 2.80, 2.20, "MOC", 7),
        ("Montana Cafe", 19.00, 8.40, 4.80, "CLM", 9),
        ("Hicko", 3.40, 2.40, 2.10, "CLM", 8),
        ("Raymond", 4.80, 3.00, 2.40, "CLM", 9),
        ("Miracle Worker", 10.60, 4.80, 3.20, "CLM", 10),
        ("Debbie Doll", 10.00, 4.60, 3.20, "CLM", 8),
        ("Dare to Fly", 5.20, 3.00, 2.40, "ALW", 7),
        ("Goodall", 12.00, 5.40, 3.60, "CLM", 9),
        ("Ripped", 23.40, 9.20, 5.40, "CLM", 10),
        ("Tejano Twist", 6.00, 3.40, 2.60, "AOC", 8),
        ("Empath", 36.40, 14.60, 7.20, "CLM", 11),
    ],
    "2026-03-15 Oaklawn (Sat)": [
        ("L.A. Diamond", 9.20, 4.40, 3.20, "CLM", 7),
        ("Good News Rocket", 3.20, 2.40, 2.10, "MC", 8),
        ("Willow Creek Road", 10.80, 4.80, 3.20, "AOC", 7),
        ("Donita", 3.60, 2.60, 2.10, "MC", 8),
        ("The Thunderer", 20.20, 8.40, 4.60, "CLM", 10),
        ("American Man", 6.20, 3.40, 2.60, "MSW", 8),
        ("Otto the Conqueror", 12.40, 5.60, 3.80, "CLM", 8),
        ("Miss Macy", 10.60, 4.80, 3.40, "ALW", 11),
        ("Chupapi Munyayo", 8.00, 4.00, 2.80, "CLM", 10),
    ],
    # === FAIR GROUNDS ===
    "2026-02-22 Fair Grounds (Sun)": [
        ("Antiphon", 11.40, 4.80, 3.60, "MSW", 12),
        ("Sully", 4.40, 2.20, 2.10, "MC", 7),
        ("Princess Celine", 3.80, 2.80, 2.10, "CLM", 8),
        ("Danzig's Dora", 9.80, 4.60, 3.00, "CLM", 8),
        ("Slam Diego", 12.40, 6.20, 4.00, "SA", 11),
        ("Fountain Run", 4.80, 3.00, 2.40, "SA", 7),
        ("Big Chopper", 20.20, 7.80, 4.80, "AOC", 10),
    ],
    "2026-02-28 Fair Grounds (Sat)": [
        ("Highly Wicked", 4.80, 2.80, 3.80, "STK", 7),
        ("What's Love", 2.80, 2.10, 2.10, "MSW", 8),
        ("Soul Coaxing", 44.00, 15.00, 8.40, "CLM", 11),
        ("Dagmara", 9.80, 5.40, 2.80, "MSW", 12),
        ("Wondrous", 14.00, 4.20, 2.80, "ALW", 6),
        ("Boss of All Bosses", 5.40, 3.80, 2.80, "STK", 10),
        ("Creole Chrome", 3.80, 2.40, 2.20, "STK", 8),
    ],
    "2026-03-01 Fair Grounds (Sun)": [
        ("Mika Ella Pika", 7.40, 3.20, 2.60, "CLM", 7),
        ("Get Her Number", 6.60, 3.20, 2.20, "SA", 6),
        ("Clearly My Star", 3.60, 2.60, 2.10, "MSW", 9),
        ("Runninginthemoney", 2.60, 2.20, 2.20, "CLM", 8),
        ("Mambo Queen", 4.20, 2.60, 2.20, "CLM", 10),
        ("Double Edge Sword", 3.60, 2.40, 2.10, "SA", 8),
        ("Unitas", 4.40, 3.40, 2.60, "MSW", 8),
        ("Sounds Like Power", 16.80, 5.60, 3.60, "AOC", 9),
    ],
    "2026-03-08 Fair Grounds (Sun)": [
        ("Our Majestic", 7.60, 3.80, 3.20, "CLM", 8),
        ("Custom Cadillac", 4.20, 2.60, 2.20, "CLM", 9),
        ("Vitruvius", 6.20, 4.00, 2.80, "MSW", 11),
        ("Fast Flame", 7.20, 4.40, 3.20, "AOC", 7),
        ("Somekinda Mischief", 5.80, 3.40, 2.60, "MC", 12),
        ("Kavod", 4.40, 2.80, 2.60, "CLM", 9),
        ("For Love and Honor", 10.60, 4.20, 3.00, "AOC", 7),
    ],
    "2026-03-14 Fair Grounds (Sat)": [
        ("Duvee", 6.00, 4.60, 3.20, "CLM", 9),
        ("Hexcel", 26.80, 14.20, 5.00, "CLM", 9),
        ("Guaguarero", 3.40, 2.20, 2.20, "MC", 9),
        ("War Belle", 9.20, 5.40, 4.00, "MC", 10),
        ("One Line Ruler", 21.60, 5.80, 2.80, "SA", 9),
        ("Blushing Justice", 5.80, 6.60, 4.00, "MSW", 10),
        ("Ur Desire", 19.40, 8.60, 4.40, "MSW", 7),
    ],
    "2026-03-15 Fair Grounds (Sat)": [
        ("Like This", 9.00, 4.20, 3.00, "CLM", 8),
        ("Sand Cast", 9.40, 4.40, 3.20, "CLM", 9),
        ("Victory Prince", 3.20, 2.40, 2.10, "MSW", 7),
        ("Notion", 9.80, 4.60, 3.20, "CLM", 8),
        ("In B.J.'s Honor", 8.40, 4.00, 2.80, "AOC", 9),
        ("Furio", 5.00, 3.00, 2.40, "AOC", 7),
        ("One More Guitar", 10.40, 4.80, 3.20, "MSW", 8),
    ],
}


def payout_to_odds(payout):
    """Convert $2 win payout to approximate odds ratio."""
    return (payout - 2.0) / 2.0


def flatten_races():
    """Flatten all race data into a list of dicts."""
    all_races = []
    for day_key, races in RACE_DATA.items():
        is_sloppy = "SLOPPY" in day_key
        track = "Fair Grounds" if "Fair Grounds" in day_key else "Oaklawn"
        for i, race in enumerate(races):
            winner, win_pay, place_pay, show_pay, rtype, starters = race
            all_races.append({
                "day": day_key,
                "race_num": i + 1,
                "winner": winner,
                "win_payout": win_pay,
                "place_payout": place_pay,
                "show_payout": show_pay,
                "race_type": rtype,
                "starters": starters,
                "odds_ratio": payout_to_odds(win_pay),
                "is_sloppy": is_sloppy,
                "track": track,
            })
    return all_races


# ============================================================
# STRATEGY SIMULATION ENGINE
# ============================================================

class Strategy:
    """A parameterized betting strategy to backtest."""

    def __init__(self, params=None):
        if params is None:
            params = self.default_params()
        self.params = params

    @staticmethod
    def default_params():
        return {
            # What payout threshold to bet WIN (minimum payout to consider)
            "win_min_payout": 6.0,      # Only bet WIN on races where we expect $6+ payouts
            "win_max_payout": 200.0,     # Cap (ignore extreme outliers)

            # Place betting
            "place_enabled": True,
            "place_bet_amount": 2.0,
            "place_itm_rate": 0.45,      # Estimated in-the-money rate

            # Win bet odds filter
            "win_bet_amount": 2.0,
            "win_min_odds_ratio": 2.0,   # Minimum odds to bet WIN (2/1)
            "win_max_odds_ratio": 30.0,  # Max odds (skip extreme longshots)

            # Value/Saver bets
            "saver_enabled": True,
            "saver_bet_amount": 2.0,
            "saver_min_odds_ratio": 4.0,  # Only saver at 4/1+
            "saver_hit_rate": 0.12,       # 12% hit rate on savers

            # Race type filters (which types to bet)
            "bet_clm": True,
            "bet_mc": True,
            "bet_alw": True,
            "bet_aoc": True,
            "bet_stk": True,
            "bet_msw": True,
            "bet_other": True,  # SA, HDC, MOC

            # Field size filters
            "min_field_size": 5,
            "max_field_size": 16,
            "big_field_bonus": 1.0,  # Multiplier for fields 10+

            # Sloppy track adjustment
            "sloppy_multiplier": 0.5,  # Cut bets by this on sloppy

            # Selection rates (what % of races we bet on)
            "win_selection_rate": 0.35,   # We bet WIN on 35% of races
            "saver_selection_rate": 0.25, # We bet SAVER on 25% of races

            # Payout-based selection (simulate our ability to pick winners)
            # This is the core parameter - how well can we identify value?
            "value_pick_accuracy": 0.22,  # 22% of our value picks are winners
        }

    def should_bet_race(self, race):
        """Check if we should bet on this race based on type/field filters."""
        rtype = race["race_type"]
        type_map = {
            "CLM": self.params["bet_clm"],
            "MC": self.params["bet_mc"],
            "ALW": self.params["bet_alw"],
            "AOC": self.params["bet_aoc"],
            "STK": self.params["bet_stk"],
            "MSW": self.params["bet_msw"],
        }
        if rtype in type_map:
            if not type_map[rtype]:
                return False
        elif not self.params["bet_other"]:
            return False

        if race["starters"] < self.params["min_field_size"]:
            return False
        if race["starters"] > self.params["max_field_size"]:
            return False

        return True


def simulate_strategy(params, all_races, seed=42):
    """
    Simulate a betting strategy across all races.

    Key insight: We can't know in advance which horse wins, but we CAN
    simulate our VALUE SELECTION ability. The strategy works like this:

    For each race we decide to bet on:
    1. PLACE BET: We bet $X PLACE on our top pick. Based on ITM rate, some cash.
    2. WIN BET: We bet $X WIN on value picks (odds >= threshold). Hit rate = accuracy param.
    3. SAVER BET: Small bet on longshots. Lower hit rate, bigger payouts.

    The simulation uses the ACTUAL payouts from historical data, but our
    "hit rate" determines how often we pick the actual winner.
    """
    random.seed(seed)
    strat = Strategy(params)

    total_wagered = 0.0
    total_returned = 0.0
    wins = 0
    bets_placed = 0
    place_cashes = 0
    saver_hits = 0
    biggest_win = 0.0
    daily_results = {}

    for race in all_races:
        if not strat.should_bet_race(race):
            continue

        day = race["day"]
        if day not in daily_results:
            daily_results[day] = {"wagered": 0, "returned": 0, "bets": 0}

        odds = race["odds_ratio"]
        payout = race["win_payout"]
        place_pay = race["place_payout"]
        sloppy_mult = params["sloppy_multiplier"] if race["is_sloppy"] else 1.0

        # ---- PLACE BET ----
        if params["place_enabled"]:
            place_amt = params["place_bet_amount"] * sloppy_mult
            total_wagered += place_amt
            daily_results[day]["wagered"] += place_amt
            bets_placed += 1

            # Does our place bet cash? Based on ITM rate
            if random.random() < params["place_itm_rate"]:
                # Use actual place payout from data
                total_returned += place_pay
                daily_results[day]["returned"] += place_pay
                place_cashes += 1

        # ---- WIN BET (Value picks) ----
        # We select win bets based on our selection rate
        if random.random() < params["win_selection_rate"]:
            if params["win_min_odds_ratio"] <= odds <= params["win_max_odds_ratio"]:
                if payout >= params["win_min_payout"]:
                    win_amt = params["win_bet_amount"] * sloppy_mult
                    big_field = params["big_field_bonus"] if race["starters"] >= 10 else 1.0
                    total_wagered += win_amt
                    daily_results[day]["wagered"] += win_amt
                    bets_placed += 1

                    # Do we pick the winner? Based on accuracy
                    if random.random() < params["value_pick_accuracy"]:
                        returned = payout * (win_amt / 2.0)  # Scale payout by bet size
                        total_returned += returned
                        daily_results[day]["returned"] += returned
                        wins += 1
                        biggest_win = max(biggest_win, returned)

        # ---- SAVER BET (Longshots) ----
        if params["saver_enabled"]:
            if random.random() < params["saver_selection_rate"]:
                if odds >= params["saver_min_odds_ratio"]:
                    saver_amt = params["saver_bet_amount"] * sloppy_mult
                    total_wagered += saver_amt
                    daily_results[day]["wagered"] += saver_amt
                    bets_placed += 1

                    # Lower hit rate for savers but bigger payouts
                    if random.random() < params["saver_hit_rate"]:
                        returned = payout * (saver_amt / 2.0)
                        total_returned += returned
                        daily_results[day]["returned"] += returned
                        saver_hits += 1
                        biggest_win = max(biggest_win, returned)

    # Calculate metrics
    net = total_returned - total_wagered
    roi = (net / total_wagered * 100) if total_wagered > 0 else 0
    num_days = len(daily_results)

    # Count profitable days
    profitable_days = sum(1 for d in daily_results.values() if d["returned"] > d["wagered"])
    daily_nets = [d["returned"] - d["wagered"] for d in daily_results.values()]
    avg_daily_net = sum(daily_nets) / len(daily_nets) if daily_nets else 0

    return {
        "total_wagered": round(total_wagered, 2),
        "total_returned": round(total_returned, 2),
        "net_profit": round(net, 2),
        "roi": round(roi, 2),
        "bets_placed": bets_placed,
        "win_hits": wins,
        "place_cashes": place_cashes,
        "saver_hits": saver_hits,
        "biggest_win": round(biggest_win, 2),
        "num_days": num_days,
        "profitable_days": profitable_days,
        "profitable_day_pct": round(100 * profitable_days / max(num_days, 1), 1),
        "avg_daily_net": round(avg_daily_net, 2),
        "avg_bet_per_day": round(bets_placed / max(num_days, 1), 1),
        "daily_budget": round(total_wagered / max(num_days, 1), 2),
    }


def run_multi_seed(params, all_races, num_seeds=20):
    """Run simulation across multiple random seeds for stability."""
    results = []
    for seed in range(num_seeds):
        r = simulate_strategy(params, all_races, seed=seed)
        results.append(r)

    # Average across seeds
    avg = {}
    for key in results[0]:
        vals = [r[key] for r in results]
        avg[key] = round(sum(vals) / len(vals), 2)

    # Add consistency metrics
    rois = [r["roi"] for r in results]
    avg["min_roi"] = round(min(rois), 2)
    avg["max_roi"] = round(max(rois), 2)
    avg["roi_std"] = round((sum((x - avg["roi"])**2 for x in rois) / len(rois))**0.5, 2)

    return avg


# ============================================================
# OPTIMIZER - Grid search + random perturbation
# ============================================================

def optimize():
    """Run continuous optimization loop."""
    all_races = flatten_races()
    total_races = len(all_races)
    total_days = len(RACE_DATA)

    print("=" * 70)
    print("  HORSE RACING BACKTEST OPTIMIZER v1.0")
    print(f"  {total_days} Race Days | {total_races} Races | Oaklawn + Fair Grounds")
    print(f"  Feb 6 - Mar 15, 2026")
    print("=" * 70)

    # Market overview
    payouts = [r["win_payout"] for r in all_races]
    print(f"\n  Total races: {total_races}")
    print(f"  Avg win payout: ${sum(payouts)/len(payouts):.2f}")
    print(f"  Median payout: ${sorted(payouts)[len(payouts)//2]:.2f}")
    print(f"  Winners $5+: {sum(1 for p in payouts if p >= 5)}/{total_races} ({100*sum(1 for p in payouts if p >= 5)/total_races:.0f}%)")
    print(f"  Winners $10+: {sum(1 for p in payouts if p >= 10)}/{total_races} ({100*sum(1 for p in payouts if p >= 10)/total_races:.0f}%)")
    print(f"  Winners $20+: {sum(1 for p in payouts if p >= 20)}/{total_races} ({100*sum(1 for p in payouts if p >= 20)/total_races:.0f}%)")
    print(f"  Winners $50+: {sum(1 for p in payouts if p >= 50)}/{total_races}")
    print(f"  Biggest payout: ${max(payouts):.2f}")

    # ============================================================
    # PHASE 1: Grid Search - Systematic exploration
    # ============================================================
    print(f"\n{'='*70}")
    print("  PHASE 1: GRID SEARCH OPTIMIZATION")
    print(f"{'='*70}")

    best_roi = -999
    best_params = None
    best_result = None
    iteration = 0
    all_results = []

    # Key parameters to grid search
    grid = {
        "win_min_payout": [4.0, 6.0, 8.0, 10.0, 14.0],
        "win_min_odds_ratio": [1.5, 2.0, 3.0, 4.0, 5.0],
        "place_itm_rate": [0.35, 0.40, 0.45, 0.50],
        "win_selection_rate": [0.20, 0.30, 0.40, 0.50],
        "saver_min_odds_ratio": [3.0, 4.0, 5.0, 7.0],
        "saver_hit_rate": [0.08, 0.10, 0.12, 0.15],
        "value_pick_accuracy": [0.15, 0.18, 0.20, 0.22, 0.25, 0.28],
        "sloppy_multiplier": [0.3, 0.5, 0.7, 1.0],
    }

    # Smart grid: test combinations of the most impactful params
    # Full grid would be too large, so we do staged optimization
    print("\n  Stage 1: Optimizing core accuracy + odds thresholds...")

    for accuracy in grid["value_pick_accuracy"]:
        for win_odds in grid["win_min_odds_ratio"]:
            for win_pay in grid["win_min_payout"]:
                for saver_odds in grid["saver_min_odds_ratio"]:
                    params = Strategy.default_params()
                    params["value_pick_accuracy"] = accuracy
                    params["win_min_odds_ratio"] = win_odds
                    params["win_min_payout"] = win_pay
                    params["saver_min_odds_ratio"] = saver_odds

                    result = run_multi_seed(params, all_races, num_seeds=10)
                    iteration += 1

                    all_results.append({
                        "params": copy.deepcopy(params),
                        "result": result,
                    })

                    if result["roi"] > best_roi:
                        best_roi = result["roi"]
                        best_params = copy.deepcopy(params)
                        best_result = result
                        print(f"    [{iteration:>4}] NEW BEST ROI: {result['roi']:>+7.1f}% | "
                              f"Net: ${result['net_profit']:>+8.2f} | "
                              f"Accuracy: {accuracy} | MinOdds: {win_odds} | "
                              f"MinPay: ${win_pay} | SaverOdds: {saver_odds}")

    print(f"\n  Stage 1 complete: {iteration} combinations tested")
    print(f"  Best ROI so far: {best_roi:+.1f}%")

    # Stage 2: Optimize selection rates and bet sizing around best
    print("\n  Stage 2: Optimizing selection rates and bet sizing...")
    stage2_best = best_roi

    for win_sel in grid["win_selection_rate"]:
        for saver_rate in grid["saver_hit_rate"]:
            for place_itm in grid["place_itm_rate"]:
                for sloppy in grid["sloppy_multiplier"]:
                    params = copy.deepcopy(best_params)
                    params["win_selection_rate"] = win_sel
                    params["saver_hit_rate"] = saver_rate
                    params["place_itm_rate"] = place_itm
                    params["sloppy_multiplier"] = sloppy

                    result = run_multi_seed(params, all_races, num_seeds=10)
                    iteration += 1

                    all_results.append({
                        "params": copy.deepcopy(params),
                        "result": result,
                    })

                    if result["roi"] > best_roi:
                        best_roi = result["roi"]
                        best_params = copy.deepcopy(params)
                        best_result = result
                        print(f"    [{iteration:>4}] NEW BEST ROI: {result['roi']:>+7.1f}% | "
                              f"Net: ${result['net_profit']:>+8.2f} | "
                              f"WinSel: {win_sel} | SaverHit: {saver_rate} | "
                              f"PlaceITM: {place_itm} | Sloppy: {sloppy}")

    print(f"\n  Stage 2 complete: {iteration} total combinations tested")

    # ============================================================
    # PHASE 2: Random Perturbation - Fine-tuning
    # ============================================================
    print(f"\n{'='*70}")
    print("  PHASE 2: RANDOM PERTURBATION (Fine-tuning)")
    print(f"{'='*70}")

    perturbation_rounds = 500
    no_improvement = 0
    max_no_improvement = 100  # Stop after 100 rounds without improvement

    for r in range(perturbation_rounds):
        # Perturb best params slightly
        params = copy.deepcopy(best_params)

        # Randomly adjust 1-3 parameters
        num_adjustments = random.randint(1, 3)
        adjustable = [
            ("win_min_payout", 0.5, 2.0, 30.0),
            ("win_min_odds_ratio", 0.25, 0.5, 15.0),
            ("place_itm_rate", 0.02, 0.15, 0.65),
            ("win_selection_rate", 0.03, 0.05, 0.70),
            ("saver_min_odds_ratio", 0.5, 1.0, 15.0),
            ("saver_hit_rate", 0.01, 0.03, 0.25),
            ("value_pick_accuracy", 0.01, 0.08, 0.40),
            ("sloppy_multiplier", 0.05, 0.1, 1.5),
            ("win_bet_amount", 0.5, 1.0, 10.0),
            ("saver_bet_amount", 0.5, 1.0, 8.0),
            ("place_bet_amount", 0.5, 1.0, 8.0),
            ("saver_selection_rate", 0.03, 0.05, 0.60),
            ("big_field_bonus", 0.1, 0.5, 2.0),
        ]

        for _ in range(num_adjustments):
            param_name, step, low, high = random.choice(adjustable)
            delta = random.choice([-1, 1]) * step * random.uniform(0.5, 2.0)
            params[param_name] = max(low, min(high, params[param_name] + delta))

        # Also randomly toggle race types sometimes
        if random.random() < 0.15:
            toggle = random.choice(["bet_clm", "bet_mc", "bet_alw", "bet_aoc", "bet_stk", "bet_msw", "bet_other"])
            params[toggle] = not params[toggle]

        result = run_multi_seed(params, all_races, num_seeds=15)
        iteration += 1

        all_results.append({
            "params": copy.deepcopy(params),
            "result": result,
        })

        if result["roi"] > best_roi:
            improvement = result["roi"] - best_roi
            best_roi = result["roi"]
            best_params = copy.deepcopy(params)
            best_result = result
            no_improvement = 0
            print(f"    [{iteration:>4}] IMPROVED +{improvement:.1f}% -> ROI: {result['roi']:>+7.1f}% | "
                  f"Net: ${result['net_profit']:>+8.2f} | "
                  f"BigWin: ${result['biggest_win']:.2f}")
        else:
            no_improvement += 1

        if no_improvement >= max_no_improvement:
            print(f"\n  Converged after {r+1} perturbation rounds ({no_improvement} without improvement)")
            break

    # ============================================================
    # PHASE 3: Strategy Variants - Test fundamentally different approaches
    # ============================================================
    print(f"\n{'='*70}")
    print("  PHASE 3: ALTERNATIVE STRATEGY EXPLORATION")
    print(f"{'='*70}")

    strategies = {
        "Conservative Place-Heavy": {
            **Strategy.default_params(),
            "place_enabled": True,
            "place_bet_amount": 3.0,
            "place_itm_rate": 0.50,
            "win_bet_amount": 2.0,
            "win_selection_rate": 0.15,
            "win_min_odds_ratio": 3.0,
            "win_min_payout": 8.0,
            "saver_enabled": False,
            "value_pick_accuracy": 0.20,
        },
        "Aggressive Value Hunter": {
            **Strategy.default_params(),
            "place_enabled": False,
            "win_bet_amount": 3.0,
            "win_selection_rate": 0.45,
            "win_min_odds_ratio": 2.5,
            "win_min_payout": 6.0,
            "saver_enabled": True,
            "saver_bet_amount": 3.0,
            "saver_min_odds_ratio": 5.0,
            "saver_selection_rate": 0.30,
            "saver_hit_rate": 0.10,
            "value_pick_accuracy": 0.22,
        },
        "Longshot Bomber": {
            **Strategy.default_params(),
            "place_enabled": True,
            "place_bet_amount": 2.0,
            "place_itm_rate": 0.45,
            "win_bet_amount": 2.0,
            "win_selection_rate": 0.20,
            "win_min_odds_ratio": 5.0,
            "win_min_payout": 12.0,
            "saver_enabled": True,
            "saver_bet_amount": 3.0,
            "saver_min_odds_ratio": 7.0,
            "saver_selection_rate": 0.35,
            "saver_hit_rate": 0.08,
            "value_pick_accuracy": 0.15,
        },
        "Chalk Avoider": {
            **Strategy.default_params(),
            "place_enabled": True,
            "place_bet_amount": 2.0,
            "place_itm_rate": 0.42,
            "win_bet_amount": 2.0,
            "win_selection_rate": 0.40,
            "win_min_odds_ratio": 3.0,
            "win_min_payout": 7.0,
            "saver_enabled": True,
            "saver_bet_amount": 2.0,
            "saver_min_odds_ratio": 4.0,
            "saver_selection_rate": 0.30,
            "saver_hit_rate": 0.12,
            "value_pick_accuracy": 0.25,
            "bet_stk": False,  # Skip stakes (too chalky)
        },
        "Claiming Specialist": {
            **Strategy.default_params(),
            "place_enabled": True,
            "place_bet_amount": 2.0,
            "place_itm_rate": 0.45,
            "win_bet_amount": 3.0,
            "win_selection_rate": 0.40,
            "win_min_odds_ratio": 2.0,
            "win_min_payout": 6.0,
            "saver_enabled": True,
            "saver_bet_amount": 2.0,
            "saver_min_odds_ratio": 4.0,
            "saver_selection_rate": 0.25,
            "saver_hit_rate": 0.14,
            "value_pick_accuracy": 0.24,
            "bet_stk": False,
            "bet_msw": False,
            "bet_alw": False,
        },
        "Big Field Value": {
            **Strategy.default_params(),
            "min_field_size": 8,
            "place_enabled": True,
            "place_bet_amount": 2.0,
            "place_itm_rate": 0.40,
            "win_bet_amount": 3.0,
            "win_selection_rate": 0.45,
            "win_min_odds_ratio": 3.0,
            "win_min_payout": 8.0,
            "saver_enabled": True,
            "saver_bet_amount": 2.0,
            "saver_min_odds_ratio": 5.0,
            "saver_selection_rate": 0.30,
            "saver_hit_rate": 0.10,
            "value_pick_accuracy": 0.20,
            "big_field_bonus": 1.3,
        },
    }

    strategy_results = {}
    for name, params in strategies.items():
        result = run_multi_seed(params, all_races, num_seeds=20)
        strategy_results[name] = result
        iteration += 1
        marker = " <<<" if result["roi"] > best_roi else ""
        print(f"  {name:<28} ROI: {result['roi']:>+7.1f}% | Net: ${result['net_profit']:>+8.2f} | "
              f"Budget: ${result['daily_budget']:.0f}/day | ProfDays: {result['profitable_day_pct']:.0f}%{marker}")

        if result["roi"] > best_roi:
            best_roi = result["roi"]
            best_params = copy.deepcopy(params)
            best_result = result

    # Now perturb the best alternative strategies too
    print("\n  Fine-tuning top alternative strategies...")
    for name, result in sorted(strategy_results.items(), key=lambda x: x[1]["roi"], reverse=True)[:3]:
        base_params = strategies[name]
        for _ in range(100):
            params = copy.deepcopy(base_params)
            # Random perturbation
            for key in ["value_pick_accuracy", "win_selection_rate", "saver_hit_rate",
                        "place_itm_rate", "win_min_payout", "win_min_odds_ratio",
                        "saver_min_odds_ratio", "sloppy_multiplier"]:
                if key in params:
                    params[key] *= random.uniform(0.85, 1.15)
            result = run_multi_seed(params, all_races, num_seeds=15)
            iteration += 1
            if result["roi"] > best_roi:
                best_roi = result["roi"]
                best_params = copy.deepcopy(params)
                best_result = result
                print(f"    [{name}] NEW BEST: ROI {result['roi']:+.1f}% | Net: ${result['net_profit']:+.2f}")

    # ============================================================
    # FINAL RESULTS
    # ============================================================
    print(f"\n{'='*70}")
    print(f"  OPTIMIZATION COMPLETE")
    print(f"  {iteration} total parameter combinations tested")
    print(f"{'='*70}")

    print(f"\n  BEST STRATEGY FOUND:")
    print(f"  {'='*50}")
    print(f"  ROI:              {best_result['roi']:>+.1f}%")
    print(f"  Net Profit:       ${best_result['net_profit']:>+.2f}")
    print(f"  Total Wagered:    ${best_result['total_wagered']:.2f}")
    print(f"  Total Returned:   ${best_result['total_returned']:.2f}")
    print(f"  Win Hits:         {best_result['win_hits']:.0f}")
    print(f"  Place Cashes:     {best_result['place_cashes']:.0f}")
    print(f"  Saver Hits:       {best_result['saver_hits']:.0f}")
    print(f"  Biggest Win:      ${best_result['biggest_win']:.2f}")
    print(f"  Profitable Days:  {best_result['profitable_day_pct']:.0f}%")
    print(f"  Avg Daily Net:    ${best_result['avg_daily_net']:+.2f}")
    print(f"  Daily Budget:     ${best_result['daily_budget']:.2f}")
    print(f"  Bets/Day:         {best_result['avg_bet_per_day']:.1f}")
    print(f"  ROI Range:        {best_result['min_roi']:+.1f}% to {best_result['max_roi']:+.1f}%")
    print(f"  ROI Std Dev:      {best_result['roi_std']:.1f}%")

    print(f"\n  OPTIMAL PARAMETERS:")
    print(f"  {'='*50}")
    for key, val in sorted(best_params.items()):
        print(f"  {key:<30} = {val}")

    # ============================================================
    # TOP 10 STRATEGIES BY ROI
    # ============================================================
    print(f"\n{'='*70}")
    print(f"  TOP 10 STRATEGIES BY ROI")
    print(f"{'='*70}")

    sorted_results = sorted(all_results, key=lambda x: x["result"]["roi"], reverse=True)
    for i, entry in enumerate(sorted_results[:10]):
        r = entry["result"]
        p = entry["params"]
        print(f"\n  #{i+1}: ROI {r['roi']:+.1f}% | Net ${r['net_profit']:+.2f} | "
              f"Budget ${r['daily_budget']:.0f}/day | ProfDays {r['profitable_day_pct']:.0f}%")
        print(f"       Accuracy: {p['value_pick_accuracy']:.2f} | WinOdds: {p['win_min_odds_ratio']:.1f}+ | "
              f"MinPay: ${p['win_min_payout']:.0f} | SaverOdds: {p['saver_min_odds_ratio']:.1f}+ | "
              f"WinSel: {p['win_selection_rate']:.2f}")

    # ============================================================
    # ACTIONABLE BETTING RULES
    # ============================================================
    print(f"\n{'='*70}")
    print(f"  ACTIONABLE BETTING RULES (from optimal params)")
    print(f"{'='*70}")

    p = best_params
    print(f"""
  Based on {total_races} races across {total_days} race days:

  RULE 1 - PLACE BETS (Steady Income)
  {'Enabled' if p['place_enabled'] else 'Disabled'}
  Bet ${p['place_bet_amount']:.0f} PLACE on your top consensus pick every race
  Expected ITM rate: {p['place_itm_rate']*100:.0f}%

  RULE 2 - WIN BETS (Value Plays)
  Only bet WIN when odds are {p['win_min_odds_ratio']:.1f}/1 or higher
  Only bet when expected payout is ${p['win_min_payout']:.0f}+
  Bet ${p['win_bet_amount']:.0f} WIN on {p['win_selection_rate']*100:.0f}% of races (be selective!)
  Target accuracy: {p['value_pick_accuracy']*100:.0f}%

  RULE 3 - SAVER BETS (Big Win Hunters)
  {'Enabled' if p['saver_enabled'] else 'Disabled'}
  Bet ${p['saver_bet_amount']:.0f} on longshots at {p['saver_min_odds_ratio']:.0f}/1+
  Bet in {p['saver_selection_rate']*100:.0f}% of races
  Expected hit rate: {p['saver_hit_rate']*100:.0f}%

  RULE 4 - RACE FILTERS
  CLM: {'YES' if p['bet_clm'] else 'NO'} | MC: {'YES' if p['bet_mc'] else 'NO'} | ALW: {'YES' if p['bet_alw'] else 'NO'}
  AOC: {'YES' if p['bet_aoc'] else 'NO'} | STK: {'YES' if p['bet_stk'] else 'NO'} | MSW: {'YES' if p['bet_msw'] else 'NO'}
  Min field: {p['min_field_size']} horses | Max field: {p['max_field_size']} horses

  RULE 5 - WEATHER
  On sloppy tracks: multiply all bets by {p['sloppy_multiplier']:.1f}x
  (Sloppy = more chaos = more value but also more risk)

  DAILY BUDGET: ~${best_result['daily_budget']:.0f}
  EXPECTED: {best_result['avg_bet_per_day']:.0f} bets/day
  PROFITABLE DAYS: {best_result['profitable_day_pct']:.0f}% of the time
""")

    # Save results
    output = {
        "metadata": {
            "total_races": total_races,
            "total_days": total_days,
            "iterations": iteration,
            "date_range": "Feb 6 - Mar 15, 2026",
            "tracks": ["Oaklawn Park", "Fair Grounds"],
            "timestamp": datetime.now().isoformat(),
        },
        "market_stats": {
            "avg_payout": round(sum(payouts) / len(payouts), 2),
            "median_payout": sorted(payouts)[len(payouts) // 2],
            "pct_over_5": round(100 * sum(1 for p in payouts if p >= 5) / total_races, 1),
            "pct_over_10": round(100 * sum(1 for p in payouts if p >= 10) / total_races, 1),
            "pct_over_20": round(100 * sum(1 for p in payouts if p >= 20) / total_races, 1),
            "max_payout": max(payouts),
        },
        "best_strategy": {
            "params": best_params,
            "result": best_result,
        },
        "top_10": [
            {
                "rank": i + 1,
                "roi": entry["result"]["roi"],
                "net_profit": entry["result"]["net_profit"],
                "daily_budget": entry["result"]["daily_budget"],
                "key_params": {
                    "accuracy": entry["params"]["value_pick_accuracy"],
                    "win_min_odds": entry["params"]["win_min_odds_ratio"],
                    "win_min_pay": entry["params"]["win_min_payout"],
                    "saver_odds": entry["params"]["saver_min_odds_ratio"],
                }
            }
            for i, entry in enumerate(sorted_results[:10])
        ],
    }

    output_path = os.path.join(os.path.dirname(__file__), "optimizer_results.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n  Results saved to {output_path}")

    return output


if __name__ == "__main__":
    output = optimize()
