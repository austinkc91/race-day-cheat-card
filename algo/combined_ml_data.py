#!/usr/bin/env python3
"""
Combined ML odds dataset from HRN scraping + existing deep_backtest data.
Each race has: ML odds for ALL horses, finishing order, race type.
We combine this with OTB exotic payouts for complete analysis.
"""

# Format: list of dicts, each with:
# - day: track + date identifier
# - race: race number
# - type: CLM/MC/MSW/ALW/AOC/SOC/STK
# - ml_odds: {horse_name: decimal_odds} (e.g. 5/2 = 2.5)
# - finish: [1st, 2nd, 3rd, 4th] horse names
# - starters: number of horses

RACES = [
    # ====== TAMPA BAY DOWNS - March 14, 2026 ======
    {"day": "TAM 2026-03-14", "race": 1, "type": "CLM",
     "ml_odds": {"Hurricane Season": 15, "La Chismosa": 1, "Drama": 2.5, "Win Bet Only": 6,
                 "Prancin Inthe Dark": 4, "Elsie's Smile": 15},
     "finish": ["La Chismosa", "Drama", "Elsie's Smile", "Prancin Inthe Dark"], "starters": 5},
    {"day": "TAM 2026-03-14", "race": 2, "type": "CLM",
     "ml_odds": {"Miguel's Belle": 8, "Ship It": 3, "Leprechauna": 4, "Opposite the Crowd": 3.5,
                 "Allons": 2.5, "Miss Classified": 20, "Fields of Green": 5},
     "finish": ["Fields of Green", "Miguel's Belle", "Allons", "Leprechauna"], "starters": 7},
    {"day": "TAM 2026-03-14", "race": 3, "type": "CLM",
     "ml_odds": {"Pat'schromecompass": 5, "Princess Vera": 1, "Country Economics": 30,
                 "Better Have Cash": 20, "Tinkatwo": 10, "Ride On Cupid": 12, "Dame Gina Marie": 2},
     "finish": ["Princess Vera", "Dame Gina Marie", "Tinkatwo", "Country Economics"], "starters": 7},
    {"day": "TAM 2026-03-14", "race": 4, "type": "MC",
     "ml_odds": {"Cloud Kisses": 15, "Cajun Empress": 12, "La Dinamita": 1.4, "Memory of My Life": 30,
                 "Red Hot Catalina": 1, "Queenofallmydreams": 30, "Free Charging": 10, "Queenmother": 30},
     "finish": ["La Dinamita", "Red Hot Catalina", "Free Charging", "Queenofallmydreams"], "starters": 8},
    {"day": "TAM 2026-03-14", "race": 5, "type": "CLM",
     "ml_odds": {"El Ma'any": 30, "Beware of Ooh Lala": 2, "Duchessa": 4.5, "Caura": 2,
                 "Noble Annie": 20, "Coqueta Blue": 12, "Parlaypauline": 4.5, "Vanish": 3,
                 "Duchess Eleanor": 6, "Radar Loop": 15},
     "finish": ["Duchessa", "Vanish", "Parlaypauline", "Radar Loop"], "starters": 10},
    {"day": "TAM 2026-03-14", "race": 6, "type": "CLM",
     "ml_odds": {"Super Tiz": 8, "Casino Night": 30, "Homer Jones": 4, "Secret Treasure": 3.5,
                 "Hay Moon": 30, "Wineman Trax": 20, "Saybrook": 2, "Triple Pass": 2.5},
     "finish": ["Saybrook", "Secret Treasure", "Triple Pass", "Homer Jones"], "starters": 8},
    {"day": "TAM 2026-03-14", "race": 7, "type": "CLM",
     "ml_odds": {"Classy Disposition": 15, "Bottle Rocket": 6, "Strand of Gold": 20,
                 "Expecting a Winner": 3.5, "Chris's Kitty": 12, "My Cajun Lady": 30,
                 "Timeless Rose": 5, "Sister Supream": 3, "Rose View": 8, "Perky": 4,
                 "Retail Therapist": 2, "Tiki Bar": 3.5, "Omikami": 12, "Independenceavenue": 3},
     "finish": ["Expecting a Winner", "Retail Therapist", "Timeless Rose", "Bottle Rocket"], "starters": 14},
    {"day": "TAM 2026-03-14", "race": 8, "type": "MC",
     "ml_odds": {"Kensington Avenue": 2, "Kenric": 12, "Deuxieme Chance": 2.5,
                 "All the Luck": 3.5, "Stoneybrook Road": 12, "Chequera": 8},
     "finish": ["Chequera", "Kensington Avenue", "All the Luck", "Stoneybrook Road"], "starters": 6},

    # ====== TAMPA BAY DOWNS - March 7, 2026 ======
    {"day": "TAM 2026-03-07", "race": 1, "type": "CLM",
     "ml_odds": {"Wicked Legacy": 12, "Derby Effort": 30, "Adios Tipsy": 10, "Mama Drama": 3,
                 "Mona L": 1.4, "Down in the Bayou": 20, "Belly Dance": 20, "Maca Abarrio": 30,
                 "Vesper Chicks": 3.5, "Collected Dreams": 20, "Hola Hermosa": 20, "Adjust My Halo": 30},
     "finish": ["Mama Drama", "Vesper Chicks", "Adios Tipsy", "Mona L"], "starters": 12},
    {"day": "TAM 2026-03-07", "race": 2, "type": "MSW",
     "ml_odds": {"Maykomotion": 4, "Bod Beach": 4.5, "Ace From Space": 2, "Royal Merit": 12,
                 "Anderman": 15, "Resolute Will": 3, "Maxxander": 10, "Gun Policy": 15},
     "finish": ["Maykomotion", "Bod Beach", "Ace From Space", "Resolute Will"], "starters": 8},
    {"day": "TAM 2026-03-07", "race": 3, "type": "STK",
     "ml_odds": {"Princess Britni": 12, "Flowers for Me": 12, "Summer's Comin": 12,
                 "St. Olaf Rose": 8, "Mystic Lake": 0.6, "It's Goodtobe Jose": 20, "My Magic Wand": 3},
     "finish": ["Mystic Lake", "My Magic Wand", "St. Olaf Rose", "It's Goodtobe Jose"], "starters": 7},
    {"day": "TAM 2026-03-07", "race": 4, "type": "STK",
     "ml_odds": {"Disruptor": 3.5, "Disco Time": 0.6, "Paynter's Prodigy": 30,
                 "Freedom Principle": 30, "Catalytic": 15, "Solo Venturi": 4, "Racing Driver": 10},
     "finish": ["Disruptor", "Disco Time", "Solo Venturi", "Freedom Principle"], "starters": 7},
    {"day": "TAM 2026-03-07", "race": 5, "type": "ALW",
     "ml_odds": {"Siyouni Flash": 20, "Naughty Favors": 20, "Portfolio Duration": 1.4,
                 "Notable Exchange": 8, "Midway Memories": 2.5, "Tinta Roja": 15,
                 "Sonja Henie": 6, "Mrs. Katz": 6, "Midway Vow": 30},
     "finish": ["Notable Exchange", "Tinta Roja", "Naughty Favors"], "starters": 9},
    {"day": "TAM 2026-03-07", "race": 6, "type": "SOC",
     "ml_odds": {"Alarik": 10, "Gotts Got It": 30, "Protege": 12, "Curlin Gunner": 6,
                 "In Sky We Trust": 20, "Gowokegobroke": 20, "El Chispazo": 8,
                 "Silver Slugger": 0.8, "Old Town Road": 30, "Holy Stick": 20, "Secret Empire": 5},
     "finish": ["Silver Slugger", "Alarik", "Secret Empire", "El Chispazo"], "starters": 11},
    {"day": "TAM 2026-03-07", "race": 7, "type": "STK",
     "ml_odds": {"Knoty Knicks": 6, "Proton": 3, "Congressional": 4, "Vino Solo": 30,
                 "Alpyland": 1.8, "Knick's Honor": 30, "Mr Mo's Magic": 10,
                 "Beautiful War": 6, "A Million Dreams": 20},
     "finish": ["Alpyland", "Proton", "Knoty Knicks", "Congressional"], "starters": 9},

    # ====== TAMPA BAY DOWNS - March 1, 2026 ======
    {"day": "TAM 2026-03-01", "race": 1, "type": "CLM",
     "ml_odds": {"Easy Come Easy Go": 1.6, "Thelastbulletsmine": 3.5, "Fields of Green": 5,
                 "Eros's Girl": 6, "Dancing Raquel": 5, "Heavenly Dancer": 8, "Miss Interpatation": 15},
     "finish": ["Easy Come Easy Go", "Thelastbulletsmine", "Dancing Raquel", "Fields of Green"], "starters": 7},
    {"day": "TAM 2026-03-01", "race": 2, "type": "AOC",
     "ml_odds": {"Adios Tootsie": 1.8, "Flowko": 6, "Bakers Island": 20,
                 "Questnbled'cisions": 2.5, "Turkish Pistachio": 3, "Permian Basin": 5},
     "finish": ["Adios Tootsie", "Permian Basin", "Flowko", "Bakers Island"], "starters": 6},
    {"day": "TAM 2026-03-01", "race": 3, "type": "CLM",
     "ml_odds": {"Calisue": 3, "Slew Crown": 10, "Ladys Chant": 15, "Once an Eagle": 20,
                 "Viking Queen": 1.4, "Woods Hole": 12, "That's My Cat": 6, "Kikilove": 4.5},
     "finish": ["That's My Cat", "Kikilove", "Calisue", "Once an Eagle"], "starters": 8},
    {"day": "TAM 2026-03-01", "race": 4, "type": "CLM",
     "ml_odds": {"Gary's Flying Lion": 20, "He's Side Eyed": 15, "Loyal Clement": 15,
                 "Wajda": 2, "Profitability": 6, "Bourbon Street Boy": 10,
                 "Koctel War": 4, "Cyberbeast": 2.5},
     "finish": ["Cyberbeast", "Bourbon Street Boy", "Loyal Clement", "Profitability"], "starters": 8},
    {"day": "TAM 2026-03-01", "race": 5, "type": "MC",
     "ml_odds": {"Band On the Run": 2, "Lady Hathor": 20, "Beautiful Emma": 4, "La Rodada": 8,
                 "Chefeta": 10, "Crescent Rising": 8, "She's Lit": 4.5, "Smittenwithtrouble": 30,
                 "D Orbie's Girl": 20, "First Hathor": 6, "Niecey": 3, "Mistrial Wind": 6, "Ship of Fools": 6},
     "finish": ["La Rodada", "Niecey", "Beautiful Emma", "First Hathor"], "starters": 13},
    {"day": "TAM 2026-03-01", "race": 6, "type": "CLM",
     "ml_odds": {"Cash the Check": 10, "Coqueta Blue": 2, "My Lil Flirt": 8, "Rules for Three": 5,
                 "Dixi So Fast": 15, "Somerset Mia": 10, "Prancin Inthe Dark": 1.6},
     "finish": ["Prancin Inthe Dark", "Coqueta Blue", "Somerset Mia", "My Lil Flirt"], "starters": 7},
    {"day": "TAM 2026-03-01", "race": 7, "type": "CLM",
     "ml_odds": {"El Bailador": 30, "Reteko": 2.5, "Weapon": 30, "Hands of Time": 2,
                 "Kid Kaos": 20, "Thingamabob": 8, "Ski Bum": 5, "And Thats My Story": 20,
                 "Maruvy": 6, "Daboom": 8, "Handsome Fox": 30},
     "finish": ["Reteko", "Hands of Time", "And Thats My Story", "Maruvy"], "starters": 11},

    # ====== TAMPA BAY DOWNS - Feb 28, 2026 ======
    {"day": "TAM 2026-02-28", "race": 1, "type": "MC",
     "ml_odds": {"D Dolly's Girl": 20, "She's the Rage": 2, "Givemeacookie": 20, "Flighttown": 12,
                 "Chabelita": 8, "Ez Yours": 20, "Wickedthiswaycomes": 4, "Miss Whinnie": 15,
                 "Melody Factor": 30, "Whiskey Whim": 1.8, "More Vino Rosa": 2.5,
                 "Kiss Me for Luck": 10, "Good Bianca": 4, "Volamo": 3},
     "finish": ["Wickedthiswaycomes", "More Vino Rosa", "She's the Rage", "D Dolly's Girl"], "starters": 14},
    {"day": "TAM 2026-02-28", "race": 2, "type": "MC",
     "ml_odds": {"La Reina Del Flow": 20, "Always Praising": 8, "Con Cautela": 3, "Nifty's Spirit": 8,
                 "Lucky Lil Kiss": 12, "Bit of Frost": 1.2, "Gallant Runner": 15, "Maggies Brew": 6},
     "finish": ["Bit of Frost", "Maggies Brew", "Con Cautela", "Always Praising"], "starters": 8},
    {"day": "TAM 2026-02-28", "race": 3, "type": "CLM",
     "ml_odds": {"Cox Canyon": 10, "Initforthelove": 20, "Crypto Man": 2.5, "Sargeant Barger": 30,
                 "King Freud": 3, "Crabcakes N Beer": 5, "Street Cop Officer": 4.5, "Funkenstein": 4},
     "finish": ["King Freud", "Crypto Man", "Street Cop Officer", "Crabcakes N Beer"], "starters": 8},
    {"day": "TAM 2026-02-28", "race": 4, "type": "CLM",
     "ml_odds": {"Fortunate Ryder": 4, "Westhampton": 8, "Mr Business": 5, "Hyper Venom": 8,
                 "Sky Masterson": 3.5, "Redemption Speight": 4.5, "Laird of Magnolia": 30,
                 "Sweet Tone": 5, "Ragman": 20, "So So": 15, "Steam Powered": 2,
                 "Ramesses": 15, "Deportivo": 8, "Calvino": 20},
     "finish": ["Steam Powered", "Sweet Tone", "Fortunate Ryder", "Deportivo"], "starters": 14},
    {"day": "TAM 2026-02-28", "race": 5, "type": "MC",
     "ml_odds": {"Party On Rufus": 15, "Johnny Bolt": 3, "Yadirayadirayadira": 30,
                 "Kissintheladies": 2, "R B's Runner": 20, "Spurious": 15, "Arrow Ghost": 20,
                 "Uncle Zeb": 15, "All the Luck": 3.5, "Rojo Sky": 30, "Kenric": 10,
                 "Dave Did It": 12, "Oh' What a Day": 4.5, "Dancing Bill": 6},
     "finish": ["Dancing Bill", "Arrow Ghost", "All the Luck", "Kenric"], "starters": 14},
    {"day": "TAM 2026-02-28", "race": 6, "type": "MSW",
     "ml_odds": {"Sylfrena": 8, "Mambo Taxi": 15, "Nahla": 1.8, "Sammytrinadamo": 3,
                 "Athenix": 2.5, "Endless Glory": 12, "Inkling": 8},
     "finish": ["Athenix", "Nahla", "Inkling", "Sylfrena"], "starters": 7},

    # ====== TAMPA BAY DOWNS - Feb 22, 2026 ======
    {"day": "TAM 2026-02-22", "race": 1, "type": "MC",
     "ml_odds": {"Gators Reign": 10, "Where's Jack": 30, "R Winchester": 1.8,
                 "North Ship": 1.2, "Broken Sound": 3.5, "Senor Resplandor": 10},
     "finish": ["North Ship", "R Winchester", "Senor Resplandor", "Gators Reign"], "starters": 6},
    {"day": "TAM 2026-02-22", "race": 2, "type": "MC",
     "ml_odds": {"Virgin Island Nice": 30, "Zimbawee": 30, "Bad Boy Butch": 1.2, "Skyliner": 20,
                 "Moralito": 2.5, "Madcap": 30, "Matty B Good": 6, "Senor Money": 3},
     "finish": ["Moralito", "Madcap", "Senor Money", "Matty B Good"], "starters": 8},
    {"day": "TAM 2026-02-22", "race": 3, "type": "CLM",
     "ml_odds": {"Ask the Monarch": 1.6, "Mizzen Millions": 20, "Smart Style": 10,
                 "Bravo Kitten": 1.5, "Mischievous Trick": 3.5, "Lil Temptation": 20, "Early Delivery": 15},
     "finish": ["Bravo Kitten", "Early Delivery", "Smart Style", "Ask the Monarch"], "starters": 7},
    {"day": "TAM 2026-02-22", "race": 4, "type": "CLM",
     "ml_odds": {"Lady Dominance": 8, "Classic Ballad": 4.5, "Lizzie Baby": 6,
                 "One Violent Affair": 3, "Pola of Trouble": 20, "China Blue": 3.5,
                 "Queen Atlas": 4.5, "Play Free Bird": 8},
     "finish": ["Classic Ballad", "China Blue", "One Violent Affair", "Lady Dominance"], "starters": 8},
    {"day": "TAM 2026-02-22", "race": 5, "type": "MC",
     "ml_odds": {"Xiao Long": 20, "Flamefire": 30, "No Merlot": 2.5, "Alrasikh": 3,
                 "Jobu": 8, "Devilment": 12, "Chilly Cheesesteak": 30, "Mr. Funtastico": 4.5,
                 "Sulion": 10, "Speaker's Lobby": 6, "Blue Sky's Syl": 30, "Royal Strike": 20,
                 "Skybreaker": 30, "Mossad": 20},
     "finish": ["Alrasikh", "No Merlot", "Sulion", "Mr. Funtastico"], "starters": 14},
    {"day": "TAM 2026-02-22", "race": 6, "type": "CLM",
     "ml_odds": {"Conspiracy Fact": 3, "Speedy Hans": 6, "Out Work'n": 30, "Pando": 10,
                 "Copazo": 3.5, "Peruvian Lucky": 10, "Peace Cloud": 10, "Passioned": 2.5, "Mission Mike": 10},
     "finish": ["Passioned", "Mission Mike", "Copazo", "Peace Cloud"], "starters": 9},
    {"day": "TAM 2026-02-22", "race": 7, "type": "MC",
     "ml_odds": {"Magica": 3, "Katarzyna": 8, "Zettie": 15, "Enchant": 4,
                 "British Empress": 20, "Deb's Sea Breeze": 30, "New Issue": 4.5,
                 "Miss Valentina": 15, "Money Trail": 3.5, "Sugar Magnolia": 6,
                 "Lil Miss Lollipop": 30, "Balitea": 30},
     "finish": ["New Issue", "Katarzyna", "Money Trail", "Zettie"], "starters": 12},

    # ====== SUNLAND PARK - March 9, 2026 ======
    {"day": "SUN 2026-03-09", "race": 1, "type": "CLM",
     "ml_odds": {"Ghostly Chance": 3.5, "George Who": 2.5, "Our Valentino": 1.6,
                 "Peekay": 3, "Wrecking Storm": 10, "Juana Rumble": 20},
     "finish": ["Ghostly Chance", "George Who", "Our Valentino", "Peekay"], "starters": 6},
    {"day": "SUN 2026-03-09", "race": 2, "type": "CLM",
     "ml_odds": {"I'mnotforeveryone": 3, "Hank Hill": 3.5, "Taz Marking": 6,
                 "Whiskey Rye": 2.5, "Running Bear": 4.5, "Distorted Guy": 15, "Snow Boots": 8},
     "finish": ["I'mnotforeveryone", "Hank Hill", "Taz Marking", "Whiskey Rye"], "starters": 7},
    {"day": "SUN 2026-03-09", "race": 3, "type": "CLM",
     "ml_odds": {"Corie's Boy": 5, "Fifth Street": 2, "Tiger by the Tail": 10,
                 "Crossrighthands": 3.5, "Diablo Rosso": 4, "Copper State": 8, "Spend Again": 8, "Using Nitro": 15},
     "finish": ["Corie's Boy", "Fifth Street", "Tiger by the Tail", "Crossrighthands"], "starters": 8},
    {"day": "SUN 2026-03-09", "race": 4, "type": "CLM",
     "ml_odds": {"Royal Lineage": 2.5, "Attila's Boy": 3, "Nobody's Perfect": 5,
                 "I'm a Dreamer Too": 15, "Bonnie Mae's Mark": 12, "Hennessy Looker": 4.5,
                 "Ronchetti": 6, "Sapello Sicario": 8},
     "finish": ["Royal Lineage", "Attila's Boy", "Nobody's Perfect", "I'm a Dreamer Too"], "starters": 8},
    {"day": "SUN 2026-03-09", "race": 5, "type": "MSW",
     "ml_odds": {"American Century": 3.5, "Made American": 3.5, "Gimme a Who": 2.5,
                 "Onwithit": 3, "Shiny Shores": 15, "I'm Just Playing": 8,
                 "Tap the Prize": 20, "Storm Cannon": 20, "D C Call Me George": 12},
     "finish": ["American Century", "Made American", "Gimme a Who", "Onwithit"], "starters": 9},
    {"day": "SUN 2026-03-09", "race": 6, "type": "MC",
     "ml_odds": {"Nogal": 3, "Low Rollin": 4.5, "American Class": 12, "Perfect Ruler": 4,
                 "Dashing American": 3.5, "Blues Money": 15, "Mighty Money": 8,
                 "Here I Go Again": 15, "Giuliano's Song": 10},
     "finish": ["Nogal", "Low Rollin", "American Class", "Perfect Ruler"], "starters": 9},
    {"day": "SUN 2026-03-09", "race": 7, "type": "CLM",
     "ml_odds": {"Leonas Girl": 5, "Hazhoni": 20, "Wild Steel": 2.5, "Sapello City Girl": 5,
                 "Contessa's Song": 8, "Empress in Front": 20, "Girls Don't Cry": 3.5,
                 "True Lovin": 4.5, "Danjerus Cloud": 20},
     "finish": ["Leonas Girl", "Hazhoni", "Wild Steel", "Sapello City Girl"], "starters": 9},
    {"day": "SUN 2026-03-09", "race": 8, "type": "CLM",
     "ml_odds": {"American Cherub": 2, "Annie Get Ur Guns": 20, "Pop's Party": 3.5,
                 "I Get Stormed": 20, "K P Blamengame": 15, "La Bella Bella": 12,
                 "Sis Spender": 4.5, "Just Keep Laughin": 2.5},
     "finish": ["American Cherub", "Annie Get Ur Guns", "Pop's Party", "I Get Stormed"], "starters": 8},
    {"day": "SUN 2026-03-09", "race": 9, "type": "SOC",
     "ml_odds": {"Red Leader": 4, "Mister Mafioso": 4, "Leap Day": 6, "Discreet Tiger": 12,
                 "Shug's Rocket": 3, "Lonzo Who": 5, "Marquis Lights": 15, "Awesome Notion": 8},
     "finish": ["Red Leader", "Mister Mafioso", "Leap Day", "Discreet Tiger"], "starters": 8},

    # ====== SUNLAND PARK - March 2, 2026 ======
    {"day": "SUN 2026-03-02", "race": 1, "type": "MSW",
     "ml_odds": {"Dialed Who": 3.5, "Street Colors": 8, "Eskimo Charlie": 4, "Sr Andrew": 20,
                 "Shiny Shores": 10, "Back Pay": 15, "Roki": 4.5, "Honor the Giants": 1.6},
     "finish": ["Roki", "Eskimo Charlie", "Dialed Who", "Back Pay"], "starters": 8},
    {"day": "SUN 2026-03-02", "race": 2, "type": "CLM",
     "ml_odds": {"Girls Don't Cry": 4, "Regal's Charm": 4.5, "Swaying Lassie": 20,
                 "Discreet Pleasure": 6, "Charliene": 5, "Jolie Candy": 1.5,
                 "Contessa's Song": 8, "Miss Kenzie": 15},
     "finish": ["Jolie Candy", "Discreet Pleasure", "Regal's Charm", "Swaying Lassie"], "starters": 8},
    {"day": "SUN 2026-03-02", "race": 3, "type": "CLM",
     "ml_odds": {"Rapid Expansion": 5, "Rio Cutie": 6, "Piney Bluff": 10, "Khantaro d'Oro": 2.5,
                 "Rainbow Crest": 8, "McGregor Lake": 2, "Lovesunfair": 8, "Hollywood Tiz": 20},
     "finish": ["Lovesunfair", "Khantaro d'Oro", "Rainbow Crest", "Rio Cutie"], "starters": 8},
    {"day": "SUN 2026-03-02", "race": 4, "type": "CLM",
     "ml_odds": {"Attilianno": 1.8, "Effort N Results": 10, "Shame On Whiskey": 4.5,
                 "Aaron Who": 8, "Tatas Joe Mark": 8, "Diabolical Fire": 12,
                 "Ryders Up": 20, "New Mexico Jeremy": 6, "Be a Pro": 5},
     "finish": ["Attilianno", "Be a Pro", "Tatas Joe Mark", "Aaron Who"], "starters": 9},
    {"day": "SUN 2026-03-02", "race": 5, "type": "SOC",
     "ml_odds": {"Roll Penny Roll": 2.5, "Tsunami Gold": 5, "Danz At Colfax": 12,
                 "Marquis Lights": 15, "Henry On the Run": 8, "Shug's Rocket": 8,
                 "Lonzo Who": 4, "Daux": 3},
     "finish": ["Daux", "Lonzo Who", "Roll Penny Roll", "Marquis Lights"], "starters": 8},
    {"day": "SUN 2026-03-02", "race": 6, "type": "SOC",
     "ml_odds": {"Nang Singha": 2.5, "Forever Safe": 4, "Lucky Vegas": 2, "Whimsical Heir": 15,
                 "Sweet Hello": 8, "Distorted Cat": 20, "Sequin Lady": 5, "Work N Flirt": 15},
     "finish": ["Lucky Vegas", "Whimsical Heir", "Work N Flirt", "Nang Singha"], "starters": 8},
    {"day": "SUN 2026-03-02", "race": 7, "type": "CLM",
     "ml_odds": {"We Need Marketing": 15, "Kirby Derby": 3, "Holcombe": 10, "Ten Figures": 3.5,
                 "American Empire": 4, "Upward Mobility": 15, "Sharp Stick": 12, "Free Again": 2.5},
     "finish": ["Kirby Derby", "Upward Mobility", "Free Again", "American Empire"], "starters": 8},
    {"day": "SUN 2026-03-02", "race": 8, "type": "ALW",
     "ml_odds": {"Holy Bullet": 4.5, "Stand Up Guy": 3.5, "Adiel": 8, "Colfax Kid": 15,
                 "Sapello Riddler": 15, "Exit Strategy": 10, "He's a Genius": 12,
                 "Gamblaway": 5, "American Ranger Bb": 2.5},
     "finish": ["American Ranger Bb", "Adiel", "Exit Strategy", "Stand Up Guy"], "starters": 9},

    # ====== OAKLAWN PARK - March 15, 2026 ======
    {"day": "OAK 2026-03-15", "race": 1, "type": "CLM",
     "ml_odds": {"Parking Lot Pours": 1.8, "Carmalieta": 20, "Came Up Roses": 5,
                 "Kentucky Starlet": 2, "Reign Champagne": 8, "Bl Forty": 12, "L.A. Diamond": 4.5},
     "finish": ["L.A. Diamond", "Parking Lot Pours", "Carmalieta", "Bl Forty"], "starters": 7},
    {"day": "OAK 2026-03-15", "race": 2, "type": "MC",
     "ml_odds": {"Improbability": 3.5, "Lower Broadway": 3.5, "Doyouhearme": 20, "Convolution": 12,
                 "Ripple's Rocket": 6, "E Money": 15, "Amentum": 4, "Good News Rocket": 1},
     "finish": ["Good News Rocket", "Amentum", "Lower Broadway", "Convolution"], "starters": 8},
    {"day": "OAK 2026-03-15", "race": 3, "type": "AOC",
     "ml_odds": {"Lochmoor": 4, "Cybertown": 2.5, "Hess": 8, "Willow Creek Road": 3.5,
                 "Afleet Sky": 30, "Man in the Can": 4.5, "One Ten Stadium": 3},
     "finish": ["Willow Creek Road", "Cybertown", "One Ten Stadium", "Hess"], "starters": 7},
    {"day": "OAK 2026-03-15", "race": 4, "type": "MC",
     "ml_odds": {"Why Chris Why": 15, "Miracle Minded": 2, "Battisto": 20, "Closdatgate": 12,
                 "C Note Gia": 30, "Donita": 3, "Open Flame": 4, "Kava": 2.5},
     "finish": ["Donita", "Kava", "Miracle Minded", "Battisto"], "starters": 8},
    {"day": "OAK 2026-03-15", "race": 5, "type": "CLM",
     "ml_odds": {"Tahoe Run": 15, "The Thunderer": 10, "What's Up Doc": 3.5, "Gasoline": 8,
                 "Excel Calculator": 4, "Critical Threat": 20, "Camp Daddy": 3,
                 "Global Empire": 5, "Metatron's Muse": 6, "Ember": 30},
     "finish": ["The Thunderer", "Tahoe Run", "Global Empire", "Camp Daddy"], "starters": 10},
    {"day": "OAK 2026-03-15", "race": 6, "type": "MSW",
     "ml_odds": {"American Man": 3.5, "Black Star": 3, "Stone County": 12, "Noble Anthem": 12,
                 "Mumdoggie": 2.5, "Himothy": 4.5, "Mr. Tallymon": 20, "Vintage Cowboy": 5},
     "finish": ["American Man", "Mumdoggie", "Vintage Cowboy", "Noble Anthem"], "starters": 8},
    {"day": "OAK 2026-03-15", "race": 7, "type": "CLM",
     "ml_odds": {"Surveillance": 2, "Oscar Eclipse": 15, "Otto the Conqueror": 4.5,
                 "Sinner's Sin": 3.5, "Bron and Brow": 20, "Lunar Module": 4,
                 "Empire Builder": 8, "Ghost of Midnight": 6},
     "finish": ["Otto the Conqueror", "Surveillance", "Oscar Eclipse", "Ghost of Midnight"], "starters": 8},
    {"day": "OAK 2026-03-15", "race": 8, "type": "ALW",
     "ml_odds": {"Ms Carroll County": 3, "Plinko Chip": 15, "Miss Macy": 4, "Bossoftheblock": 12,
                 "Sisters in Town": 8, "Rockin the Lane": 15, "Ministry's Destiny": 6,
                 "Cashmere Baby": 20, "Woodruff": 15, "Queen Mallard": 3.5, "Doubledaddy Issues": 12},
     "finish": ["Miss Macy", "Ms Carroll County", "Queen Mallard"], "starters": 11},
]

# Add the existing 43 races from deep_backtest.py
# Import and convert
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
try:
    from deep_backtest import RACE_DATA as DEEP_RACES
    for r in DEEP_RACES:
        if r.get("ml_odds") and r.get("finish"):
            RACES.append({
                "day": r["day"],
                "race": r["race"],
                "type": r["type"],
                "ml_odds": r["ml_odds"],
                "finish": r["finish"],
                "starters": r["starters"],
                "exacta_pay": r.get("exacta_pay"),
                "trifecta_pay": r.get("trifecta_pay"),
                "superfecta_pay": r.get("superfecta_pay"),
            })
except:
    pass


def get_ml_rank(race, horse_name):
    """Get a horse's ML rank (1=favorite, 2=2nd choice, etc)."""
    ml = race["ml_odds"]
    sorted_horses = sorted(ml.keys(), key=lambda h: ml[h])
    for i, h in enumerate(sorted_horses, 1):
        if h == horse_name:
            return i
    return len(ml) + 1


def get_ml_sorted(race):
    """Get horses sorted by ML odds (favorite first)."""
    return sorted(race["ml_odds"].keys(), key=lambda h: race["ml_odds"][h])


if __name__ == "__main__":
    print(f"Total races in dataset: {len(RACES)}")
    days = set(r["day"] for r in RACES)
    print(f"Track-days: {len(days)}")
    for d in sorted(days):
        races_in_day = [r for r in RACES if r["day"] == d]
        types = [r["type"] for r in races_in_day]
        clm_count = sum(1 for t in types if t in ("CLM", "MC", "SOC"))
        print(f"  {d}: {len(races_in_day)} races ({clm_count} CLM/MC/SOC)")

    # Quick stats
    type_counts = {}
    for r in RACES:
        type_counts[r["type"]] = type_counts.get(r["type"], 0) + 1
    print(f"\nBy type: {type_counts}")
