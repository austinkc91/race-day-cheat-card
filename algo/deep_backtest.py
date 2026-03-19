#!/usr/bin/env python3
"""
DEEP BACKTEST — Exhaustive strategy search across 43 real races with actual exotic payouts.
Goal: Find a strategy with POSITIVE ROI on real data.

Key insight from previous work: Mechanical ML-top-N boxing loses because chalk
exactas ($5-12) don't cover the $10/race cost. We need to either:
1. Be MORE selective (skip chalk-heavy races)
2. Focus on HIGH-PAYOUT bet types (trifectas, superfectas in big fields)
3. Use KEY bets instead of BOXES (cheaper, more targeted)
4. Go CONTRARIAN (bet value horses, not favorites)
"""

import json
import itertools
from collections import defaultdict

# ============== REAL RACE DATA (43 races, 5 track-days) ==============
RACE_DATA = [
    # ====== PARX MARCH 18, 2026 ======
    {"day": "Parx Mar 18", "race": 1, "type": "CLM", "starters": 9,
     "ml_odds": {"Angel Mesa": 20, "Paddy's Gift": 6, "Lu Lu Vaton": 20, "Sweet Marie": 10,
                 "Motown Honey": 5, "Laugh Like Lucy": 4.5, "She Can Scat": 8, "Toxic Girl": 3, "Mink Stole": 2.5},
     "finish": ["Mink Stole", "Paddy's Gift", "Laugh Like Lucy", "Angel Mesa"],
     "exacta_pay": 17.80, "trifecta_pay": 94.60, "superfecta_pay": 522.00,
     "win_pay": 3.60, "place_pay": 2.40, "show_pay": 2.10},
    {"day": "Parx Mar 18", "race": 2, "type": "CLM", "starters": 6,
     "ml_odds": {"Goldieness": 1.6, "Aruma": 2.5, "Creme Caramel": 20, "So Swell": 8, "Golden Philly": 3.5, "Mikey's Song": 12},
     "finish": ["Goldieness", "Aruma", "Golden Philly", "Mikey's Song"],
     "exacta_pay": 5.20, "trifecta_pay": 11.60, "superfecta_pay": 28.00,
     "win_pay": 2.80, "place_pay": 2.10, "show_pay": 2.10},
    {"day": "Parx Mar 18", "race": 3, "type": "MC", "starters": 6,
     "ml_odds": {"Honor for Mandin": 20, "Chartage": 1.6, "Little Sneckdraw": 12, "Tap the Devil": 8, "Mucho Magnifico": 3.5, "Winning Song": 1.8},
     "finish": ["Chartage", "Winning Song", "Little Sneckdraw"],
     "exacta_pay": 6.80, "trifecta_pay": 13.20, "superfecta_pay": None,
     "win_pay": 3.20, "place_pay": 2.10, "show_pay": 2.10},
    {"day": "Parx Mar 18", "race": 4, "type": "CLM", "starters": 6,
     "ml_odds": {"Inamorata": 10, "Ravenite": 12, "Laughing Lady": 2, "It's a Shore Thing": 5, "Sandy Girl": 2.5, "My Vanilla": 3},
     "finish": ["It's a Shore Thing", "Inamorata", "Ravenite", "Sandy Girl"],
     "exacta_pay": 42.60, "trifecta_pay": 147.40, "superfecta_pay": 400.00,
     "win_pay": 9.00, "place_pay": 5.00, "show_pay": 3.40},
    {"day": "Parx Mar 18", "race": 5, "type": "MC", "starters": 7,
     "ml_odds": {"Quetzal Island": 10, "Battle Lou": 5, "El Huirro": 6, "King Barou": 4, "The Beast Master": 5, "Cap'n Cats": 2.5, "Walkers Beach": 3},
     "finish": ["King Barou", "Cap'n Cats", "Quetzal Island"],
     "exacta_pay": 10.00, "trifecta_pay": 35.80, "superfecta_pay": None,
     "win_pay": 5.60, "place_pay": 2.80, "show_pay": 2.20},
    {"day": "Parx Mar 18", "race": 6, "type": "CLM", "starters": 9,
     "ml_odds": {"Cattin": 20, "Mega Charlie": 15, "Wicked Genius": 15, "Arak": 3, "Tiempo Perfecto": 4,
                 "Lunar Rocket": 15, "Time Tested": 2.5, "H C Holiday": 12, "Jigsaw": 6},
     "finish": ["H C Holiday", "Arak", "Cattin", "Time Tested"],
     "exacta_pay": 82.60, "trifecta_pay": 322.80, "superfecta_pay": 1044.00,
     "win_pay": 19.80, "place_pay": 7.00, "show_pay": 4.20},
    {"day": "Parx Mar 18", "race": 7, "type": "MSW", "starters": 8,
     "ml_odds": {"Thisgirlsgotchill": 6, "South Boundary": 6, "Honorisia": 12, "Stately Girl": 6,
                 "Exciter": 4, "Sea Eff P T O": 6, "Dreaming of Bella": 3, "Into Hijinks": 3.5},
     "finish": ["Exciter", "Stately Girl", "Thisgirlsgotchill", "Into Hijinks"],
     "exacta_pay": 23.00, "trifecta_pay": 84.80, "superfecta_pay": 275.60,
     "win_pay": 6.80, "place_pay": 3.40, "show_pay": 2.80},
    {"day": "Parx Mar 18", "race": 8, "type": "SOC", "starters": 7,
     "ml_odds": {"Marelow": 4, "Mo Attitude": 3.5, "More Than Grace": 6, "Give Her Another": 5,
                 "Sevenon": 6, "Alyvia Mavis": 3, "Didn't It Rain": 6},
     "finish": ["More Than Grace", "Mo Attitude", "Marelow", "Give Her Another"],
     "exacta_pay": 58.40, "trifecta_pay": 91.40, "superfecta_pay": 500.80,
     "win_pay": 6.40, "place_pay": 4.40, "show_pay": 2.60},
    {"day": "Parx Mar 18", "race": 9, "type": "CLM", "starters": 6,
     "ml_odds": {"Union Purrfection": 10, "Chance": 1.2, "Fluff the Pillow": 12, "Heat Alert": 3, "Inmortal J": 5, "Modica": 6},
     "finish": ["Chance", "Modica", "Heat Alert"],
     "exacta_pay": 31.00, "trifecta_pay": None, "superfecta_pay": None,
     "win_pay": 2.60, "place_pay": 2.20, "show_pay": 2.10},
    {"day": "Parx Mar 18", "race": 10, "type": "CLM", "starters": 6,
     "ml_odds": {"Horse1": 3, "Horse2": 4, "Horse3": 5, "Horse4": 6, "Get Like Mike": 5, "Horse6": 8},
     "finish": ["Get Like Mike", "Horse1", "Horse2"],
     "exacta_pay": 15.00, "trifecta_pay": 50.00, "superfecta_pay": None,
     "win_pay": 8.00, "place_pay": 4.00, "show_pay": 3.00},

    # ====== PARX MARCH 17, 2026 ======
    {"day": "Parx Mar 17", "race": 1, "type": "CLM", "starters": 8,
     "ml_odds": {"Back East": 20, "Bourbon Aficionado": 5, "Fazaro": 6, "Azure Lady": 5,
                 "Bad Advice": 4.5, "Cisco Kid": 3, "Onlygodcanjudgeme": 20, "Tojo's Mojo": 2.5},
     "finish": ["Tojo's Mojo", "Bourbon Aficionado", "Cisco Kid", "Bad Advice"],
     "exacta_pay": 18.40, "trifecta_pay": 40.60, "superfecta_pay": 54.80,
     "win_pay": 5.60, "place_pay": 3.20, "show_pay": 2.20},
    {"day": "Parx Mar 17", "race": 2, "type": "CLM", "starters": 7,
     "ml_odds": {"Mister Lincoln": 6, "Midlaner": 5, "Easy Action": 2, "Nancy Made My Day": 6,
                 "Shipman": 5, "Three Captains": 6, "Mac Daddy Too": 4},
     "finish": ["Easy Action", "Three Captains", "Mac Daddy Too", "Midlaner"],
     "exacta_pay": 40.40, "trifecta_pay": 123.60, "superfecta_pay": 479.20,
     "win_pay": 3.00, "place_pay": 2.40, "show_pay": 2.10},
    {"day": "Parx Mar 17", "race": 3, "type": "MC", "starters": 7,
     "ml_odds": {"Buff Gary": 4, "Nomowineforyou": 2, "Nakimax": 12, "Tongue Tied": 15,
                 "King of the Cross": 5, "Disco Rhodes": 2.5, "Slew of Fortune": 15},
     "finish": ["Nomowineforyou", "Buff Gary", "King of the Cross", "Tongue Tied"],
     "exacta_pay": 9.60, "trifecta_pay": 26.80, "superfecta_pay": 82.20,
     "win_pay": 3.60, "place_pay": 2.20, "show_pay": 2.10},
    {"day": "Parx Mar 17", "race": 4, "type": "CLM", "starters": 7,
     "ml_odds": {"Waitwaitdonttellme": 15, "Fuhgeddaboudit": 4, "Burning Embers": 8, "Sheza Bernardini": 3,
                 "Sofster": 5, "Pontiffany": 2, "Girlfromouterspace": 8},
     "finish": ["Pontiffany", "Fuhgeddaboudit", "Sheza Bernardini", "Sofster"],
     "exacta_pay": 21.80, "trifecta_pay": 44.80, "superfecta_pay": 167.40,
     "win_pay": 5.80, "place_pay": 3.80, "show_pay": 2.20},
    {"day": "Parx Mar 17", "race": 5, "type": "MC", "starters": 8,
     "ml_odds": {"Breezefromtheeast": 3.5, "J K Strong": 2.5, "Hart of Coupella": 15, "Always in Play": 6,
                 "Breeze Along Belle": 6, "Sacred Prayer": 6, "Shaunnasaprilfool": 6, "Bulma": 5},
     "finish": ["Breezefromtheeast", "Always in Play", "Bulma", "Sacred Prayer"],
     "exacta_pay": 60.60, "trifecta_pay": 248.40, "superfecta_pay": 836.00,
     "win_pay": 6.40, "place_pay": 3.80, "show_pay": 2.80},
    {"day": "Parx Mar 17", "race": 6, "type": "CLM", "starters": 9,
     "ml_odds": {"Adios Jersey": 3, "Twenty One Kid": 10, "Biagio": 8, "Carbonite": 10,
                 "Celestial Dark": 20, "Authentic Kingdom": 4.5, "Rainy Skies": 10, "Capital Conquest": 8, "Twentyeighttothree": 4},
     "finish": ["Biagio", "Adios Jersey", "Celestial Dark", "Carbonite"],
     "exacta_pay": 95.60, "trifecta_pay": 2661.00, "superfecta_pay": 11895.80,
     "win_pay": 16.80, "place_pay": 7.60, "show_pay": 5.60},
    {"day": "Parx Mar 17", "race": 7, "type": "SOC", "starters": 8,
     "ml_odds": {"Leretha": 12, "Perugia": 5, "I Am Rue": 4, "Mila Rose": 4.5,
                 "House of Magic": 3.5, "Shubagail": 6, "Byebyejealouseye": 6, "Tavria": 20},
     "finish": ["I Am Rue", "Byebyejealouseye", "Shubagail", "Leretha"],
     "exacta_pay": 76.20, "trifecta_pay": 239.60, "superfecta_pay": 782.60,
     "win_pay": 9.60, "place_pay": 4.60, "show_pay": 3.40},
    {"day": "Parx Mar 17", "race": 8, "type": "SOC", "starters": 6,
     "ml_odds": {"Spicy Delight": 6, "Center Stage": 5, "Pachelbel": 2.5, "Lovely Charm": 3.5,
                 "Jess's Moment": 6, "Golden Eib Micrphn": 2},
     "finish": ["Golden Eib Micrphn", "Pachelbel", "Jess's Moment", "Spicy Delight"],
     "exacta_pay": 21.00, "trifecta_pay": 79.20, "superfecta_pay": 269.80,
     "win_pay": 9.40, "place_pay": 4.00, "show_pay": 2.80},

    # ====== PARX MARCH 16, 2026 ======
    {"day": "Parx Mar 16", "race": 1, "type": "CLM", "starters": 8,
     "ml_odds": {"Horse_A": 2.5, "Horse_B": 5, "Horse_C": 6, "Horse_D": 8, "Horse_E": 3, "King Phoenix": 2.5, "Horse_G": 10, "Horse_H": 15},
     "finish": ["King Phoenix", "Horse_B", "Horse_D"],
     "exacta_pay": 7.80, "trifecta_pay": 29.40, "superfecta_pay": 53.80,
     "win_pay": 3.20, "place_pay": 2.20, "show_pay": 2.10},
    {"day": "Parx Mar 16", "race": 2, "type": "CLM", "starters": 7,
     "ml_odds": {"Horse_A": 5, "Horse_B": 3, "Horse_C": 8, "Horse_D": 10, "Z Storm": 5, "Horse_F": 6, "Horse_G": 4},
     "finish": ["Z Storm", "Horse_A", "Horse_F"],
     "exacta_pay": 36.60, "trifecta_pay": 1103.80, "superfecta_pay": 5622.80,
     "win_pay": 9.80, "place_pay": 5.00, "show_pay": 4.40},
    {"day": "Parx Mar 16", "race": 3, "type": "CLM", "starters": 6,
     "ml_odds": {"Horse_A": 4, "Horse_B": 3, "Rozzyroo": 2, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10},
     "finish": ["Rozzyroo", "Horse_B", "Horse_E"],
     "exacta_pay": 8.40, "trifecta_pay": 11.80, "superfecta_pay": None,
     "win_pay": 4.20, "place_pay": 2.40, "show_pay": 2.10},
    {"day": "Parx Mar 16", "race": 4, "type": "SOC", "starters": 5,
     "ml_odds": {"Horse_A": 4, "Untouchable": 3, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8},
     "finish": ["Untouchable", "Horse_D", "Horse_C"],
     "exacta_pay": 4.00, "trifecta_pay": None, "superfecta_pay": None,
     "win_pay": 3.40, "place_pay": None, "show_pay": None},
    {"day": "Parx Mar 16", "race": 5, "type": "CLM", "starters": 7,
     "ml_odds": {"Horse_A": 6, "Quivira Crane": 3.5, "Horse_C": 5, "Horse_D": 4, "Horse_E": 8, "Horse_F": 10, "Horse_G": 12},
     "finish": ["Quivira Crane", "Horse_A", "Horse_D"],
     "exacta_pay": 8.40, "trifecta_pay": 20.00, "superfecta_pay": None,
     "win_pay": 6.80, "place_pay": 2.80, "show_pay": 2.10},
    {"day": "Parx Mar 16", "race": 6, "type": "MSW", "starters": 8,
     "ml_odds": {"Horse_A": 6, "Peacefulezfeeling": 3, "Horse_C": 8, "Horse_D": 10, "Horse_E": 5, "Horse_F": 4, "Horse_G": 12, "Horse_H": 15},
     "finish": ["Peacefulezfeeling", "Horse_A", "Horse_C"],
     "exacta_pay": 90.20, "trifecta_pay": 210.60, "superfecta_pay": 477.00,
     "win_pay": 11.80, "place_pay": 6.60, "show_pay": 3.20},
    {"day": "Parx Mar 16", "race": 7, "type": "CLM", "starters": 8,
     "ml_odds": {"Horse_A": 5, "Horse_B": 6, "Horse_C": 8, "Horse_D": 3, "Horse_E": 10, "All American Rod": 4, "Horse_G": 4.5, "Horse_H": 12},
     "finish": ["All American Rod", "Horse_G", "Horse_A"],
     "exacta_pay": 84.80, "trifecta_pay": 283.40, "superfecta_pay": 1027.40,
     "win_pay": 7.20, "place_pay": 4.20, "show_pay": 2.60},
    {"day": "Parx Mar 16", "race": 8, "type": "CLM", "starters": 7,
     "ml_odds": {"Horse_A": 4, "Horse_B": 5, "Jackson Road": 1.8, "Horse_D": 3, "Horse_E": 6, "Horse_F": 8, "Horse_G": 10},
     "finish": ["Jackson Road", "Horse_D", "Horse_E"],
     "exacta_pay": 28.00, "trifecta_pay": 165.40, "superfecta_pay": 466.40,
     "win_pay": 7.80, "place_pay": 3.20, "show_pay": 2.40},
    {"day": "Parx Mar 16", "race": 9, "type": "SOC", "starters": 7,
     "ml_odds": {"Horse_A": 5, "Hermoso Hombre": 3, "Horse_C": 6, "Horse_D": 4, "Horse_E": 8, "Horse_F": 10, "Horse_G": 12},
     "finish": ["Hermoso Hombre", "Horse_C", "Horse_F"],
     "exacta_pay": 23.00, "trifecta_pay": 205.60, "superfecta_pay": 372.60,
     "win_pay": 4.60, "place_pay": 3.00, "show_pay": 2.80},

    # ====== FAIR GROUNDS MARCH 16, 2026 ======
    {"day": "FG Mar 16", "race": 1, "type": "MC", "starters": 7,
     "ml_odds": {"Horse_A": 3, "Horse_B": 5, "Horse_C": 6, "Horse_D": 8, "Hannah Boo": 4, "Horse_F": 10, "Horse_G": 12},
     "finish": ["Hannah Boo", "Horse_B", "Horse_D"],
     "exacta_pay": 24.60, "trifecta_pay": 100.00, "superfecta_pay": 369.40,
     "win_pay": 6.60, "place_pay": 3.20, "show_pay": 2.80},
    {"day": "FG Mar 16", "race": 2, "type": "CLM", "starters": 8,
     "ml_odds": {"Horse_A": 3, "Ice Cold Blonde": 2, "Horse_C": 5, "Horse_D": 4, "Horse_E": 6, "Horse_F": 8, "Horse_G": 10, "Horse_H": 15},
     "finish": ["Ice Cold Blonde", "Horse_D", "Horse_C"],
     "exacta_pay": 12.60, "trifecta_pay": 16.40, "superfecta_pay": 35.60,
     "win_pay": 5.20, "place_pay": 2.80, "show_pay": 2.10},
    {"day": "FG Mar 16", "race": 3, "type": "SOC", "starters": 9,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Fortuity": 20, "Horse_G": 10, "Horse_H": 12, "Horse_I": 15},
     "finish": ["Fortuity", "Horse_B", "Horse_I"],
     "exacta_pay": 412.60, "trifecta_pay": 1372.80, "superfecta_pay": 32496.80,
     "win_pay": 55.60, "place_pay": 25.60, "show_pay": 8.60},
    {"day": "FG Mar 16", "race": 4, "type": "ALW", "starters": 5,
     "ml_odds": {"Horse_A": 4, "Horse_B": 3, "Horse_C": 6, "Horse_D": 5, "A.P.'s Girl": 2},
     "finish": ["A.P.'s Girl", "Horse_D", "Horse_C"],
     "exacta_pay": 22.80, "trifecta_pay": 31.20, "superfecta_pay": None,
     "win_pay": 4.00, "place_pay": 2.80, "show_pay": None},
    {"day": "FG Mar 16", "race": 5, "type": "CLM", "starters": 9,
     "ml_odds": {"Horse_A": 4, "Horse_B": 5, "Kin to the Wicked": 2, "Horse_D": 6, "Horse_E": 3, "Horse_F": 8, "Horse_G": 10, "Horse_H": 12, "Horse_I": 15},
     "finish": ["Kin to the Wicked", "Horse_E", "Horse_I"],
     "exacta_pay": 14.40, "trifecta_pay": 99.40, "superfecta_pay": 331.20,
     "win_pay": 2.60, "place_pay": 2.10, "show_pay": 2.10},
    {"day": "FG Mar 16", "race": 6, "type": "CLM", "starters": 10,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10,
                 "Horse_G": 12, "Horse_H": 15, "Next Level": 8, "Horse_J": 20},
     "finish": ["Next Level", "Horse_F", "Horse_D"],
     "exacta_pay": 57.40, "trifecta_pay": 403.80, "superfecta_pay": 1019.80,
     "win_pay": 18.40, "place_pay": 8.00, "show_pay": 5.80},
    {"day": "FG Mar 16", "race": 7, "type": "MC", "starters": 8,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10, "General Graham": 5, "Horse_H": 12},
     "finish": ["General Graham", "Horse_F", "Horse_A"],
     "exacta_pay": 34.00, "trifecta_pay": 234.40, "superfecta_pay": 1913.00,
     "win_pay": 5.40, "place_pay": 3.60, "show_pay": 3.00},
    {"day": "FG Mar 16", "race": 8, "type": "AOC", "starters": 8,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10, "Vesture": 5, "Horse_H": 3},
     "finish": ["Vesture", "Horse_H", "Horse_C"],
     "exacta_pay": 23.20, "trifecta_pay": 163.20, "superfecta_pay": 584.60,
     "win_pay": 5.40, "place_pay": 3.40, "show_pay": 2.60},

    # ====== FAIR GROUNDS MARCH 15, 2026 ======
    {"day": "FG Mar 15", "race": 1, "type": "CLM", "starters": 9,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Like This": 10,
                 "Horse_F": 8, "Horse_G": 12, "Horse_H": 15, "Horse_I": 20},
     "finish": ["Like This", "Horse_C", "Horse_A"],
     "exacta_pay": 63.40, "trifecta_pay": 1398.40, "superfecta_pay": 7821.20,
     "win_pay": 9.00, "place_pay": 4.60, "show_pay": 3.60},
    {"day": "FG Mar 15", "race": 2, "type": "CLM", "starters": 6,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Sand Cast": 5, "Horse_F": 8},
     "finish": ["Sand Cast", "Horse_F", "Horse_C"],
     "exacta_pay": 224.60, "trifecta_pay": 696.40, "superfecta_pay": 2204.80,
     "win_pay": 9.40, "place_pay": 5.60, "show_pay": 3.00},
    {"day": "FG Mar 15", "race": 3, "type": "MSW", "starters": 10,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Victory Prince": 2, "Horse_E": 6, "Horse_F": 8,
                 "Horse_G": 10, "Horse_H": 12, "Horse_I": 15, "Horse_J": 20},
     "finish": ["Victory Prince", "Horse_J", "Horse_F"],
     "exacta_pay": 34.80, "trifecta_pay": 683.20, "superfecta_pay": 6256.40,
     "win_pay": 3.20, "place_pay": 2.20, "show_pay": 2.20},
    {"day": "FG Mar 15", "race": 4, "type": "SOC", "starters": 8,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10, "Notion": 3, "Horse_H": 12},
     "finish": ["Notion", "Horse_B", "Horse_A"],
     "exacta_pay": 36.40, "trifecta_pay": 211.20, "superfecta_pay": 1115.20,
     "win_pay": 9.80, "place_pay": 4.40, "show_pay": 2.80},
    {"day": "FG Mar 15", "race": 5, "type": "AOC", "starters": 10,
     "ml_odds": {"In B.J.'s Honor": 6, "Horse_B": 3, "Horse_C": 4, "Horse_D": 5, "Horse_E": 8,
                 "Horse_F": 10, "Horse_G": 12, "Horse_H": 15, "Horse_I": 20, "Horse_J": 6},
     "finish": ["In B.J.'s Honor", "Horse_G", "Horse_C"],
     "exacta_pay": 47.00, "trifecta_pay": 821.60, "superfecta_pay": 3548.20,
     "win_pay": 8.40, "place_pay": 4.60, "show_pay": 3.60},
    {"day": "FG Mar 15", "race": 6, "type": "AOC", "starters": 6,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Furio": 2.5, "Horse_E": 6, "Horse_F": 8},
     "finish": ["Furio", "Horse_B", "Horse_F"],
     "exacta_pay": 16.80, "trifecta_pay": 83.60, "superfecta_pay": 240.60,
     "win_pay": 5.00, "place_pay": 3.40, "show_pay": 2.80},
    {"day": "FG Mar 15", "race": 7, "type": "MSW", "starters": 8,
     "ml_odds": {"Horse_A": 3, "Horse_B": 4, "One More Guitar": 4.5, "Horse_D": 5, "Horse_E": 6, "Horse_F": 8, "Horse_G": 10, "Horse_H": 12},
     "finish": ["One More Guitar", "Horse_G", "Horse_D"],
     "exacta_pay": 25.40, "trifecta_pay": 65.00, "superfecta_pay": 747.80,
     "win_pay": 10.40, "place_pay": 4.00, "show_pay": 2.80},
    {"day": "FG Mar 15", "race": 8, "type": "CLM", "starters": 10,
     "ml_odds": {"Horse_A": 3, "Iron in the Fire": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8,
                 "Horse_F": 10, "Horse_G": 12, "Horse_H": 15, "Horse_I": 20, "Horse_J": 6},
     "finish": ["Iron in the Fire", "Horse_C", "Horse_G"],
     "exacta_pay": None, "trifecta_pay": None, "superfecta_pay": None,
     "win_pay": 16.40, "place_pay": 4.80, "show_pay": 3.40},
]


def get_ml_sorted(race):
    """Get horses sorted by ML odds (lowest = most favored)."""
    return sorted(race["ml_odds"].items(), key=lambda x: x[1])


def get_ml_top_n(race, n):
    """Get the top N horses by ML odds."""
    return [h[0] for h in get_ml_sorted(race)[:n]]


def get_ml_rank(race, horse):
    """Get ML rank of a horse (1=favorite)."""
    sorted_h = get_ml_sorted(race)
    for i, (name, _) in enumerate(sorted_h):
        if name == horse:
            return i + 1
    return 999


def get_competitiveness(race):
    """Score how competitive/open a race is (high = competitive, no clear fav)."""
    odds = sorted(race["ml_odds"].values())
    if len(odds) < 2:
        return 0
    # Ratio of 2nd favorite to favorite — higher = more competitive
    return odds[1] / odds[0]


def race_has_value_spread(race):
    """Check if there's a big spread between top ML and mid-pack (value opportunity)."""
    odds = sorted(race["ml_odds"].values())
    if len(odds) < 4:
        return False
    # If favorite is 2/1 or less but 4th pick is 6/1+, there's value in the exotics
    return odds[0] <= 3 and odds[3] >= 6


# ============== STRATEGY FUNCTIONS ==============

def strat_trifecta_big_fields_only(races, top_n=5, bet=0.50, min_starters=8):
    """Trifecta box in big fields only — where payouts justify cost."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("trifecta_pay"):
            continue

        day = race["day"]
        top = get_ml_top_n(race, top_n)
        combos = top_n * (top_n - 1) * (top_n - 2)
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 3 and all(f in top for f in finish[:3]):
            payout = race["trifecta_pay"] * (bet / 2.0)
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_superfecta_big_fields(races, top_n=6, bet=0.10, min_starters=8):
    """Superfecta box in big fields — tiny bet, huge payout potential."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("superfecta_pay"):
            continue

        day = race["day"]
        top = get_ml_top_n(race, top_n)
        combos = top_n * (top_n - 1) * (top_n - 2) * (top_n - 3)
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 4 and all(f in top for f in finish[:4]):
            payout = race["superfecta_pay"] * (bet / 2.0)
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_exacta_key_fav_with_value(races, key_bet=1.0, min_starters=7):
    """KEY the ML favorite on top AND bottom with horses ranked 3-6 by ML.
    Skip the #2 ML pick (already obvious), focus on value horses underneath.
    Cheaper than boxing — only 2*(N-1) combos instead of N*(N-1)."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue

        day = race["day"]
        ml_sorted = get_ml_sorted(race)
        fav = ml_sorted[0][0]  # ML favorite
        # Use horses ranked 3-6 (skip #2 which is obvious)
        value_horses = [h[0] for h in ml_sorted[2:6]]

        # KEY: fav on top with value, plus value on top with fav
        # = len(value) * 2 combos
        num_combos = len(value_horses) * 2
        cost = key_bet * num_combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 2:
            first, second = finish[0], finish[1]
            # Hit if fav is in top 2 AND any value horse is in top 2
            if (first == fav and second in value_horses) or \
               (first in value_horses and second == fav):
                payout = race["exacta_pay"] * (key_bet / 2.0) if race["exacta_pay"] else 0
                total_r += payout
                daily[day]["r"] += payout
                hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_exacta_key_top2_with_field(races, key_bet=0.50, min_starters=7):
    """KEY ML top 2 each on top with ML 3-5 underneath.
    = 2 keys * 3 with-horses = 6 combos per race ($3 at $0.50)
    Plus reverse: ML 3-5 on top with ML top 2 underneath = 3*2 = 6 more ($3)
    Total: 12 combos = $6/race at $0.50."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue

        day = race["day"]
        ml_sorted = get_ml_sorted(race)
        top2 = [h[0] for h in ml_sorted[:2]]
        mid = [h[0] for h in ml_sorted[2:5]]

        all_covered = top2 + mid  # 5 horses total
        # Exacta combos: any of these 5 in 1st, any other of these 5 in 2nd
        # But we're being selective — only top2 with mid and vice versa
        # top2 on top with mid: 2*3 = 6
        # mid on top with top2: 3*2 = 6
        # Total: 12 combos
        num_combos = 12
        cost = key_bet * num_combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 2:
            first, second = finish[0], finish[1]
            hit = False
            if first in top2 and second in mid:
                hit = True
            elif first in mid and second in top2:
                hit = True
            if hit:
                payout = race["exacta_pay"] * (key_bet / 2.0) if race["exacta_pay"] else 0
                total_r += payout
                daily[day]["r"] += payout
                hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_competitive_races_only(races, competitiveness_min=1.3, top_n=5,
                                  ex_bet=0.50, tri_bet=0.50, tri_min=8):
    """Only bet competitive races (no heavy favorite). These have bigger payouts."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    ex_hits, ex_plays = 0, 0
    tri_hits, tri_plays = 0, 0

    for race in races:
        comp = get_competitiveness(race)
        if comp < competitiveness_min:
            continue

        day = race["day"]
        top = get_ml_top_n(race, top_n)
        finish = race["finish"]

        # Exacta box
        if race["starters"] >= 7:
            combos = top_n * (top_n - 1)
            cost = ex_bet * combos
            total_w += cost
            daily[day]["w"] += cost
            ex_plays += 1
            if len(finish) >= 2 and finish[0] in top and finish[1] in top:
                payout = race["exacta_pay"] * (ex_bet / 2.0) if race["exacta_pay"] else 0
                total_r += payout
                daily[day]["r"] += payout
                ex_hits += 1

        # Trifecta box
        if race["starters"] >= tri_min and race.get("trifecta_pay"):
            top_tri = get_ml_top_n(race, 4)
            combos = 24
            cost = tri_bet * combos
            total_w += cost
            daily[day]["w"] += cost
            tri_plays += 1
            if len(finish) >= 3 and all(f in top_tri for f in finish[:3]):
                payout = race["trifecta_pay"] * (tri_bet / 2.0) if race["trifecta_pay"] else 0
                total_r += payout
                daily[day]["r"] += payout
                tri_hits += 1

    return {"w": total_w, "r": total_r, "ex_hits": ex_hits, "ex_plays": ex_plays,
            "tri_hits": tri_hits, "tri_plays": tri_plays, "daily": dict(daily)}


def strat_value_spread_races(races, ex_bet=0.50, tri_bet=0.50):
    """Only bet races with big ML spread (chalk fav + longshot possibilities).
    These races produce the biggest exotic payouts."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if not race_has_value_spread(race):
            continue
        if race["starters"] < 7:
            continue

        day = race["day"]
        top5 = get_ml_top_n(race, 5)
        finish = race["finish"]

        # Trifecta box top 5
        if race.get("trifecta_pay") and race["starters"] >= 8:
            combos = 60  # 5*4*3
            cost = tri_bet * combos
            total_w += cost
            daily[day]["w"] += cost
            plays += 1
            if len(finish) >= 3 and all(f in top5 for f in finish[:3]):
                payout = race["trifecta_pay"] * (tri_bet / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_trifecta_key_fav(races, bet=0.50, min_starters=8, with_n=4):
    """KEY the ML favorite on top, box the next N underneath.
    Much cheaper than a full trifecta box.
    Combos: with_n * (with_n-1) = 12 at with_n=4, vs 60 for a 5-box."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("trifecta_pay"):
            continue

        day = race["day"]
        ml_sorted = get_ml_sorted(race)
        fav = ml_sorted[0][0]
        with_horses = [h[0] for h in ml_sorted[1:1+with_n]]

        combos = with_n * (with_n - 1)  # Fav on top, permutations of with underneath
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 3:
            if finish[0] == fav and finish[1] in with_horses and finish[2] in with_horses:
                payout = race["trifecta_pay"] * (bet / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_place_grind(races, bet=5.0):
    """Place bet on ML favorite every race. Favorites place (1st or 2nd) ~60% of time.
    Lower takeout (15-17%) than exotics."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        day = race["day"]
        fav = get_ml_top_n(race, 1)[0]
        total_w += bet
        daily[day]["w"] += bet
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if fav in finish[:2]:  # Placed 1st or 2nd
            if fav == finish[0]:
                # Winner — use place_pay
                payout = race["place_pay"] * (bet / 2.0) if race.get("place_pay") else bet * 1.2
            else:
                # 2nd place — approximate: place_pay * 0.85
                payout = race["place_pay"] * (bet / 2.0) * 0.85 if race.get("place_pay") else bet * 1.05
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_show_grind(races, bet=5.0):
    """Show bet on ML favorite every race. Favorites show (top 3) ~70% of time."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        day = race["day"]
        fav = get_ml_top_n(race, 1)[0]
        total_w += bet
        daily[day]["w"] += bet
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if fav in finish[:3]:  # Top 3
            if fav == finish[0]:
                payout = race["show_pay"] * (bet / 2.0) if race.get("show_pay") else bet * 1.05
            else:
                # Non-winner show pay is typically slightly less
                payout = race["show_pay"] * (bet / 2.0) * 0.9 if race.get("show_pay") else bet * 1.02
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_win_longshot_value(races, min_ml=5, max_ml=12, bet=5.0):
    """Win bet ONLY on ML value range (5/1 to 12/1 winners).
    These hit less often but when they do, the payout is big."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        day = race["day"]
        # Check if any horse in target ML range
        targets = [(h, o) for h, o in race["ml_odds"].items() if min_ml <= o <= max_ml]
        if not targets:
            continue

        # Bet on the lowest-odds horse in the value range (most likely to hit)
        targets.sort(key=lambda x: x[1])
        target_horse = targets[0][0]

        total_w += bet
        daily[day]["w"] += bet
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if finish[0] == target_horse:
            payout = race["win_pay"] * (bet / 2.0) if race.get("win_pay") else 0
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_superfecta_all_in(races, top_n=8, bet=0.10, min_starters=9):
    """$0.10 superfecta box on top 8 by ML in 9+ starter races.
    Hit rate is low but payouts are MASSIVE (often $500-$10,000+).
    Cost: 8*7*6*5 * $0.10 = $168/race — too expensive for box.
    Use partial wheel instead: KEY top 2 on top, top 6 underneath."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("superfecta_pay"):
            continue

        day = race["day"]
        ml_sorted = get_ml_sorted(race)
        top2 = [h[0] for h in ml_sorted[:2]]
        next_n = [h[0] for h in ml_sorted[2:top_n]]
        all_horses = top2 + next_n

        # Partial: top2 on top, any 3 of remaining underneath
        # Each top2 horse: C(next_n, 3) * 3! arrangements = len(next_n)*(len(next_n)-1)*(len(next_n)-2)
        # For 2 key horses: 2 * (n-2)*(n-3)*(n-4) where n = top_n
        n = len(next_n)
        if n < 3:
            continue
        combos_per_key = n * (n-1) * (n-2)
        total_combos = 2 * combos_per_key
        cost = bet * total_combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 4:
            if finish[0] in top2 and finish[1] in all_horses and \
               finish[2] in all_horses and finish[3] in all_horses:
                payout = race["superfecta_pay"] * (bet / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_trifecta_wide_big_fields(races, top_n=6, bet=0.20, min_starters=9):
    """Wide trifecta box (top 6 ML) at $0.20 in 9+ starters.
    More expensive but catches way more trifectas. Big fields = big payouts."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("trifecta_pay"):
            continue

        day = race["day"]
        top = get_ml_top_n(race, top_n)
        combos = top_n * (top_n-1) * (top_n-2)
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 3 and all(f in top for f in finish[:3]):
            payout = race["trifecta_pay"] * (bet / 2.0)
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_contrarian_exacta(races, bet=1.0, min_starters=7):
    """Contrarian: KEY ML #3-#5 on top with ML #1-#2 underneath.
    Bets on non-favorites winning but favorites placing.
    Catches upsets with big payouts."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue

        day = race["day"]
        ml_sorted = get_ml_sorted(race)
        top2 = [h[0] for h in ml_sorted[:2]]
        mid = [h[0] for h in ml_sorted[2:5]]

        # Mid horses on top, top2 underneath
        combos = len(mid) * len(top2)  # 3*2 = 6
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 2:
            if finish[0] in mid and finish[1] in top2:
                payout = race["exacta_pay"] * (bet / 2.0) if race["exacta_pay"] else 0
                total_r += payout
                daily[day]["r"] += payout
                hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_contrarian_trifecta(races, bet=0.50, min_starters=8):
    """Contrarian trifecta: ML #2-#5 in top 3, exclude the heavy favorite.
    When the favorite loses but top contenders fill the frame."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("trifecta_pay"):
            continue

        day = race["day"]
        ml_sorted = get_ml_sorted(race)
        # Skip fav, use #2-#5
        contenders = [h[0] for h in ml_sorted[1:5]]

        combos = 4 * 3 * 2  # 24
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 3 and all(f in contenders for f in finish[:3]):
            payout = race["trifecta_pay"] * (bet / 2.0)
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_combo_tri_plus_super(races, tri_bet=0.50, super_bet=0.10,
                                 tri_top=5, super_top=6, min_starters=8):
    """Combined: trifecta box + superfecta partial in big fields.
    The superfecta is a saver — if you hit tri, you probably hit super too."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})

    for race in races:
        if race["starters"] < min_starters:
            continue
        day = race["day"]
        finish = race["finish"]

        # Trifecta
        if race.get("trifecta_pay"):
            top = get_ml_top_n(race, tri_top)
            combos = tri_top * (tri_top-1) * (tri_top-2)
            cost = tri_bet * combos
            total_w += cost
            daily[day]["w"] += cost
            if len(finish) >= 3 and all(f in top for f in finish[:3]):
                total_r += race["trifecta_pay"] * (tri_bet / 2.0)
                daily[day]["r"] += race["trifecta_pay"] * (tri_bet / 2.0)

        # Superfecta
        if race.get("superfecta_pay"):
            top_s = get_ml_top_n(race, super_top)
            combos_s = super_top * (super_top-1) * (super_top-2) * (super_top-3)
            cost_s = super_bet * combos_s
            total_w += cost_s
            daily[day]["w"] += cost_s
            if len(finish) >= 4 and all(f in top_s for f in finish[:4]):
                total_r += race["superfecta_pay"] * (super_bet / 2.0)
                daily[day]["r"] += race["superfecta_pay"] * (super_bet / 2.0)

    return {"w": total_w, "r": total_r, "daily": dict(daily)}


def strat_exacta_skip_chalk(races, top_n=5, bet=0.50, min_starters=7, min_fav_odds=2.5):
    """Exacta box but SKIP races where the favorite is too heavy (under min_fav_odds).
    These chalk races produce tiny exacta payouts."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue

        # Skip if favorite is too heavy
        fav_odds = min(race["ml_odds"].values())
        if fav_odds < min_fav_odds:
            continue

        day = race["day"]
        top = get_ml_top_n(race, top_n)
        combos = top_n * (top_n - 1)
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        plays += 1

        finish = race["finish"]
        if len(finish) >= 2 and finish[0] in top and finish[1] in top:
            payout = race["exacta_pay"] * (bet / 2.0) if race["exacta_pay"] else 0
            total_r += payout
            daily[day]["r"] += payout
            hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


def strat_race_type_filter(races, allowed_types, ex_bet=0.50, tri_bet=0.50,
                            ex_top=5, tri_top=4, min_starters_ex=7, min_starters_tri=8):
    """Only bet on specific race types."""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0})

    for race in races:
        if race["type"] not in allowed_types:
            continue
        day = race["day"]
        finish = race["finish"]

        # Exacta
        if race["starters"] >= min_starters_ex:
            top = get_ml_top_n(race, ex_top)
            combos = ex_top * (ex_top - 1)
            cost = ex_bet * combos
            total_w += cost
            daily[day]["w"] = daily[day].get("w", 0) + cost
            if len(finish) >= 2 and finish[0] in top and finish[1] in top:
                payout = race["exacta_pay"] * (ex_bet / 2.0) if race["exacta_pay"] else 0
                total_r += payout
                daily[day]["r"] = daily[day].get("r", 0) + payout

        # Trifecta
        if race["starters"] >= min_starters_tri and race.get("trifecta_pay"):
            top = get_ml_top_n(race, tri_top)
            combos = tri_top * (tri_top-1) * (tri_top-2)
            cost = tri_bet * combos
            total_w += cost
            daily[day]["w"] = daily[day].get("w", 0) + cost
            if len(finish) >= 3 and all(f in top for f in finish[:3]):
                payout = race["trifecta_pay"] * (tri_bet / 2.0)
                total_r += payout
                daily[day]["r"] = daily[day].get("r", 0) + payout

    return {"w": total_w, "r": total_r, "daily": dict(daily)}


def strat_trifecta_key_top2_with_all(races, bet=0.50, min_starters=8, with_n=5):
    """KEY ML top 2 on top, with ML 3-7 underneath for trifecta.
    Both fav AND second fav must finish 1st/2nd (either order),
    3rd can be any of the with-horses.
    Combos: 2 * with_n (2 key arrangements * n options for 3rd)"""
    total_w, total_r = 0, 0
    daily = defaultdict(lambda: {"w": 0, "r": 0, "bets": 0})
    hits, plays = 0, 0

    for race in races:
        if race["starters"] < min_starters:
            continue
        if not race.get("trifecta_pay"):
            continue

        day = race["day"]
        ml_sorted = get_ml_sorted(race)
        top2 = [h[0] for h in ml_sorted[:2]]
        with_horses = [h[0] for h in ml_sorted[2:2+with_n]]

        # Key top2 in 1st/2nd (both orders), with any of with_horses in 3rd
        combos = 2 * len(with_horses)
        cost = bet * combos
        total_w += cost
        daily[day]["w"] += cost
        daily[day]["bets"] += 1
        plays += 1

        finish = race["finish"]
        if len(finish) >= 3:
            if finish[0] in top2 and finish[1] in top2 and finish[2] in with_horses:
                payout = race["trifecta_pay"] * (bet / 2.0)
                total_r += payout
                daily[day]["r"] += payout
                hits += 1

    return {"w": total_w, "r": total_r, "hits": hits, "plays": plays, "daily": dict(daily)}


# ============== PRINT RESULTS ==============

def print_result(name, r):
    net = r["r"] - r["w"]
    roi = (net / r["w"] * 100) if r["w"] > 0 else 0
    days = r.get("daily", {})
    profitable_days = sum(1 for d in days.values() if d.get("r", 0) > d.get("w", 0))

    hits_str = ""
    if "hits" in r and "plays" in r:
        rate = r["hits"]/r["plays"]*100 if r["plays"] > 0 else 0
        hits_str = f" | Hits: {r['hits']}/{r['plays']} ({rate:.0f}%)"

    marker = " *** PROFITABLE ***" if roi > 0 else ""
    print(f"{name:55s} W:${r['w']:7.1f} R:${r['r']:7.1f} Net:${net:+8.1f} ROI:{roi:+6.1f}% "
          f"Days:{profitable_days}/{len(days)}{hits_str}{marker}")


# ============== RUN ALL STRATEGIES ==============

if __name__ == "__main__":
    print("=" * 120)
    print("DEEP BACKTEST — 43 real races, 5 track-days (Parx Mar 16-18, Fair Grounds Mar 15-16)")
    print("All payouts are REAL from track results. $2 base used for payout scaling.")
    print("=" * 120)

    # ---- TRIFECTA STRATEGIES ----
    print("\n--- TRIFECTA STRATEGIES ---")
    for top_n in [4, 5, 6]:
        for bet in [0.20, 0.50, 1.0]:
            for min_s in [7, 8, 9]:
                r = strat_trifecta_big_fields_only(RACE_DATA, top_n=top_n, bet=bet, min_starters=min_s)
                if r["plays"] > 0:
                    print_result(f"Tri Box ML{top_n} ${bet:.2f} {min_s}+ starters", r)

    # ---- SUPERFECTA STRATEGIES ----
    print("\n--- SUPERFECTA STRATEGIES ---")
    for top_n in [5, 6, 7, 8]:
        for bet in [0.10, 0.20]:
            for min_s in [8, 9]:
                r = strat_superfecta_big_fields(RACE_DATA, top_n=top_n, bet=bet, min_starters=min_s)
                if r["plays"] > 0:
                    print_result(f"Super Box ML{top_n} ${bet:.2f} {min_s}+ starters", r)

    r = strat_superfecta_all_in(RACE_DATA, top_n=7, bet=0.10, min_starters=8)
    if r["plays"] > 0:
        print_result("Super Partial Key ML2+5 $0.10 8+", r)
    r = strat_superfecta_all_in(RACE_DATA, top_n=8, bet=0.10, min_starters=9)
    if r["plays"] > 0:
        print_result("Super Partial Key ML2+6 $0.10 9+", r)

    # ---- EXACTA STRATEGIES ----
    print("\n--- EXACTA STRATEGIES ---")
    for top_n in [3, 4, 5]:
        for bet in [0.50, 1.0]:
            for min_s in [7, 8]:
                r = strat_exacta_skip_chalk(RACE_DATA, top_n=top_n, bet=bet, min_starters=min_s, min_fav_odds=0)
                if r["plays"] > 0:
                    print_result(f"Ex Box ML{top_n} ${bet:.2f} {min_s}+ all races", r)

    print("\n  -- Exacta: Skip chalk favorites --")
    for min_fav in [2.0, 2.5, 3.0, 3.5]:
        for top_n in [4, 5]:
            r = strat_exacta_skip_chalk(RACE_DATA, top_n=top_n, bet=0.50, min_starters=7, min_fav_odds=min_fav)
            if r["plays"] > 0:
                print_result(f"Ex Box ML{top_n} $0.50 7+ skip fav<{min_fav}", r)

    # ---- EXACTA KEY STRATEGIES ----
    print("\n--- EXACTA KEY STRATEGIES ---")
    for bet in [0.50, 1.0]:
        for min_s in [7, 8]:
            r = strat_exacta_key_fav_with_value(RACE_DATA, key_bet=bet, min_starters=min_s)
            if r["plays"] > 0:
                print_result(f"Ex Key Fav w/ ML3-6 ${bet:.2f} {min_s}+", r)

    for bet in [0.50, 1.0]:
        r = strat_exacta_key_top2_with_field(RACE_DATA, key_bet=bet, min_starters=7)
        if r["plays"] > 0:
            print_result(f"Ex Key Top2 w/ ML3-5 ${bet:.2f} 7+", r)

    # ---- CONTRARIAN STRATEGIES ----
    print("\n--- CONTRARIAN STRATEGIES ---")
    for bet in [0.50, 1.0, 2.0]:
        r = strat_contrarian_exacta(RACE_DATA, bet=bet, min_starters=7)
        if r["plays"] > 0:
            print_result(f"Contrarian Ex ML3-5 top / ML1-2 bottom ${bet:.2f}", r)

    for bet in [0.50, 1.0]:
        r = strat_contrarian_trifecta(RACE_DATA, bet=bet, min_starters=8)
        if r["plays"] > 0:
            print_result(f"Contrarian Tri ML2-5 skip fav ${bet:.2f} 8+", r)

    # ---- TRIFECTA KEY STRATEGIES ----
    print("\n--- TRIFECTA KEY STRATEGIES ---")
    for bet in [0.50, 1.0]:
        for with_n in [3, 4, 5]:
            for min_s in [7, 8, 9]:
                r = strat_trifecta_key_fav(RACE_DATA, bet=bet, min_starters=min_s, with_n=with_n)
                if r["plays"] > 0:
                    print_result(f"Tri Key Fav w/{with_n} ${bet:.2f} {min_s}+", r)

    for bet in [0.50, 1.0]:
        for with_n in [3, 4, 5]:
            r = strat_trifecta_key_top2_with_all(RACE_DATA, bet=bet, min_starters=8, with_n=with_n)
            if r["plays"] > 0:
                print_result(f"Tri Key Top2 w/{with_n} ${bet:.2f} 8+", r)

    # ---- COMPETITIVE RACE FILTERS ----
    print("\n--- COMPETITIVE RACE FILTERS ---")
    for comp_min in [1.2, 1.5, 1.8, 2.0]:
        r = strat_competitive_races_only(RACE_DATA, competitiveness_min=comp_min)
        if r["w"] > 0:
            print_result(f"Competitive {comp_min}+ Ex5+Tri4 8+", r)

    # ---- PLACE/SHOW GRIND ----
    print("\n--- PLACE / SHOW GRIND ---")
    for bet in [3, 5, 10]:
        r = strat_place_grind(RACE_DATA, bet=bet)
        print_result(f"Place Grind ML Fav ${bet}", r)
    for bet in [3, 5, 10]:
        r = strat_show_grind(RACE_DATA, bet=bet)
        print_result(f"Show Grind ML Fav ${bet}", r)

    # ---- WIN VALUE BETS ----
    print("\n--- WIN VALUE BETS ---")
    for min_ml, max_ml in [(4, 8), (5, 10), (5, 12), (6, 15), (3, 6)]:
        r = strat_win_longshot_value(RACE_DATA, min_ml=min_ml, max_ml=max_ml, bet=5.0)
        if r["plays"] > 0:
            print_result(f"Win Value ML {min_ml}-{max_ml} $5", r)

    # ---- RACE TYPE FILTERS ----
    print("\n--- RACE TYPE FILTERS ---")
    for types, label in [
        (["CLM"], "CLM only"),
        (["CLM", "MC"], "CLM+MC"),
        (["CLM", "MC", "SOC"], "CLM+MC+SOC"),
        (["MSW"], "MSW only"),
        (["SOC", "AOC"], "SOC+AOC"),
    ]:
        r = strat_race_type_filter(RACE_DATA, types)
        if r["w"] > 0:
            print_result(f"Type filter: {label} Ex5+Tri4", r)

    # ---- COMBO STRATEGIES ----
    print("\n--- COMBO: TRIFECTA + SUPERFECTA ---")
    for tri_bet in [0.20, 0.50]:
        for super_bet in [0.10, 0.20]:
            r = strat_combo_tri_plus_super(RACE_DATA, tri_bet=tri_bet, super_bet=super_bet,
                                            tri_top=5, super_top=6, min_starters=8)
            if r["w"] > 0:
                print_result(f"Tri5 ${tri_bet:.2f} + Super6 ${super_bet:.2f} 8+", r)

    # ---- VALUE SPREAD FILTER ----
    print("\n--- VALUE SPREAD FILTER ---")
    r = strat_value_spread_races(RACE_DATA, ex_bet=0.50, tri_bet=0.50)
    if r["w"] > 0:
        print_result("Value Spread Tri5 $0.50 8+", r)
    r = strat_value_spread_races(RACE_DATA, ex_bet=0.50, tri_bet=0.20)
    if r["w"] > 0:
        print_result("Value Spread Tri5 $0.20 8+", r)

    # ---- WIDE TRIFECTA ----
    print("\n--- WIDE TRIFECTA (TOP 6) ---")
    for bet in [0.10, 0.20, 0.50]:
        for min_s in [8, 9, 10]:
            r = strat_trifecta_wide_big_fields(RACE_DATA, top_n=6, bet=bet, min_starters=min_s)
            if r["plays"] > 0:
                print_result(f"Wide Tri6 ${bet:.2f} {min_s}+", r)

    print("\n" + "=" * 120)
    print("SUMMARY: Look for strategies with POSITIVE ROI (marked with ***)")
    print("=" * 120)
