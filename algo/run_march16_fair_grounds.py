#!/usr/bin/env python3
"""
Fair Grounds Race Analysis - Monday, March 16, 2026
Multi-source consensus + value algorithm picks
"""

from value_handicapper import *


def build_fair_grounds_march16():
    """Build race card with all source data compiled."""
    races = []

    # ============================================================
    # RACE 1 - Maiden Claiming | 5.5F Dirt | $14,000 | 12:45 PM
    # ============================================================
    r1 = Race(1, "Fair Grounds", "March 16, 2026", "Maiden Claiming", "5.5F", "Dirt", 14000, "12:45 PM")
    r1.horses = [
        Horse("Flora Bound", 1, "5/1", "Micah Meeks", "David Terre"),
        Horse("Goodmorning Gracie", 2, "9/2", "Mitchell Murrill", "Joseph M. Foster",
              sftb_rank=1.8),
        Horse("Stormy Lou", 3, "6/1", "Juan P. Vargas", "Gerard Perron"),
        Horse("Metallic Maid", 4, "9/2", "Marcelino Pedroza Jr.", "Carrol Castille",
              sftb_rank=1.8),
        Horse("Hannah Boo", 5, "7/2", "Sofia Vives", "Sam B. David Jr.",
              sftb_rank=1.0, racing_dudes_pick=True),
        Horse("Go North Boss", 6, "8/1", "Harry Hernandez", "Jonathan Wong"),
        Horse("Stella Guitar", 7, "4/1", "Axel Concepcion", "W. Bret Calhoun",
              sftb_rank=1.4, hrn_pick=True),
        Horse("Miss Maddie", 8, "12/1", "Jose Riquelme", "Emile Schwandt"),
    ]
    races.append(r1)

    # ============================================================
    # RACE 2 - Claiming 3yo Fillies | 6F Dirt | $18,000 | 1:15 PM
    # ============================================================
    r2 = Race(2, "Fair Grounds", "March 16, 2026", "Claiming", "6F", "Dirt", 18000, "1:15 PM")
    r2.horses = [
        Horse("Authentic Angel", 1, "7/2", "James Graham", "J. Keith Desormeaux",
              sftb_rank=1.5),
        Horse("Ice Cold Blonde", 2, "7/2", "Sofia Vives", "Whitney J. Zeringue Jr.",
              sftb_rank=1.5),
        Horse("Hold the Drama", 3, "4/1", "Harry Hernandez", "Jonathan Wong"),
        Horse("Kitten Gloves", 4, "4/1", "Jose L. Ortiz", "Randy Degeyter Jr.",
              racing_dudes_pick=True, hrn_pick=True),  # Racing Dudes AND HRN pick + top jockey
        Horse("Undisputable", 5, "3/1", "Colby J. Hernandez", "Dallas Stewart",
              sftb_rank=1.0),
        Horse("Great Owl", 6, "8/1", "Hunter Rea", "Larry Rivelli"),
    ]
    races.append(r2)

    # ============================================================
    # RACE 3 - Starter Optional Claiming | 1M Turf | $19,000 | 1:45 PM
    # ============================================================
    r3 = Race(3, "Fair Grounds", "March 16, 2026", "Starter Optional Claiming", "1M", "Turf", 19000, "1:45 PM")
    r3.horses = [
        Horse("Even the Wind", 1, "12/1", "Marcelino Pedroza Jr.", "Chris M. Block"),
        Horse("Bigfoot Sighting", 2, "20/1", "Jose Luis Rodriguez", "Cesar Govea"),
        Horse("Moogie Son", 3, "20/1", "Sofia Vives", "Larry Rivelli"),
        Horse("Foxtrot Harry", 4, "6/1", "Isaac Castillo", "Jonathan Wong",
              hrn_pick=True),  # HRN's top pick at 6/1 - VALUE!
        Horse("Not Falling Back", 5, "12/1", "Jareth Loveberry", "Chris M. Block",
              racing_dudes_pick=True),  # Racing Dudes pick at 12/1 - BIG VALUE!
        Horse("Fortuity", 6, "10/1", "Jansen Melancon", "Randy Degeyter Jr."),
        Horse("Red Road", 7, "7/2", "Brian J. Hernandez Jr.", "Sturges J. Ducoing",
              sftb_rank=1.8),
        Horse("Twoko Bay", 8, "20/1", "Erica M. Murray", "Gary M. Scherer"),
        Horse("Boitano", 9, "2/1", "Axel Concepcion", "Jose M. Camejo",
              sftb_rank=1.0),  # Heavy favorite - SFTB top pick
        Horse("Mister Muldoon", 10, "7/2", "James Graham", "Hugh H. Robertson",
              sftb_rank=1.8),
    ]
    races.append(r3)

    # ============================================================
    # RACE 4 - Allowance 3yo Fillies | 1-1/16M Dirt | $55,000 | 2:15 PM
    # ============================================================
    r4 = Race(4, "Fair Grounds", "March 16, 2026", "Allowance", "1-1/16M", "Dirt", 55000, "2:15 PM")
    r4.horses = [
        Horse("Majestical", 1, "2/1", "Jose L. Ortiz", "Peter Eurton",
              racing_dudes_pick=True, sftb_rank=1.0),  # Chalk - top jockey, top trainer
        Horse("Huck's Agenda", 2, "5/2", "Brian J. Hernandez Jr.", "Kenneth G. McPeek"),
        Horse("Sticker Shocked", 3, "3/1", "Colby J. Hernandez", "Kenneth G. McPeek"),
        Horse("Zaffa", 4, "6/1", "Declan Cannon", "Brendan P. Walsh"),
        Horse("A. P.'s Girl", 5, "3/1", "Ben Curtis", "Peter Eurton"),
    ]
    races.append(r4)

    # ============================================================
    # RACE 5 - Claiming F&M | 6F Dirt | $20,000 | 2:45 PM
    # ============================================================
    r5 = Race(5, "Fair Grounds", "March 16, 2026", "Claiming", "6F", "Dirt", 20000, "2:45 PM")
    r5.horses = [
        Horse("Charge the Deal", 1, "15/1", "Isaac Castillo", "Juan A. Larrosa"),
        Horse("Dose of Reality", 2, "6/1", "Hunter Rea", "Carl J. Woodley"),
        Horse("Kin to the Wicked", 3, "4/5", "Axel Concepcion", "W. Bret Calhoun",
              sftb_rank=1.0, racing_dudes_pick=True),  # HEAVY chalk at 4/5
        Horse("La Maxima", 4, "9/2", "Jose L. Ortiz", "Alexis Claire"),
        Horse("Blissit", 5, "10/1", "Mitchell Murrill", "Joseph M. Foster"),
        Horse("John's June", 6, "20/1", "Emanuel Nieves", "Samuel Breaux"),
        Horse("Miss Makeithappen", 7, "12/1", "Juan P. Vargas", "Ricky Demouchet"),
        Horse("Platinumus Maximus", 8, "12/1", "Marcelino Pedroza Jr.", "Carrol Castille"),
        Horse("Little Em", 9, "12/1", "Sofia Vives", "Sam B. David Jr."),
    ]
    races.append(r5)

    # ============================================================
    # RACE 6 - Claiming | 1-1/16M Turf | $28,000 | 3:15 PM
    # ============================================================
    r6 = Race(6, "Fair Grounds", "March 16, 2026", "Claiming", "1-1/16M", "Turf", 28000, "3:15 PM")
    r6.horses = [
        Horse("Flamingproposition", 1, "12/1", "Harry Hernandez", "Jonathan Wong"),
        Horse("Enlighten", 2, "5/1", "Micah Meeks", "Keith A. Austin",
              racing_dudes_pick=True),  # Racing Dudes pick at 5/1 - value spot
        Horse("Another Mystery", 3, "4/1", "Jareth Loveberry", "Chris M. Block"),
        Horse("Bold Discovery", 4, "12/1", "Emanuel Nieves", "Rob Atras"),
        Horse("Polar Bear Plunge", 5, "9/2", "Axel Concepcion", "Mertkan Kantarmaci"),
        Horse("Frosty Blue", 6, "6/1", "Marcelino Pedroza Jr.", "Allen Landry"),
        Horse("Summer in Adriane", 7, "9/2", "Ben Curtis", "Michael J. Maker"),
        Horse("Ever Dangerous", 8, "5/1", "Isaac Castillo", "Robertino Diodoro"),
        Horse("Next Level", 9, "8/1", "James Graham", "J. Keith Desormeaux"),
    ]
    races.append(r6)

    # ============================================================
    # RACE 7 - Maiden Optional Claiming 3yo | 6F Dirt | $30,000 | 3:45 PM
    # ============================================================
    r7 = Race(7, "Fair Grounds", "March 16, 2026", "Maiden Optional Claiming", "6F", "Dirt", 30000, "3:45 PM")
    r7.horses = [
        Horse("Kalatua", 1, "8/1", "Ben Curtis", "Hugh H. Robertson"),
        Horse("Hutchinson", 2, "12/1", "James Graham", "J. Keith Desormeaux"),
        Horse("Pampered Prince", 3, "8/1", "Jareth Loveberry", "Albert M. Stall Jr."),
        Horse("La Norme de Jour", 4, "8/1", "Axel Concepcion", "W. Bret Calhoun"),
        Horse("Apollo Eleven", 5, "10/1", "Isaac Castillo", "Norm W. Casse"),
        Horse("Editor", 6, "4/1", "Marcelino Pedroza Jr.", "Joe Sharp"),
        Horse("General Graham", 7, "3/1", "Jose L. Ortiz", "Eddie Kenneally",
              racing_dudes_pick=True),  # Top jockey + Racing Dudes
        Horse("Kingofsomewherehot", 8, "9/2", "Brian J. Hernandez Jr.", "Kenneth G. McPeek"),
        Horse("Candy Dreamin", 9, "10/1", "Juan P. Vargas", "Juan A. Larrosa"),
    ]
    races.append(r7)

    # ============================================================
    # RACE 8 - Allowance OC | 5.5F Turf | $56,000 | 4:15 PM
    # ============================================================
    r8 = Race(8, "Fair Grounds", "March 16, 2026", "Allowance Optional Claiming", "5.5F", "Turf", 56000, "4:15 PM")
    r8.horses = [
        Horse("Pineland", 1, "9/2", "Declan Cannon", "Lindsay Schultz",
              racing_dudes_pick=True),
        Horse("Mister Mmmmm", 2, "4/1", "Jose L. Ortiz", "Joe Sharp"),
        Horse("That's Right", 3, "5/1", "Ben Curtis", "Joe Sharp"),
        Horse("Rock N Roll Bolt", 4, "8/1", "Axel Concepcion", "Jose M. Camejo"),
        Horse("Bridle a Butterfly", 5, "8/1", "Sofia Vives", "Albert M. Stall Jr."),
        Horse("Fit to Fly", 6, "6/1", "Isaac Castillo", "Aubrie Suarez"),
        Horse("Vesture", 7, "7/2", "Brian J. Hernandez Jr.", "W. Bret Calhoun"),
        Horse("Amoudi Bay", 8, "6/1", "James Graham", "Lindsay Schultz"),
    ]
    races.append(r8)

    # ============================================================
    # RACE 9 - Claiming F&M | 1M 70Y Dirt | $15,000 | 4:45 PM
    # ============================================================
    r9 = Race(9, "Fair Grounds", "March 16, 2026", "Claiming", "1M 70Y", "Dirt", 15000, "4:45 PM")
    r9.horses = [
        Horse("Sweet Alexis", 1, "3/1", "Juan P. Vargas", "Keith G. Bourgeois",
              racing_dudes_pick=True),
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


def main():
    races = build_fair_grounds_march16()
    all_analyses = []

    print("\n" + "=" * 70)
    print("  FAIR GROUNDS - MONDAY, MARCH 16, 2026")
    print("  VALUE HANDICAPPER ALGORITHM v1.0")
    print("  Strategy: Find big-payout winners the public is sleeping on")
    print("=" * 70)

    for race in races:
        analysis = analyze_race(race)
        all_analyses.append(analysis)
        print(format_race_analysis(analysis))

    # Generate betting card
    print(generate_betting_card(all_analyses))

    # Summary stats
    print("\n" + "=" * 60)
    print("RACE DAY SUMMARY")
    print("=" * 60)

    all_value_plays = []
    all_picks = []
    for a in all_analyses:
        for h in a["ranked"]:
            if h.bet_type != "SKIP":
                all_picks.append(h)
            if h.bet_type in ("VALUE WIN", "SAVER"):
                all_value_plays.append(h)

    print(f"\nTotal races analyzed: {len(races)}")
    print(f"Total picks: {len(all_picks)}")
    print(f"Value plays (longshots with support): {len(all_value_plays)}")

    if all_value_plays:
        print("\nVALUE PLAYS TO WATCH:")
        for h in sorted(all_value_plays, key=lambda x: x.algo_score, reverse=True):
            print(f"  {h.name:<25} {h.ml_odds:>6} | Score: {h.algo_score} | Value: {h.value_score:.1f}")


if __name__ == "__main__":
    main()
