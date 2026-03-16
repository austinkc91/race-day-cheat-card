#!/usr/bin/env python3
"""
Multi-Track, Multi-Day Value Analysis
March 16-21, 2026

Tracks: Fair Grounds, Parx Racing, Oaklawn Park
Strategy: Value plays at 4/1+ with expert support = BIG WINNERS
"""

from value_handicapper import *
import json
from datetime import datetime


def build_fair_grounds_march16():
    """Fair Grounds - Monday, March 16, 2026 - 9 races"""
    races = []

    # Sources compiled: SFTB, Racing Dudes, HRN, FanDuel (limited), Ultimate Capper
    # Note: FanDuel had no races loaded yet. AI Horse Picks only had March 15 data.

    # R1 - Maiden Claiming | 5.5F Dirt | $14,000
    r1 = Race(1, "Fair Grounds", "2026-03-16", "Maiden Claiming", "5.5F", "Dirt", 14000, "12:45 PM")
    r1.horses = [
        Horse("Flora Bound", 1, "5/1", "Micah Meeks", "David Terre"),
        Horse("Goodmorning Gracie", 2, "9/2", "Mitchell Murrill", "Joseph M. Foster", sftb_rank=1.8),
        Horse("Stormy Lou", 3, "6/1", "Juan P. Vargas", "Gerard Perron"),
        Horse("Metallic Maid", 4, "9/2", "Marcelino Pedroza Jr.", "Carrol Castille", sftb_rank=1.8),
        Horse("Hannah Boo", 5, "7/2", "Sofia Vives", "Sam B. David Jr.", sftb_rank=1.0, racing_dudes_pick=True),
        Horse("Go North Boss", 6, "8/1", "Harry Hernandez", "Jonathan Wong"),
        Horse("Stella Guitar", 7, "4/1", "Axel Concepcion", "W. Bret Calhoun", sftb_rank=1.4, hrn_pick=True),
        Horse("Miss Maddie", 8, "12/1", "Jose Riquelme", "Emile Schwandt"),
    ]
    races.append(r1)

    # R2 - Claiming 3yo Fillies | 6F Dirt | $18,000
    r2 = Race(2, "Fair Grounds", "2026-03-16", "Claiming", "6F", "Dirt", 18000, "1:15 PM")
    r2.horses = [
        Horse("Authentic Angel", 1, "7/2", "James Graham", "J. Keith Desormeaux", sftb_rank=1.5),
        Horse("Ice Cold Blonde", 2, "7/2", "Sofia Vives", "Whitney J. Zeringue Jr.", sftb_rank=1.5),
        Horse("Hold the Drama", 3, "4/1", "Harry Hernandez", "Jonathan Wong"),
        Horse("Kitten Gloves", 4, "4/1", "Jose L. Ortiz", "Randy Degeyter Jr.", racing_dudes_pick=True, hrn_pick=True),
        Horse("Undisputable", 5, "3/1", "Colby J. Hernandez", "Dallas Stewart", sftb_rank=1.0),
        Horse("Great Owl", 6, "8/1", "Hunter Rea", "Larry Rivelli"),
    ]
    races.append(r2)

    # R3 - SOC | 1M Turf | $19,000
    r3 = Race(3, "Fair Grounds", "2026-03-16", "Starter Optional Claiming", "1M", "Turf", 19000, "1:45 PM")
    r3.horses = [
        Horse("Even the Wind", 1, "12/1", "Marcelino Pedroza Jr.", "Chris M. Block"),
        Horse("Bigfoot Sighting", 2, "20/1", "Jose Luis Rodriguez", "Cesar Govea"),
        Horse("Moogie Son", 3, "20/1", "Sofia Vives", "Larry Rivelli"),
        Horse("Foxtrot Harry", 4, "6/1", "Isaac Castillo", "Jonathan Wong", hrn_pick=True),
        Horse("Not Falling Back", 5, "12/1", "Jareth Loveberry", "Chris M. Block", racing_dudes_pick=True),
        Horse("Fortuity", 6, "10/1", "Jansen Melancon", "Randy Degeyter Jr."),
        Horse("Red Road", 7, "7/2", "Brian J. Hernandez Jr.", "Sturges J. Ducoing", sftb_rank=1.8),
        Horse("Twoko Bay", 8, "20/1", "Erica M. Murray", "Gary M. Scherer"),
        Horse("Boitano", 9, "2/1", "Axel Concepcion", "Jose M. Camejo", sftb_rank=1.0),
        Horse("Mister Muldoon", 10, "7/2", "James Graham", "Hugh H. Robertson", sftb_rank=1.8),
    ]
    races.append(r3)

    # R4 - Allowance 3yo Fillies | 1-1/16M Dirt | $55,000
    r4 = Race(4, "Fair Grounds", "2026-03-16", "Allowance", "1-1/16M", "Dirt", 55000, "2:15 PM")
    r4.horses = [
        Horse("Majestical", 1, "2/1", "Jose L. Ortiz", "Peter Eurton", racing_dudes_pick=True, sftb_rank=1.0),
        Horse("Huck's Agenda", 2, "5/2", "Brian J. Hernandez Jr.", "Kenneth G. McPeek"),
        Horse("Sticker Shocked", 3, "3/1", "Colby J. Hernandez", "Kenneth G. McPeek"),
        Horse("Zaffa", 4, "6/1", "Declan Cannon", "Brendan P. Walsh"),
        Horse("A. P.'s Girl", 5, "3/1", "Ben Curtis", "Peter Eurton"),
    ]
    races.append(r4)

    # R5 - Claiming F&M | 6F Dirt | $20,000
    r5 = Race(5, "Fair Grounds", "2026-03-16", "Claiming", "6F", "Dirt", 20000, "2:45 PM")
    r5.horses = [
        Horse("Charge the Deal", 1, "15/1", "Isaac Castillo", "Juan A. Larrosa"),
        Horse("Dose of Reality", 2, "6/1", "Hunter Rea", "Carl J. Woodley"),
        Horse("Kin to the Wicked", 3, "4/5", "Axel Concepcion", "W. Bret Calhoun", sftb_rank=1.0, racing_dudes_pick=True),
        Horse("La Maxima", 4, "9/2", "Jose L. Ortiz", "Alexis Claire"),
        Horse("Blissit", 5, "10/1", "Mitchell Murrill", "Joseph M. Foster"),
        Horse("John's June", 6, "20/1", "Emanuel Nieves", "Samuel Breaux"),
        Horse("Miss Makeithappen", 7, "12/1", "Juan P. Vargas", "Ricky Demouchet"),
        Horse("Platinumus Maximus", 8, "12/1", "Marcelino Pedroza Jr.", "Carrol Castille"),
        Horse("Little Em", 9, "12/1", "Sofia Vives", "Sam B. David Jr."),
    ]
    races.append(r5)

    # R6 - Claiming | 1-1/16M Turf | $28,000
    r6 = Race(6, "Fair Grounds", "2026-03-16", "Claiming", "1-1/16M", "Turf", 28000, "3:15 PM")
    r6.horses = [
        Horse("Flamingproposition", 1, "12/1", "Harry Hernandez", "Jonathan Wong"),
        Horse("Enlighten", 2, "5/1", "Micah Meeks", "Keith A. Austin", racing_dudes_pick=True),
        Horse("Another Mystery", 3, "4/1", "Jareth Loveberry", "Chris M. Block"),
        Horse("Bold Discovery", 4, "12/1", "Emanuel Nieves", "Rob Atras"),
        Horse("Polar Bear Plunge", 5, "9/2", "Axel Concepcion", "Mertkan Kantarmaci"),
        Horse("Frosty Blue", 6, "6/1", "Marcelino Pedroza Jr.", "Allen Landry"),
        Horse("Summer in Adriane", 7, "9/2", "Ben Curtis", "Michael J. Maker"),
        Horse("Ever Dangerous", 8, "5/1", "Isaac Castillo", "Robertino Diodoro"),
        Horse("Next Level", 9, "8/1", "James Graham", "J. Keith Desormeaux"),
    ]
    races.append(r6)

    # R7 - Maiden OC 3yo | 6F Dirt | $30,000
    r7 = Race(7, "Fair Grounds", "2026-03-16", "Maiden Claiming", "6F", "Dirt", 30000, "3:45 PM")
    r7.horses = [
        Horse("Kalatua", 1, "8/1", "Ben Curtis", "Hugh H. Robertson"),
        Horse("Hutchinson", 2, "12/1", "James Graham", "J. Keith Desormeaux"),
        Horse("Pampered Prince", 3, "8/1", "Jareth Loveberry", "Albert M. Stall Jr."),
        Horse("La Norme de Jour", 4, "8/1", "Axel Concepcion", "W. Bret Calhoun"),
        Horse("Apollo Eleven", 5, "10/1", "Isaac Castillo", "Norm W. Casse"),
        Horse("Editor", 6, "4/1", "Marcelino Pedroza Jr.", "Joe Sharp"),
        Horse("General Graham", 7, "3/1", "Jose L. Ortiz", "Eddie Kenneally", racing_dudes_pick=True),
        Horse("Kingofsomewherehot", 8, "9/2", "Brian J. Hernandez Jr.", "Kenneth G. McPeek"),
        Horse("Candy Dreamin", 9, "10/1", "Juan P. Vargas", "Juan A. Larrosa"),
    ]
    races.append(r7)

    # R8 - AOC | 5.5F Turf | $56,000
    r8 = Race(8, "Fair Grounds", "2026-03-16", "Allowance Optional Claiming", "5.5F", "Turf", 56000, "4:15 PM")
    r8.horses = [
        Horse("Pineland", 1, "9/2", "Declan Cannon", "Lindsay Schultz", racing_dudes_pick=True),
        Horse("Mister Mmmmm", 2, "4/1", "Jose L. Ortiz", "Joe Sharp"),
        Horse("That's Right", 3, "5/1", "Ben Curtis", "Joe Sharp"),
        Horse("Rock N Roll Bolt", 4, "8/1", "Axel Concepcion", "Jose M. Camejo"),
        Horse("Bridle a Butterfly", 5, "8/1", "Sofia Vives", "Albert M. Stall Jr."),
        Horse("Fit to Fly", 6, "6/1", "Isaac Castillo", "Aubrie Suarez"),
        Horse("Vesture", 7, "7/2", "Brian J. Hernandez Jr.", "W. Bret Calhoun"),
        Horse("Amoudi Bay", 8, "6/1", "James Graham", "Lindsay Schultz"),
    ]
    races.append(r8)

    # R9 - Claiming F&M | 1M 70Y Dirt | $15,000
    r9 = Race(9, "Fair Grounds", "2026-03-16", "Claiming", "1M 70Y", "Dirt", 15000, "4:45 PM")
    r9.horses = [
        Horse("Sweet Alexis", 1, "3/1", "Juan P. Vargas", "Keith G. Bourgeois", racing_dudes_pick=True),
        Horse("Agami", 2, "8/1", "Devin H. Magnon", "Roland Patt Jr."),
        Horse("Anita's Vision", 3, "8/1", "Emanuel Nieves", "Sherman Savoie"),
        Horse("Molto Vino", 4, "6/1", "Hunter Rea", "Andy L. Rogers"),
        Horse("Visionista", 5, "6/1", "Mitchell Murrill", "Eduardo Rodriguez"),
        Horse("Pat Hand Girl", 6, "20/1", "Jose Riquelme", "Kenneth L. Hargrave"),
        Horse("Strawberry Sundae", 7, "7/2", "Isaac Castillo", "Shane Wilson"),
        Horse("Averi Ever After", 8, "20/1", "Jamison Mudd", "Steven Duke"),
        Horse("Apriority Catch", 9, "5/1", "Harry Hernandez", "Jonathan Wong"),
    ]
    races.append(r9)

    return races


def build_parx_march16():
    """Parx Racing - Monday, March 16, 2026 - 10 races"""
    races = []

    # R1 - $7,500 Claiming | 5.5F Dirt | $21,000
    r1 = Race(1, "Parx", "2026-03-16", "Claiming", "5.5F", "Dirt", 21000, "12:40 PM")
    r1.horses = [
        Horse("Sittin Chilly", 1, "10/1", "Angel Castillo", "Ronald J. Dandy", sftb_rank=4.6),
        Horse("Battle Anthem", 2, "9/2", "Luis M. Ocasio", "Daniel Velazquez", sftb_rank=2.0),
        Horse("Carcharoth", 3, "7/2", "Adam Bowman", "Josue Arce", sftb_rank=1.5, hrn_pick=False),
        Horse("Taporical", 4, "15/1", "Kendry Rivera", "Ramon F. Martin", sftb_rank=7.0),
        Horse("Chase a Dream", 5, "3/1", "Dexter Haddock", "Miguel Penaloza", sftb_rank=1.2),
        Horse("King Phoenix", 6, "5/2", "Ruben Silvera", "Richard E. Dutrow Jr.", sftb_rank=1.0, hrn_pick=True),
        Horse("Kerner", 7, "10/1", "Jean Aguilar", "Tony Perez Flores", sftb_rank=4.6),
    ]
    races.append(r1)

    # R2 - $12,500 Claiming | 6F Dirt | $23,000
    r2 = Race(2, "Parx", "2026-03-16", "Claiming", "6F", "Dirt", 23000, "1:07 PM")
    r2.horses = [
        Horse("Drake Drive", 1, "6/1", "Andrew Wolfsont", "Louis C. Linder Jr.", sftb_rank=2.3),
        Horse("Airman Trevor", 2, "12/1", "Angel Castillo", "Trevor Gallimore", sftb_rank=4.3),
        Horse("Week's Strong", 3, "3/1", "Frankie Pennington", "J. Tyler Servis", sftb_rank=1.3),
        Horse("Munyhungry", 4, "2/1", "Andy Hernandez", "Jacinto Solis", sftb_rank=1.0, hrn_pick=True),
        Horse("Z Storm Is Coming", 5, "5/1", "Luis M. Ocasio", "Miguel A. Rodriguez", sftb_rank=2.0),
        Horse("Fastidious", 6, "20/1", "Julio Correa", "Jose M. Santaella-Calderon", sftb_rank=7.0),
        Horse("Pastero", 7, "4/1", "Dexter Haddock", "Scott A. Lake", sftb_rank=1.7),
    ]
    races.append(r2)

    # R3 - $12,500 Claiming F&M | 6.5F Dirt | $23,000
    r3 = Race(3, "Parx", "2026-03-16", "Claiming", "6.5F", "Dirt", 23000, "1:34 PM")
    r3.horses = [
        Horse("Candothis", 1, "9/2", "Mychel J. Sanchez", "Scott A. Lake"),
        Horse("Nezy's Girl", 2, "4/1", "Kendry Rivera", "Clarence B. King"),
        Horse("Rozzyroo", 3, "2/1", "Julio A. Hernandez", "Andrew L. Simoff", hrn_pick=True),
        Horse("Classic Mystery", 4, "5/1", "Dexter Haddock", "Jacinto Solis"),
        Horse("Joyful Joyce", 5, "10/1", "Francisco Martinez", "Howard R. Brown Jr."),
        Horse("Breezethrutime", 6, "5/2", "Andy Hernandez", "Melecio Saldana Guerrero"),
    ]
    races.append(r3)

    # R4 - SOC F&M | 1M 70Y Dirt | $25,000
    r4 = Race(4, "Parx", "2026-03-16", "Starter Optional Claiming", "1M 70Y", "Dirt", 25000, "2:01 PM")
    r4.horses = [
        Horse("Cynthia Gail", 1, "4/1", "Luis M. Ocasio", "Michael V. Pino"),
        Horse("Untouchable", 2, "3/1", "Mychel J. Sanchez", "Michael V. Pino"),
        Horse("J J's Honor", 3, "20/1", "Adam Bowman", "Jose M. Santaella-Calderon"),
        Horse("Judy's Flyer", 4, "6/5", "Francisco Martinez", "Scott A. Lake"),
        Horse("Keystormrising", 5, "15/1", "Joezer Rangel", "Alan Bedard"),
        Horse("People Get Ready", 6, "7/2", "Andy Hernandez", "Jacinto Solis"),
    ]
    races.append(r4)

    # R5 - $12,500 Claiming F&M | 7F Dirt | $23,000
    r5 = Race(5, "Parx", "2026-03-16", "Claiming", "7F", "Dirt", 23000, "2:28 PM")
    r5.horses = [
        Horse("Melody's Kiss", 1, "6/1", "Francisco Martinez", "James E. Nicholson Jr."),
        Horse("Quivira Crane", 2, "7/2", "Silvestre Gonzalez", "Bobbi Anne Hawthorne"),
        Horse("K D Kakes", 3, "20/1", "Adam Bowman", "Jose M. Santaella-Calderon"),
        Horse("West Side Diva", 4, "5/2", "Angel Castillo", "Jose G. Gonzalez-Milian"),
        Horse("Zeena Swift", 5, "6/5", "Eliseo Ruiz", "Louis C. Linder Jr."),
        Horse("Shines Madelin", 6, "20/1", "Joezer Rangel", "Jose M. Santaella-Calderon"),
    ]
    races.append(r5)

    # R6 - MSW F&M | 6F Dirt | $40,000
    r6 = Race(6, "Parx", "2026-03-16", "Maiden Special Weight", "6F", "Dirt", 40000, "2:55 PM")
    r6.horses = [
        Horse("Bidibidibombom", 1, "5/1", "Angel R. Rodriguez", "Edward T. Allard"),
        Horse("Peacefulezfeeling", 2, "3/1", "Kendry Rivera", "Kathleen A. Demasi"),
        Horse("Xmas in Cairo", 3, "6/1", "Andrew Wolfsont", "Bernard G. Dunham"),
        Horse("J C's Lovin' Life", 4, "2/1", "Abner Adorno", "Robert E. Reid Jr."),
        Horse("Likeastraightshot", 5, "6/1", "David Cora", "T. Bernard Houghton"),
        Horse("Elegant Lass", 6, "4/1", "Andy Hernandez", "Michael M. Moore"),
    ]
    races.append(r6)

    # R7 - $40,000 Claiming | 1M 70Y Dirt | $30,000
    r7 = Race(7, "Parx", "2026-03-16", "Claiming", "1M 70Y", "Dirt", 30000, "3:22 PM")
    r7.horses = [
        Horse("Mr Flowers", 1, "5/2", "Mychel J. Sanchez", "Jamie Ness"),
        Horse("Iron Sharpens Iron", 2, "7/2", "Frankie Pennington", "Jacinto Solis"),
        Horse("Chain Lightning", 3, "8/1", "Luis M. Ocasio", "Harold Wyner"),
        Horse("Dreambuilder", 4, "3/1", "Abner Adorno", "Guadalupe Preciado"),
        Horse("Smile Maker", 5, "6/1", "Dexter Haddock", "Guadalupe Preciado"),
        Horse("All American Rod", 6, "4/1", "Ruben Silvera", "Jamie Ness"),
        Horse("My Imagination", 7, "15/1", "Adam Bowman", "Alan Bedard"),
    ]
    races.append(r7)

    # R8 - $16,000 Claiming | 6.5F Dirt | $26,000
    r8 = Race(8, "Parx", "2026-03-16", "Claiming", "6.5F", "Dirt", 26000, "3:49 PM")
    r8.horses = [
        Horse("One Improbable", 1, "6/1", "Yan Rodriguez", "Miguel A. Rodriguez"),
        Horse("Amore d'Oro", 2, "5/1", "Eliseo Ruiz", "Timothy J. Shaw"),
        Horse("Jackson Road", 3, "9/5", "Jorge A. Vargas Jr.", "Ernesto Padilla-Preciado"),
        Horse("Ortho Star", 4, "5/2", "Mychel J. Sanchez", "Michael V. Pino"),
        Horse("Whiskeyromeosierra", 5, "8/1", "Kendry Rivera", "Edward J. Coletti Jr."),
        Horse("Au Some Warrior", 6, "6/1", "Andy Hernandez", "Susan L. Crowell"),
    ]
    races.append(r8)

    # R9 - SOC | 1M 70Y Dirt | $30,000
    r9 = Race(9, "Parx", "2026-03-16", "Starter Optional Claiming", "1M 70Y", "Dirt", 30000, "4:16 PM")
    r9.horses = [
        Horse("Dreaming of Gerry", 1, "5/2", "Ruben Silvera", "Jamie Ness"),
        Horse("Hermoso Hombre", 2, "3/1", "Mychel J. Sanchez", "Michael V. Pino"),
        Horse("Gametime Gladiator", 3, "7/2", "Melvis Gonzalez", "Josue Arce"),
        Horse("Yodel E. A. Who", 4, "5/1", "Kendry Rivera", "Jamie Ness"),
        Horse("Nixon Joy", 5, "6/1", "Joezer Rangel", "Jose M. Santaella-Calderon"),
        Horse("Elusive Target", 6, "6/1", "Jean Aguilar", "Miguel Penaloza"),
    ]
    races.append(r9)

    # R10 - $5,000 Claiming F&M | 1M 70Y Dirt | $18,000
    r10 = Race(10, "Parx", "2026-03-16", "Claiming", "1M 70Y", "Dirt", 18000, "4:43 PM")
    r10.horses = [
        Horse("Pacific Princess", 1, "5/1", "Dexter Haddock", "Alexander Martinez"),
        Horse("Beachgrass", 2, "8/1", "Luis D. Rivera", "Jorge Diaz"),
        Horse("Miss Chamita", 3, "4/1", "Luis M. Ocasio", "Elliott Soto-Martinez"),
        Horse("Extremely Gruntled", 4, "15/1", "Eliseo Ruiz", "Thomas Iannotti IV"),
        Horse("Beyond a Million", 5, "8/1", "Ajhari Williams", "Abdul Williams"),
        Horse("Ghostly Girl", 6, "6/1", "Noel Herman", "Jorge Diaz"),
        Horse("Thegoddessofsnakes", 7, "4/5", "Ruben Silvera", "Jamie Ness"),
    ]
    races.append(r10)

    return races


def run_analysis(track_name, races):
    """Run analysis and return structured results."""
    all_analyses = []

    print(f"\n{'#' * 70}")
    print(f"  {track_name}")
    print(f"  VALUE HANDICAPPER v1.0 - Focus: Big Winners at Value Odds")
    print(f"{'#' * 70}")

    for race in races:
        analysis = analyze_race(race)
        all_analyses.append(analysis)
        print(format_race_analysis(analysis))

    print(generate_betting_card(all_analyses))

    # Collect all picks for tracking
    picks = []
    for a in all_analyses:
        race = a["race"]
        for h in a["ranked"]:
            if h.bet_type != "SKIP":
                picks.append({
                    "track": race.track,
                    "date": race.date,
                    "race": race.number,
                    "horse": h.name,
                    "odds": h.ml_odds,
                    "bet_type": h.bet_type,
                    "algo_score": h.algo_score,
                    "value_score": h.value_score,
                    "consensus": h.consensus_count,
                    "result": "PENDING"
                })

    return all_analyses, picks


def main():
    all_picks = []

    print("=" * 70)
    print("  MULTI-TRACK VALUE HANDICAPPER REPORT")
    print("  March 16-21, 2026")
    print("  Strategy: Find BIG WINNERS the public is sleeping on")
    print("=" * 70)
    print()
    print("APPROACH:")
    print("- Score every horse using multi-source consensus + value algorithm")
    print("- Prioritize horses at 4/1+ with expert support (VALUE PLAYS)")
    print("- Use contrarian logic in cheap claiming (upsets are common)")
    print("- Bet to WIN on value plays, PLACE as insurance")
    print("- Goal: Hit 1-2 big payoffs per day to be profitable")
    print()

    # Day 1: Fair Grounds March 16
    fg_analyses, fg_picks = run_analysis(
        "FAIR GROUNDS - Monday, March 16, 2026",
        build_fair_grounds_march16()
    )
    all_picks.extend(fg_picks)

    # Day 1: Parx March 16
    parx_analyses, parx_picks = run_analysis(
        "PARX RACING - Monday, March 16, 2026",
        build_parx_march16()
    )
    all_picks.extend(parx_picks)

    # MASTER SUMMARY
    print("\n" + "=" * 70)
    print("  MASTER BETTING CARD - ALL TRACKS - MARCH 16, 2026")
    print("=" * 70)

    value_plays = [p for p in all_picks if "VALUE" in p["bet_type"] or "SAVER" in p["bet_type"]]
    win_plays = [p for p in all_picks if "WIN" in p["bet_type"]]
    place_plays = [p for p in all_picks if "PLACE" in p["bet_type"]]

    print(f"\nTotal actionable picks: {len(all_picks)}")
    print(f"VALUE WIN plays (our bread and butter): {len(value_plays)}")
    print(f"Standard WIN plays: {len(win_plays)}")
    print(f"PLACE plays: {len(place_plays)}")

    if value_plays:
        print("\n--- TOP VALUE PLAYS (BEST BETS) ---")
        for p in sorted(value_plays, key=lambda x: x["algo_score"], reverse=True):
            potential = 2 * parse_odds_to_decimal(p["odds"])
            print(f"  {p['track']:<15} R{p['race']} | {p['horse']:<25} | {p['odds']:>6} | Score: {p['algo_score']} | Potential $2 win: ${potential:.2f}")

    print("\n--- ALL WIN PLAYS ---")
    for p in sorted(win_plays, key=lambda x: x["algo_score"], reverse=True):
        potential = 2 * parse_odds_to_decimal(p["odds"])
        marker = " ** VALUE **" if "VALUE" in p["bet_type"] else ""
        print(f"  {p['track']:<15} R{p['race']} | {p['horse']:<25} | {p['odds']:>6} | Pot: ${potential:.2f}{marker}")

    if place_plays:
        print("\n--- PLACE PLAYS ---")
        for p in sorted(place_plays, key=lambda x: x["algo_score"], reverse=True):
            print(f"  {p['track']:<15} R{p['race']} | {p['horse']:<25} | {p['odds']:>6} | Score: {p['algo_score']}")

    # Cost analysis
    total_cost = 0
    total_potential = 0
    for p in all_picks:
        if "WIN" in p["bet_type"]:
            amt = 3 if parse_odds_to_decimal(p["odds"]) >= 6.0 else 2
            total_cost += amt
            total_potential += amt * parse_odds_to_decimal(p["odds"])
        elif "PLACE" in p["bet_type"]:
            total_cost += 2

    print(f"\n--- COST ANALYSIS ---")
    print(f"Total investment: ${total_cost}")
    if win_plays:
        avg_odds = sum(parse_odds_to_decimal(p["odds"]) for p in win_plays) / len(win_plays)
        print(f"Average odds on WIN plays: {avg_odds:.1f}/1")
        print(f"If we hit just 1 VALUE play: likely covers entire day's bets")
        print(f"If we hit 2+ VALUE plays: PROFITABLE day")

    # Save picks for tracking
    picks_file = "/home/austin/race-day-cheat-card/algo/picks_tracker.json"
    with open(picks_file, "w") as f:
        json.dump(all_picks, f, indent=2)
    print(f"\nPicks saved to {picks_file} for results tracking")

    # UPCOMING PREVIEW
    print("\n" + "=" * 70)
    print("  UPCOMING RACE DAYS TO ANALYZE")
    print("=" * 70)
    print("  Tue Mar 17: Parx Racing (entries available, SFTB picks ready)")
    print("  Wed Mar 18: Parx Racing")
    print("  Thu Mar 19: Oaklawn Park (9 races, $448K purses)")
    print("  Fri Mar 20: Oaklawn Park (10 races, $513K purses)")
    print("  Sat Mar 21: Oaklawn Park (11 races, $1.05M purses - BIG DAY)")
    print("  Sun Mar 22: Oaklawn Park + Fair Grounds")
    print()
    print("Strategy note: Oaklawn Thu-Sat is our sweet spot from backtesting.")
    print("Maiden claiming races had 2/2 hits on Saturday. Higher purse races")
    print("are more predictable. The $1M+ Saturday card should be prime hunting.")


if __name__ == "__main__":
    main()
