import json
import hashlib

# Some of these names are changed (standardized) later in this file
# If common_utils is imported, names seen here may be different than names as accessed
# standardize_name is meant to help with this
NEUTRAL_SITE_MATCHUPS = [
    {'Navy', 'Notre Dame'},
    # {'Jackson State', 'SC State'},
    # {'North Alabama', 'Mercer'},
    {'Louisville', 'Georgia Tech'},
    # {'Hampton', 'Grambling'},
    # {'Central State', 'MVSU'},
    {'North Carolina', 'South Carolina'},
    # {'Eastern Washington', 'NDSU'},
    {'Virginia', 'Tennessee'},
    {'LSU', 'Florida State'},
    # {'Jackson State', 'Florida A&M'},
    {'Air Force', 'Sam Houston'},
    # {'UAPB', 'Tennessee State'},
    # {'Drake', 'South Dakota State'},
    # {'Hampton', 'Howard'},
    {'Indiana', 'Louisville'},
    # {'NC Central', 'MVSU'},
    {'Memphis', 'Missouri'},
    # {'Harvard', 'Holy Cross'},
    {'Texas A&M', 'Arkansas'},
    # {'Grambling', 'PVAMU'},
    {'Oklahoma', 'Texas'},
    # {'Jackson State', 'Alabama A&M'},
    # {'Southern', 'Bethune-Cookman'},
    # {'Alabama State', 'Alabama A&M'},
    {'Georgia', 'Florida'},
    # {'Grambling', 'Alabama State'},
    {'Iowa', 'Northwestern'},
    {'Army', 'Air Force'},
    {'Pitt', 'Syracuse'},
    # {'Bethune-Cookman', 'FAMU'},
    {'Penn State', 'Michigan State'},
    # {'Southern', 'Grambling'},
    {'Navy', 'Army'},
]

TEAM_ALIASES = {
    "Boston College": {},
    "Clemson": {},
    "Florida State": {},
    "Louisville": {},
    "North Carolina State": {"NC State"},
    "Syracuse": {},
    "Wake Forest": {},
    "Duke": {},
    "Georgia Tech": {},
    "Miami (FL)": {"Miami FL", "Miami"},
    "North Carolina": {},
    "Pittsburgh": {"Pitt"},
    "Virginia": {},
    "Virginia Tech": {},
    "Charlotte": {},
    "East Carolina": {},
    "Florida Atlantic": {},
    "Memphis": {},
    "Navy": {},
    "North Texas": {},
    "Rice": {},
    "SMU": {},
    "South Florida": {"USF"},
    "Temple": {},
    "Tulane": {},
    "Tulsa": {},
    "UAB": {},
    "UTSA": {},
    "Baylor": {},
    "BYU": {},
    "Cincinnati": {},
    "Houston": {},
    "Iowa State": {},
    "Kansas": {},
    "Kansas State": {},
    "Oklahoma": {},
    "Oklahoma State": {},
    "TCU": {},
    "Texas": {},
    "Texas Tech": {},
    "UCF": {},
    "West Virginia": {},
    "Indiana": {},
    "Maryland": {},
    "Michigan": {},
    "Michigan State": {},
    "Ohio State": {},
    "Penn State": {},
    "Rutgers": {},
    "Illinois": {},
    "Iowa": {},
    "Minnesota": {},
    "Nebraska": {},
    "Northwestern": {},
    "Purdue": {},
    "Wisconsin": {},
    "Florida International": {"FIU"},
    "Jacksonville State": {},
    "Liberty": {},
    "Louisiana Tech": {},
    "Middle Tennessee": {},
    "New Mexico State": {},
    "Sam Houston State": {"Sam Houston"},
    "UTEP": {},
    "Western Kentucky": {"WKU"},
    "Army": {"Army West Point"},
    "Notre Dame": {},
    "UConn": {},
    "UMass": {"Massachusetts"},
    "Akron": {},
    "Bowling Green": {},
    "Buffalo": {},
    "Kent State": {},
    "Miami (OH)": {"Miami OH", "Miami (Ohio)"},
    "Ohio": {},
    "Ball State": {},
    "Central Michigan": {},
    "Eastern Michigan": {},
    "Northern Illinois": {"NIU"},
    "Toledo": {},
    "Western Michigan": {},
    "Air Force": {},
    "Boise State": {},
    "Colorado State": {},
    "New Mexico": {},
    "Utah State": {},
    "Wyoming": {},
    "Fresno State": {},
    "Hawai'i": {"Hawaii"},
    "Nevada": {},
    "San Diego State": {},
    "San Jose State": {"San José State"},
    "UNLV": {},
    "Arizona": {},
    "Arizona State": {},
    "California": {},
    "Colorado": {},
    "Oregon": {},
    "Oregon State": {},
    "Stanford": {},
    "UCLA": {},
    "USC": {},
    "Utah": {},
    "Washington": {},
    "Washington State": {},
    "Florida": {},
    "Georgia": {},
    "Kentucky": {},
    "Missouri": {},
    "South Carolina": {},
    "Tennessee": {},
    "Vanderbilt": {},
    "Alabama": {},
    "Arkansas": {},
    "Auburn": {},
    "LSU": {},
    "Mississippi State": {},
    "Ole Miss": {"Mississippi"},
    "Texas A&M": {},
    "Appalachian State": {},
    "Coastal Carolina": {},
    "Georgia Southern": {},
    "Georgia State": {},
    "James Madison": {},
    "Marshall": {},
    "Old Dominion": {},
    "Arkansas State": {},
    "Louisiana": {},
    "Louisiana-Monroe": {"ULM", "UL Monroe"},
    "South Alabama": {},
    "Southern Miss": {},
    "Texas State": {},
    "Troy": {}
}

def convert_line_to_win_probability(favored_by):
    magnitude = abs(favored_by)
    if magnitude > 20:
        if favored_by < 0:
            return 1 - 0.99
        else:
            return 0.99
        
    magnitude = round_decimal_line(magnitude)
    favored = favored_by > 0

    line_to_prob = {
        0: 0.5,
        0.5: 0.5,
        1: 0.512,
        1.5: 0.525,
        2: 0.534,
        2.5: 0.543,
        3: 0.574,
        3.5: 0.6060,
        4: 0.6190,
        4.5: 0.631,
        5: 0.641,
        5.5: 0.651,
        6: 0.664,
        6.5: 0.677,
        7: 0.703,
        7.5: 0.730,
        8: 0.738,
        8.5: 0.746,
        9: 0.751,
        9.5: 0.755,
        10: 0.774,
        10.5: 0.793,
        11: 0.799,
        11.5: 0.806,
        12: 0.816,
        12.5: 0.826,
        13: 0.83,
        13.5: 0.835,
        14: 0.851,
        14.5: 0.868,
        15: 0.874,
        15.5: 0.881,
        16: 0.886,
        16.5: 0.891,
        17: 0.914,
        17.5: 0.937,
        18: 0.95,
        18.5: 0.962,
        19: 0.973,
        19.5: 0.984,
        20: 0.99
    }

    mag_prob = line_to_prob[magnitude]
    if favored:
        return mag_prob
    return 1 - mag_prob


def round_decimal_line(line):
    decimal = abs(line) % 1
    if decimal in {0.0, 0.5}:
        return line
    
    whole = abs(line) // 1
    direction = -1 if line < 0 else 1
    rounded_decimal = 0.0
    if decimal >= 0.75:
        rounded_decimal = 1.0
    elif decimal > 0.25 and decimal < 0.75:
        rounded_decimal = 0.5
    
    if direction < 0:
        rounded_decimal = 0 - rounded_decimal
    return direction*whole + rounded_decimal

def clean_name(name):
    name = name.replace('amp;', '')
    return name

def standardize_name(name):
    # Need to add more, but placeholder for now
    name = clean_name(name)
    if name not in TEAM_ALIASES.keys():
        for standardized_name, aliases in TEAM_ALIASES.items():
            if name in aliases:
                return standardized_name
    if name not in TEAM_ALIASES.keys():
        print(f'Found unrecognized team: {name}')
    return name

NEUTRAL_SITE_MATCHUPS = [
    set((standardize_name(list(m)[0]), standardize_name(list(m)[1]))) for m in NEUTRAL_SITE_MATCHUPS
]

# This function creates a hash of the 2 team names, irrespective of order
def get_id_for_matchup(str1, str2):
    combined_str = str1 + '#' + str2 if str1 < str2 else str2 + '#' + str1
    hash_object = hashlib.sha256(combined_str.encode())
    unique_string = hash_object.hexdigest()
    return unique_string