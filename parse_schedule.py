from common_utils import *
import json

DATA_BASE_DIRECTORY = '524-01'

def parse_matchup(line):
    if " vs. " in line:
        teams = line.split(" vs. ")
        team0 = standardize_name(teams[0].strip())
        team1 = standardize_name(teams[1].strip())
        neutral = False
        if {team0, team1} in NEUTRAL_SITE_MATCHUPS:
            neutral = True
        return {
            "home_team": team0,
            "away_team": team1,
            "neutral": neutral
        }
    elif " at " in line:
        teams = line.split(" at ")
        team0 = standardize_name(teams[0].strip())
        team1 = standardize_name(teams[1].strip())
        neutral = False
        if {team0, team1} in NEUTRAL_SITE_MATCHUPS:
            neutral = True
        return {
            "home_team": team1,
            "away_team": team0,
            "neutral": neutral
        }
    else:
        return None

def convert_matchups(input_file, output_file):
    matchups = []
    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                matchup = parse_matchup(line)
                if matchup:
                    matchups.append(matchup)

    with open(output_file, 'w') as file:
        json.dump(matchups, file, indent=2)

if __name__ == "__main__":
    input_file = f"{DATA_BASE_DIRECTORY}/txt/schedule.txt"
    output_file = f"{DATA_BASE_DIRECTORY}/json/schedule.json"
    convert_matchups(input_file, output_file)
    print(f"Converted matchups from {input_file} to {output_file}")