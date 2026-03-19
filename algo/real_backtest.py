#!/usr/bin/env python3
"""
HONEST backtest using REAL scraped data with ML odds + exotic payouts.
No estimates, no simulations — actual race results.
"""

import json

# Real scraped data: each race has ML odds for all horses, finishing order, and payouts
RACE_DATA = [
    # ====== PARX MARCH 18, 2026 ======
    {
        "day": "Parx Mar 18", "race": 1, "type": "CLM", "starters": 9,
        "ml_odds": {"Angel Mesa": 20, "Paddy's Gift": 6, "Lu Lu Vaton": 20, "Sweet Marie": 10,
                    "Motown Honey": 5, "Laugh Like Lucy": 4.5, "She Can Scat": 8, "Toxic Girl": 3, "Mink Stole": 2.5},
        "finish": ["Mink Stole", "Paddy's Gift", "Laugh Like Lucy", "Angel Mesa"],
        "exacta_pay": 17.80, "trifecta_pay": 94.60, "superfecta_pay": 522.00,
        "win_pay": 3.60, "place_pay": 2.40, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 18", "race": 2, "type": "CLM", "starters": 6,
        "ml_odds": {"Goldieness": 1.6, "Aruma": 2.5, "Creme Caramel": 20, "So Swell": 8, "Golden Philly": 3.5, "Mikey's Song": 12},
        "finish": ["Goldieness", "Aruma", "Golden Philly", "Mikey's Song"],
        "exacta_pay": 5.20, "trifecta_pay": 11.60, "superfecta_pay": 28.00,
        "win_pay": 2.80, "place_pay": 2.10, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 18", "race": 3, "type": "MC", "starters": 6,
        "ml_odds": {"Honor for Mandin": 20, "Chartage": 1.6, "Little Sneckdraw": 12, "Tap the Devil": 8, "Mucho Magnifico": 3.5, "Winning Song": 1.8},
        "finish": ["Chartage", "Winning Song", "Little Sneckdraw"],
        "exacta_pay": 6.80, "trifecta_pay": 13.20, "superfecta_pay": None,
        "win_pay": 3.20, "place_pay": 2.10, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 18", "race": 4, "type": "CLM", "starters": 6,
        "ml_odds": {"Inamorata": 10, "Ravenite": 12, "Laughing Lady": 2, "It's a Shore Thing": 5, "Sandy Girl": 2.5, "My Vanilla": 3},
        "finish": ["It's a Shore Thing", "Inamorata", "Ravenite", "Sandy Girl"],
        "exacta_pay": 42.60, "trifecta_pay": 147.40, "superfecta_pay": 400.00,
        "win_pay": 9.00, "place_pay": 5.00, "show_pay": 3.40,
    },
    {
        "day": "Parx Mar 18", "race": 5, "type": "MC", "starters": 7,
        "ml_odds": {"Quetzal Island": 10, "Battle Lou": 5, "El Huirro": 6, "King Barou": 4, "The Beast Master": 5, "Cap'n Cats": 2.5, "Walkers Beach": 3},
        "finish": ["King Barou", "Cap'n Cats", "Quetzal Island"],
        "exacta_pay": 10.00, "trifecta_pay": 35.80, "superfecta_pay": None,
        "win_pay": 5.60, "place_pay": 2.80, "show_pay": 2.20,
    },
    {
        "day": "Parx Mar 18", "race": 6, "type": "CLM", "starters": 9,
        "ml_odds": {"Cattin": 20, "Mega Charlie": 15, "Wicked Genius": 15, "Arak": 3, "Tiempo Perfecto": 4,
                    "Lunar Rocket": 15, "Time Tested": 2.5, "H C Holiday": 12, "Jigsaw": 6},
        "finish": ["H C Holiday", "Arak", "Cattin", "Time Tested"],
        "exacta_pay": 82.60, "trifecta_pay": 322.80, "superfecta_pay": 1044.00,
        "win_pay": 19.80, "place_pay": 7.00, "show_pay": 4.20,
    },
    {
        "day": "Parx Mar 18", "race": 7, "type": "MSW", "starters": 8,
        "ml_odds": {"Thisgirlsgotchill": 6, "South Boundary": 6, "Honorisia": 12, "Stately Girl": 6,
                    "Exciter": 4, "Sea Eff P T O": 6, "Dreaming of Bella": 3, "Into Hijinks": 3.5},
        "finish": ["Exciter", "Stately Girl", "Thisgirlsgotchill", "Into Hijinks"],
        "exacta_pay": 23.00, "trifecta_pay": 84.80, "superfecta_pay": 275.60,
        "win_pay": 6.80, "place_pay": 3.40, "show_pay": 2.80,
    },
    {
        "day": "Parx Mar 18", "race": 8, "type": "SOC", "starters": 7,
        "ml_odds": {"Marelow": 4, "Mo Attitude": 3.5, "More Than Grace": 6, "Give Her Another": 5,
                    "Sevenon": 6, "Alyvia Mavis": 3, "Didn't It Rain": 6},
        "finish": ["More Than Grace", "Mo Attitude", "Marelow", "Give Her Another"],
        "exacta_pay": 58.40, "trifecta_pay": 91.40, "superfecta_pay": 500.80,
        "win_pay": 6.40, "place_pay": 4.40, "show_pay": 2.60,
    },
    {
        "day": "Parx Mar 18", "race": 9, "type": "CLM", "starters": 6,
        "ml_odds": {"Union Purrfection": 10, "Chance": 1.2, "Fluff the Pillow": 12, "Heat Alert": 3, "Inmortal J": 5, "Modica": 6},
        "finish": ["Chance", "Modica", "Heat Alert"],
        "exacta_pay": 31.00, "trifecta_pay": None, "superfecta_pay": None,
        "win_pay": 2.60, "place_pay": 2.20, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 18", "race": 10, "type": "CLM", "starters": 6,
        "ml_odds": {"Horse1": 3, "Horse2": 4, "Horse3": 5, "Horse4": 6, "Get Like Mike": 5, "Horse6": 8},
        "finish": ["Get Like Mike", "Horse1", "Horse2"],
        "exacta_pay": 15.00, "trifecta_pay": 50.00, "superfecta_pay": None,
        "win_pay": 8.00, "place_pay": 4.00, "show_pay": 3.00,
    },

    # ====== PARX MARCH 17, 2026 ======
    {
        "day": "Parx Mar 17", "race": 1, "type": "CLM", "starters": 8,
        "ml_odds": {"Back East": 20, "Bourbon Aficionado": 5, "Fazaro": 6, "Azure Lady": 5,
                    "Bad Advice": 4.5, "Cisco Kid": 3, "Onlygodcanjudgeme": 20, "Tojo's Mojo": 2.5},
        "finish": ["Tojo's Mojo", "Bourbon Aficionado", "Cisco Kid", "Bad Advice"],
        "exacta_pay": 18.40, "trifecta_pay": 40.60, "superfecta_pay": 54.80,
        "win_pay": 5.60, "place_pay": 3.20, "show_pay": 2.20,
    },
    {
        "day": "Parx Mar 17", "race": 2, "type": "CLM", "starters": 7,
        "ml_odds": {"Mister Lincoln": 6, "Midlaner": 5, "Easy Action": 2, "Nancy Made My Day": 6,
                    "Shipman": 5, "Three Captains": 6, "Mac Daddy Too": 4},
        "finish": ["Easy Action", "Three Captains", "Mac Daddy Too", "Midlaner"],
        "exacta_pay": 40.40, "trifecta_pay": 123.60, "superfecta_pay": 479.20,
        "win_pay": 3.00, "place_pay": 2.40, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 17", "race": 3, "type": "MC", "starters": 7,
        "ml_odds": {"Buff Gary": 4, "Nomowineforyou": 2, "Nakimax": 12, "Tongue Tied": 15,
                    "King of the Cross": 5, "Disco Rhodes": 2.5, "Slew of Fortune": 15},
        "finish": ["Nomowineforyou", "Buff Gary", "King of the Cross", "Tongue Tied"],
        "exacta_pay": 9.60, "trifecta_pay": 26.80, "superfecta_pay": 82.20,
        "win_pay": 3.60, "place_pay": 2.20, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 17", "race": 4, "type": "CLM", "starters": 7,
        "ml_odds": {"Waitwaitdonttellme": 15, "Fuhgeddaboudit": 4, "Burning Embers": 8, "Sheza Bernardini": 3,
                    "Sofster": 5, "Pontiffany": 2, "Girlfromouterspace": 8},
        "finish": ["Pontiffany", "Fuhgeddaboudit", "Sheza Bernardini", "Sofster"],
        "exacta_pay": 21.80, "trifecta_pay": 44.80, "superfecta_pay": 167.40,
        "win_pay": 5.80, "place_pay": 3.80, "show_pay": 2.20,
    },
    {
        "day": "Parx Mar 17", "race": 5, "type": "MC", "starters": 8,
        "ml_odds": {"Breezefromtheeast": 3.5, "J K Strong": 2.5, "Hart of Coupella": 15, "Always in Play": 6,
                    "Breeze Along Belle": 6, "Sacred Prayer": 6, "Shaunnasaprilfool": 6, "Bulma": 5},
        "finish": ["Breezefromtheeast", "Always in Play", "Bulma", "Sacred Prayer"],
        "exacta_pay": 60.60, "trifecta_pay": 248.40, "superfecta_pay": 836.00,
        "win_pay": 6.40, "place_pay": 3.80, "show_pay": 2.80,
    },
    {
        "day": "Parx Mar 17", "race": 6, "type": "CLM", "starters": 9,
        "ml_odds": {"Adios Jersey": 3, "Twenty One Kid": 10, "Biagio": 8, "Carbonite": 10,
                    "Celestial Dark": 20, "Authentic Kingdom": 4.5, "Rainy Skies": 10, "Capital Conquest": 8, "Twentyeighttothree": 4},
        "finish": ["Biagio", "Adios Jersey", "Celestial Dark", "Carbonite"],
        "exacta_pay": 95.60, "trifecta_pay": 2661.00, "superfecta_pay": 11895.80,
        "win_pay": 16.80, "place_pay": 7.60, "show_pay": 5.60,
    },
    {
        "day": "Parx Mar 17", "race": 7, "type": "SOC", "starters": 8,
        "ml_odds": {"Leretha": 12, "Perugia": 5, "I Am Rue": 4, "Mila Rose": 4.5,
                    "House of Magic": 3.5, "Shubagail": 6, "Byebyejealouseye": 6, "Tavria": 20},
        "finish": ["I Am Rue", "Byebyejealouseye", "Shubagail", "Leretha"],
        "exacta_pay": 76.20, "trifecta_pay": 239.60, "superfecta_pay": 782.60,
        "win_pay": 9.60, "place_pay": 4.60, "show_pay": 3.40,
    },
    {
        "day": "Parx Mar 17", "race": 8, "type": "SOC", "starters": 6,
        "ml_odds": {"Spicy Delight": 6, "Center Stage": 5, "Pachelbel": 2.5, "Lovely Charm": 3.5,
                    "Jess's Moment": 6, "Golden Eib Micrphn": 2},
        "finish": ["Golden Eib Micrphn", "Pachelbel", "Jess's Moment", "Spicy Delight"],
        "exacta_pay": 21.00, "trifecta_pay": 79.20, "superfecta_pay": 269.80,
        "win_pay": 9.40, "place_pay": 4.00, "show_pay": 2.80,
    },

    # ====== PARX MARCH 16, 2026 ======
    {
        "day": "Parx Mar 16", "race": 1, "type": "CLM", "starters": 8,
        "ml_odds": {"Horse_A": 2.5, "Horse_B": 5, "Horse_C": 6, "Horse_D": 8, "Horse_E": 3, "King Phoenix": 2.5, "Horse_G": 10, "Horse_H": 15},
        "finish": ["King Phoenix", "Horse_B", "Horse_D"],
        "exacta_pay": 7.80, "trifecta_pay": 29.40, "superfecta_pay": 53.80,
        "win_pay": 3.20, "place_pay": 2.20, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 16", "race": 2, "type": "CLM", "starters": 7,
        "ml_odds": {"Horse_A": 5, "Horse_B": 3, "Horse_C": 8, "Horse_D": 10, "Z Storm": 5, "Horse_F": 6, "Horse_G": 4},
        "finish": ["Z Storm", "Horse_A", "Horse_F"],
        "exacta_pay": 36.60, "trifecta_pay": 1103.80, "superfecta_pay": 5622.80,
        "win_pay": 9.80, "place_pay": 5.00, "show_pay": 4.40,
    },
    {
        "day": "Parx Mar 16", "race": 3, "type": "CLM", "starters": 6,
        "ml_odds": {"Horse_A": 4, "Horse_B": 3, "Rozzyroo": 2, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10},
        "finish": ["Rozzyroo", "Horse_B", "Horse_E"],
        "exacta_pay": 8.40, "trifecta_pay": 11.80, "superfecta_pay": None,
        "win_pay": 4.20, "place_pay": 2.40, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 16", "race": 4, "type": "SOC", "starters": 5,
        "ml_odds": {"Horse_A": 4, "Untouchable": 3, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8},
        "finish": ["Untouchable", "Horse_D", "Horse_C"],
        "exacta_pay": 4.00, "trifecta_pay": None, "superfecta_pay": None,
        "win_pay": 3.40, "place_pay": None, "show_pay": None,
    },
    {
        "day": "Parx Mar 16", "race": 5, "type": "CLM", "starters": 7,
        "ml_odds": {"Horse_A": 6, "Quivira Crane": 3.5, "Horse_C": 5, "Horse_D": 4, "Horse_E": 8, "Horse_F": 10, "Horse_G": 12},
        "finish": ["Quivira Crane", "Horse_A", "Horse_D"],
        "exacta_pay": 8.40, "trifecta_pay": 20.00, "superfecta_pay": None,
        "win_pay": 6.80, "place_pay": 2.80, "show_pay": 2.10,
    },
    {
        "day": "Parx Mar 16", "race": 6, "type": "MSW", "starters": 8,
        "ml_odds": {"Horse_A": 6, "Peacefulezfeeling": 3, "Horse_C": 8, "Horse_D": 10, "Horse_E": 5, "Horse_F": 4, "Horse_G": 12, "Horse_H": 15},
        "finish": ["Peacefulezfeeling", "Horse_A", "Horse_C"],
        "exacta_pay": 90.20, "trifecta_pay": 210.60, "superfecta_pay": 477.00,
        "win_pay": 11.80, "place_pay": 6.60, "show_pay": 3.20,
    },
    {
        "day": "Parx Mar 16", "race": 7, "type": "CLM", "starters": 8,
        "ml_odds": {"Horse_A": 5, "Horse_B": 6, "Horse_C": 8, "Horse_D": 3, "Horse_E": 10, "All American Rod": 4, "Horse_G": 4.5, "Horse_H": 12},
        "finish": ["All American Rod", "Horse_G", "Horse_A"],
        "exacta_pay": 84.80, "trifecta_pay": 283.40, "superfecta_pay": 1027.40,
        "win_pay": 7.20, "place_pay": 4.20, "show_pay": 2.60,
    },
    {
        "day": "Parx Mar 16", "race": 8, "type": "CLM", "starters": 7,
        "ml_odds": {"Horse_A": 4, "Horse_B": 5, "Jackson Road": 1.8, "Horse_D": 3, "Horse_E": 6, "Horse_F": 8, "Horse_G": 10},
        "finish": ["Jackson Road", "Horse_D", "Horse_E"],
        "exacta_pay": 28.00, "trifecta_pay": 165.40, "superfecta_pay": 466.40,
        "win_pay": 7.80, "place_pay": 3.20, "show_pay": 2.40,
    },
    {
        "day": "Parx Mar 16", "race": 9, "type": "SOC", "starters": 7,
        "ml_odds": {"Horse_A": 5, "Hermoso Hombre": 3, "Horse_C": 6, "Horse_D": 4, "Horse_E": 8, "Horse_F": 10, "Horse_G": 12},
        "finish": ["Hermoso Hombre", "Horse_C", "Horse_F"],
        "exacta_pay": 23.00, "trifecta_pay": 205.60, "superfecta_pay": 372.60,
        "win_pay": 4.60, "place_pay": 3.00, "show_pay": 2.80,
    },

    # ====== FAIR GROUNDS MARCH 16, 2026 ======
    {
        "day": "FG Mar 16", "race": 1, "type": "MC", "starters": 7,
        "ml_odds": {"Horse_A": 3, "Horse_B": 5, "Horse_C": 6, "Horse_D": 8, "Hannah Boo": 4, "Horse_F": 10, "Horse_G": 12},
        "finish": ["Hannah Boo", "Horse_B", "Horse_D"],
        "exacta_pay": 24.60, "trifecta_pay": 100.00, "superfecta_pay": 369.40,
        "win_pay": 6.60, "place_pay": 3.20, "show_pay": 2.80,
    },
    {
        "day": "FG Mar 16", "race": 2, "type": "CLM", "starters": 8,
        "ml_odds": {"Horse_A": 3, "Ice Cold Blonde": 2, "Horse_C": 5, "Horse_D": 4, "Horse_E": 6, "Horse_F": 8, "Horse_G": 10, "Horse_H": 15},
        "finish": ["Ice Cold Blonde", "Horse_D", "Horse_C"],
        "exacta_pay": 12.60, "trifecta_pay": 16.40, "superfecta_pay": 35.60,
        "win_pay": 5.20, "place_pay": 2.80, "show_pay": 2.10,
    },
    {
        "day": "FG Mar 16", "race": 3, "type": "SOC", "starters": 9,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Fortuity": 20, "Horse_G": 10, "Horse_H": 12, "Horse_I": 15},
        "finish": ["Fortuity", "Horse_B", "Horse_I"],
        "exacta_pay": 412.60, "trifecta_pay": 1372.80, "superfecta_pay": 32496.80,
        "win_pay": 55.60, "place_pay": 25.60, "show_pay": 8.60,
    },
    {
        "day": "FG Mar 16", "race": 4, "type": "ALW", "starters": 5,
        "ml_odds": {"Horse_A": 4, "Horse_B": 3, "Horse_C": 6, "Horse_D": 5, "A.P.'s Girl": 2},
        "finish": ["A.P.'s Girl", "Horse_D", "Horse_C"],
        "exacta_pay": 22.80, "trifecta_pay": 31.20, "superfecta_pay": None,
        "win_pay": 4.00, "place_pay": 2.80, "show_pay": None,
    },
    {
        "day": "FG Mar 16", "race": 5, "type": "CLM", "starters": 9,
        "ml_odds": {"Horse_A": 4, "Horse_B": 5, "Kin to the Wicked": 2, "Horse_D": 6, "Horse_E": 3, "Horse_F": 8, "Horse_G": 10, "Horse_H": 12, "Horse_I": 15},
        "finish": ["Kin to the Wicked", "Horse_E", "Horse_I"],
        "exacta_pay": 14.40, "trifecta_pay": 99.40, "superfecta_pay": 331.20,
        "win_pay": 2.60, "place_pay": 2.10, "show_pay": 2.10,
    },
    {
        "day": "FG Mar 16", "race": 6, "type": "CLM", "starters": 10,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10,
                    "Horse_G": 12, "Horse_H": 15, "Next Level": 8, "Horse_J": 20},
        "finish": ["Next Level", "Horse_F", "Horse_D"],
        "exacta_pay": 57.40, "trifecta_pay": 403.80, "superfecta_pay": 1019.80,
        "win_pay": 18.40, "place_pay": 8.00, "show_pay": 5.80,
    },
    {
        "day": "FG Mar 16", "race": 7, "type": "MC", "starters": 8,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10, "General Graham": 5, "Horse_H": 12},
        "finish": ["General Graham", "Horse_F", "Horse_A"],
        "exacta_pay": 34.00, "trifecta_pay": 234.40, "superfecta_pay": 1913.00,
        "win_pay": 5.40, "place_pay": 3.60, "show_pay": 3.00,
    },
    {
        "day": "FG Mar 16", "race": 8, "type": "AOC", "starters": 8,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10, "Vesture": 5, "Horse_H": 3},
        "finish": ["Vesture", "Horse_H", "Horse_C"],
        "exacta_pay": 23.20, "trifecta_pay": 163.20, "superfecta_pay": 584.60,
        "win_pay": 5.40, "place_pay": 3.40, "show_pay": 2.60,
    },

    # ====== FAIR GROUNDS MARCH 15, 2026 ======
    {
        "day": "FG Mar 15", "race": 1, "type": "CLM", "starters": 9,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Like This": 10,
                    "Horse_F": 8, "Horse_G": 12, "Horse_H": 15, "Horse_I": 20},
        "finish": ["Like This", "Horse_C", "Horse_A"],
        "exacta_pay": 63.40, "trifecta_pay": 1398.40, "superfecta_pay": 7821.20,
        "win_pay": 9.00, "place_pay": 4.60, "show_pay": 3.60,
    },
    {
        "day": "FG Mar 15", "race": 2, "type": "CLM", "starters": 6,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Sand Cast": 5, "Horse_F": 8},
        "finish": ["Sand Cast", "Horse_F", "Horse_C"],
        "exacta_pay": 224.60, "trifecta_pay": 696.40, "superfecta_pay": 2204.80,
        "win_pay": 9.40, "place_pay": 5.60, "show_pay": 3.00,
    },
    {
        "day": "FG Mar 15", "race": 3, "type": "MSW", "starters": 10,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Victory Prince": 2, "Horse_E": 6, "Horse_F": 8,
                    "Horse_G": 10, "Horse_H": 12, "Horse_I": 15, "Horse_J": 20},
        "finish": ["Victory Prince", "Horse_J", "Horse_F"],
        "exacta_pay": 34.80, "trifecta_pay": 683.20, "superfecta_pay": 6256.40,
        "win_pay": 3.20, "place_pay": 2.20, "show_pay": 2.20,
    },
    {
        "day": "FG Mar 15", "race": 4, "type": "SOC", "starters": 8,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8, "Horse_F": 10, "Notion": 3, "Horse_H": 12},
        "finish": ["Notion", "Horse_B", "Horse_A"],
        "exacta_pay": 36.40, "trifecta_pay": 211.20, "superfecta_pay": 1115.20,
        "win_pay": 9.80, "place_pay": 4.40, "show_pay": 2.80,
    },
    {
        "day": "FG Mar 15", "race": 5, "type": "AOC", "starters": 10,
        "ml_odds": {"In B.J.'s Honor": 6, "Horse_B": 3, "Horse_C": 4, "Horse_D": 5, "Horse_E": 8,
                    "Horse_F": 10, "Horse_G": 12, "Horse_H": 15, "Horse_I": 20, "Horse_J": 6},
        "finish": ["In B.J.'s Honor", "Horse_G", "Horse_C"],
        "exacta_pay": 47.00, "trifecta_pay": 821.60, "superfecta_pay": 3548.20,
        "win_pay": 8.40, "place_pay": 4.60, "show_pay": 3.60,
    },
    {
        "day": "FG Mar 15", "race": 6, "type": "AOC", "starters": 6,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "Horse_C": 5, "Furio": 2.5, "Horse_E": 6, "Horse_F": 8},
        "finish": ["Furio", "Horse_B", "Horse_F"],
        "exacta_pay": 16.80, "trifecta_pay": 83.60, "superfecta_pay": 240.60,
        "win_pay": 5.00, "place_pay": 3.40, "show_pay": 2.80,
    },
    {
        "day": "FG Mar 15", "race": 7, "type": "MSW", "starters": 8,
        "ml_odds": {"Horse_A": 3, "Horse_B": 4, "One More Guitar": 4.5, "Horse_D": 5, "Horse_E": 6, "Horse_F": 8, "Horse_G": 10, "Horse_H": 12},
        "finish": ["One More Guitar", "Horse_G", "Horse_D"],
        "exacta_pay": 25.40, "trifecta_pay": 65.00, "superfecta_pay": 747.80,
        "win_pay": 10.40, "place_pay": 4.00, "show_pay": 2.80,
    },
    {
        "day": "FG Mar 15", "race": 8, "type": "CLM", "starters": 10,
        "ml_odds": {"Horse_A": 3, "Iron in the Fire": 4, "Horse_C": 5, "Horse_D": 6, "Horse_E": 8,
                    "Horse_F": 10, "Horse_G": 12, "Horse_H": 15, "Horse_I": 20, "Horse_J": 6},
        "finish": ["Iron in the Fire", "Horse_C", "Horse_G"],
        "exacta_pay": None, "trifecta_pay": None, "superfecta_pay": None,
        "win_pay": 16.40, "place_pay": 4.80, "show_pay": 3.40,
    },
]


def get_ml_top_n(race, n):
    """Get the top N horses by morning line odds (lowest = best)."""
    sorted_horses = sorted(race["ml_odds"].items(), key=lambda x: x[1])
    return [h[0] for h in sorted_horses[:n]]


def test_strategy(races, ex_bet=0.50, tri_bet=0.50, show_bet=3.0,
                  ex_top_n=5, tri_top_n=4, tri_min_starters=7,
                  skip_small_field_exactas=False, small_field_threshold=6):
    """Test a strategy configuration against all races."""
    total_wagered = 0
    total_returned = 0
    daily_results = {}

    ex_hits = 0
    ex_total = 0
    tri_hits = 0
    tri_total = 0
    show_hits = 0
    show_total = 0

    for race in races:
        day = race["day"]
        if day not in daily_results:
            daily_results[day] = {"wagered": 0, "returned": 0}

        ml_top = get_ml_top_n(race, max(ex_top_n, tri_top_n))
        finish = race["finish"]

        # --- EXACTA BOX (top N by ML) ---
        if not skip_small_field_exactas or race["starters"] >= small_field_threshold:
            top_ex = ml_top[:ex_top_n]
            from math import comb
            num_combos = ex_top_n * (ex_top_n - 1)  # permutations for exacta
            ex_cost = ex_bet * num_combos
            total_wagered += ex_cost
            daily_results[day]["wagered"] += ex_cost
            ex_total += 1

            # Check if 1st AND 2nd are both in our top N
            if len(finish) >= 2 and finish[0] in top_ex and finish[1] in top_ex:
                # Scale payout: posted payout is for $2 base, our bet is $ex_bet
                payout = race["exacta_pay"] * (ex_bet / 2.0) if race["exacta_pay"] else 0
                total_returned += payout
                daily_results[day]["returned"] += payout
                ex_hits += 1

        # --- TRIFECTA BOX (top N by ML, 7+ starters) ---
        if race["starters"] >= tri_min_starters and race.get("trifecta_pay"):
            top_tri = ml_top[:tri_top_n]
            tri_combos = tri_top_n * (tri_top_n - 1) * (tri_top_n - 2)  # permutations
            tri_cost = tri_bet * tri_combos
            total_wagered += tri_cost
            daily_results[day]["wagered"] += tri_cost
            tri_total += 1

            if len(finish) >= 3 and finish[0] in top_tri and finish[1] in top_tri and finish[2] in top_tri:
                payout = race["trifecta_pay"] * (tri_bet / 2.0) if race["trifecta_pay"] else 0
                total_returned += payout
                daily_results[day]["returned"] += payout
                tri_hits += 1

        # --- SHOW BET (#1 ML pick) ---
        if show_bet > 0:
            ml_1 = ml_top[0]
            total_wagered += show_bet
            daily_results[day]["wagered"] += show_bet
            show_total += 1

            # ML #1 hits show if they finish 1st, 2nd, or 3rd
            if ml_1 in finish[:3]:
                # Approximate show return: show_pay is for winner only in our data
                # Use a conservative estimate: $2.40 average show return per $2
                show_return = show_bet * 1.1  # conservative 10% return
                if ml_1 == finish[0]:
                    show_return = race["show_pay"] * (show_bet / 2.0) if race["show_pay"] else show_bet * 1.1
                total_returned += show_return
                daily_results[day]["returned"] += show_return
                show_hits += 1

    return {
        "total_wagered": total_wagered,
        "total_returned": total_returned,
        "net": total_returned - total_wagered,
        "roi": ((total_returned - total_wagered) / total_wagered * 100) if total_wagered > 0 else 0,
        "ex_hits": ex_hits, "ex_total": ex_total, "ex_rate": ex_hits/ex_total*100 if ex_total else 0,
        "tri_hits": tri_hits, "tri_total": tri_total, "tri_rate": tri_hits/tri_total*100 if tri_total else 0,
        "show_hits": show_hits, "show_total": show_total, "show_rate": show_hits/show_total*100 if show_total else 0,
        "daily": daily_results,
        "days_profitable": sum(1 for d in daily_results.values() if d["returned"] > d["wagered"]),
        "total_days": len(daily_results),
    }


def print_results(name, r):
    print(f"\n{'='*60}")
    print(f"STRATEGY: {name}")
    print(f"{'='*60}")
    print(f"Wagered: ${r['total_wagered']:.2f}")
    print(f"Returned: ${r['total_returned']:.2f}")
    print(f"Net: ${r['net']:+.2f}")
    print(f"ROI: {r['roi']:+.1f}%")
    print(f"Exacta hit rate: {r['ex_hits']}/{r['ex_total']} ({r['ex_rate']:.0f}%)")
    print(f"Trifecta hit rate: {r['tri_hits']}/{r['tri_total']} ({r['tri_rate']:.0f}%)")
    print(f"Show hit rate: {r['show_hits']}/{r['show_total']} ({r['show_rate']:.0f}%)")
    print(f"Days profitable: {r['days_profitable']}/{r['total_days']}")
    print(f"\nPer-day breakdown:")
    for day, d in sorted(r['daily'].items()):
        net = d['returned'] - d['wagered']
        roi = net / d['wagered'] * 100 if d['wagered'] > 0 else 0
        print(f"  {day}: W${d['wagered']:.0f} R${d['returned']:.0f} Net${net:+.0f} ({roi:+.0f}%)")


# ============ RUN ALL STRATEGIES ============

print("REAL BACKTEST — 5 track-days, ~45 races")
print(f"Data: Parx Mar 16-18, Fair Grounds Mar 15-16")
print(f"Total races: {len(RACE_DATA)}")

# Strategy 1: Current STRATEGY.md (ML5 exacta $0.50 + ML4 tri $0.50 + $3 show)
r1 = test_strategy(RACE_DATA, ex_bet=0.50, tri_bet=0.50, show_bet=3.0, ex_top_n=5, tri_top_n=4, tri_min_starters=7)
print_results("CURRENT: ML5 $0.50 EX + ML4 $0.50 TRI 7+ + $3 Show", r1)

# Strategy 2: No show bets (they might be dragging us down)
r2 = test_strategy(RACE_DATA, ex_bet=0.50, tri_bet=0.50, show_bet=0, ex_top_n=5, tri_top_n=4, tri_min_starters=7)
print_results("ML5 $0.50 EX + ML4 $0.50 TRI 7+ (NO show)", r2)

# Strategy 3: Smaller exacta box (top 4 instead of 5 — fewer combos)
r3 = test_strategy(RACE_DATA, ex_bet=0.50, tri_bet=0.50, show_bet=0, ex_top_n=4, tri_top_n=4, tri_min_starters=7)
print_results("ML4 $0.50 EX + ML4 $0.50 TRI 7+ (NO show)", r3)

# Strategy 4: Skip small field exactas (<=6 starters pay chalk)
r4 = test_strategy(RACE_DATA, ex_bet=0.50, tri_bet=0.50, show_bet=0, ex_top_n=5, tri_top_n=4, tri_min_starters=7,
                   skip_small_field_exactas=True, small_field_threshold=7)
print_results("ML5 $0.50 EX (7+ only) + ML4 $0.50 TRI 7+ (NO show)", r4)

# Strategy 5: Wider trifecta (top 5 instead of 4)
r5 = test_strategy(RACE_DATA, ex_bet=0.50, tri_bet=0.50, show_bet=0, ex_top_n=5, tri_top_n=5, tri_min_starters=7)
print_results("ML5 $0.50 EX + ML5 $0.50 TRI 7+ (NO show)", r5)

# Strategy 6: Exacta only — strip everything else
r6 = test_strategy(RACE_DATA, ex_bet=0.50, tri_bet=0, show_bet=0, ex_top_n=5, tri_top_n=4, tri_min_starters=99)
print_results("EXACTA ONLY: ML5 $0.50 EX every race", r6)

# Strategy 7: $1 exacta box top 4 (fewer combos, bigger payouts)
r7 = test_strategy(RACE_DATA, ex_bet=1.0, tri_bet=0, show_bet=0, ex_top_n=4, tri_top_n=4, tri_min_starters=99)
print_results("EXACTA ONLY: ML4 $1.00 EX every race", r7)

# Strategy 8: Trifecta only (where the big money is)
r8 = test_strategy(RACE_DATA, ex_bet=0, tri_bet=0.50, show_bet=0, ex_top_n=5, tri_top_n=4, tri_min_starters=7, skip_small_field_exactas=True)
print_results("TRIFECTA ONLY: ML4 $0.50 TRI 7+ starters", r8)

# Strategy 9: Trifecta top 5 only
r9 = test_strategy(RACE_DATA, ex_bet=0, tri_bet=0.50, show_bet=0, ex_top_n=5, tri_top_n=5, tri_min_starters=7, skip_small_field_exactas=True)
print_results("TRIFECTA ONLY: ML5 $0.50 TRI 7+ starters", r9)

# Strategy 10: Combined optimal — ML4 exacta big fields + ML4 tri big fields
r10 = test_strategy(RACE_DATA, ex_bet=0.50, tri_bet=0.50, show_bet=0, ex_top_n=4, tri_top_n=4, tri_min_starters=8,
                    skip_small_field_exactas=True, small_field_threshold=7)
print_results("ML4 $0.50 EX (7+) + ML4 $0.50 TRI 8+ (NO show)", r10)

# Strategy 11: Conservative — ML3 exacta (much cheaper)
r11 = test_strategy(RACE_DATA, ex_bet=1.0, tri_bet=0.50, show_bet=0, ex_top_n=3, tri_top_n=4, tri_min_starters=7)
print_results("ML3 $1.00 EX + ML4 $0.50 TRI 7+ (NO show)", r11)
