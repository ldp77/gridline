import json
import pandas as pd
import common_utils

HOME_FIELD_ADVANTAGE = 3
DATA_BASE_DIRECTORY = '824-02'
DEBUG = False

# Specify the files (in order) to read lines from
# Once a line for a matchup is found in one of these files, it will not be updated if found in a later file
infilenames = [
    'draftkings.json',
    # 'vegasinsider.json'
]
infilenames += [f'indirectlines-{n}.json' for n in range(1,9)]
infilenames = [f'{DATA_BASE_DIRECTORY}/json/{filename}' for filename in infilenames]

all_game_lines = []
known_matchups = set()
for infilename in infilenames:
    with open(infilename, 'r') as infile:
        game_lines = json.loads(infile.read())
    new_game_lines = []
    for line in game_lines:
        matchup_id = common_utils.get_id_for_matchup(line['home_team'], line['away_team'])
        if matchup_id not in known_matchups:
            known_matchups.add(matchup_id)
            new_game_lines.append(line)
    all_game_lines = all_game_lines + new_game_lines
initial_lines_df = pd.DataFrame(all_game_lines)

def lines_df_from_input_files_list(infilenames):
    all_game_lines = []
    known_matchups = set()
    for infilename in infilenames:
        with open(infilename, 'r') as infile:
            game_lines = json.loads(infile.read())
        new_game_lines = []
        for line in game_lines:
            matchup_id = common_utils.get_id_for_matchup(line['home_team'], line['away_team'])
            if matchup_id not in known_matchups:
                known_matchups.add(matchup_id)
                new_game_lines.append(line)
        all_game_lines = all_game_lines + new_game_lines

    return pd.DataFrame(all_game_lines)

def adjust_line_for_location(desired_home_team, desired_away_team, desired_neutral, game_line_dict):
    '''
    Used to adjust a line for home field advantage. For example,

        Texas A&M is a 6.5 point favorite @Miami, but we want to know the line of that matchup on a neutral field.
        In this line, Miami is given 3 points as the home team. On a neutral field those would be taken away.
        In this case the line is Texas A&M -9.5

        OR

        Texas A&M is a 3.5 point underdog @Ole Miss, but we want to know the line if Texas A&M was at home.
        Ole Miss would no longer be the home team, so the line goes down to Ole Miss -0.5 on a neutral field.
        If Texas A&M got 3 points for home field advantage, the line would become Texas A&M -2.5

    (for now) Returns a dictionary with all attributes making up the game line
    '''

    old_line = game_line_dict['line']
    old_favorite = game_line_dict['favorite']
    old_neutral = game_line_dict['neutral']
    old_home_team = game_line_dict['home_team']
    old_away_team = game_line_dict['away_team']

    # If both scenarios are neutral site, it doesn't matter who is home/away, no point adjustment needed
    if old_neutral and desired_neutral:
        return game_line_dict
    
    # If the home team, away team, and neutral site are all the same, no point adjustment needed
    if all([old_home_team == desired_home_team, old_away_team == desired_away_team, old_neutral == desired_neutral]):
        return game_line_dict
    
    if old_neutral == False and desired_neutral == True:
        
        # Away team should receive 3 points
        adjustment_direction = 1 if old_away_team == old_favorite else -1
        
        new_line = old_line + adjustment_direction * HOME_FIELD_ADVANTAGE
        if new_line < 0:
            new_line = abs(new_line)
            new_favorite = old_home_team if old_favorite == old_away_team else old_away_team
        else:
            new_favorite = old_favorite

        return {
            'home_team': desired_home_team,
            'away_team': desired_away_team,
            'line': new_line,
            'favorite': new_favorite,
            'neutral': desired_neutral,
            'game_id': game_line_dict['game_id']
        }

    if old_neutral == True and desired_neutral == False:
        
        # Home team should receive 3 points
        adjustment_direction = 1 if desired_home_team == old_favorite else -1

        new_line = old_line + adjustment_direction * HOME_FIELD_ADVANTAGE
        if new_line < 0:
            new_line = abs(new_line)
            new_favorite = old_home_team if old_favorite == old_away_team else old_away_team
        else:
            new_favorite = old_favorite

        return {
            'home_team': desired_home_team,
            'away_team': desired_away_team,
            'line': new_line,
            'favorite': new_favorite,
            'neutral': desired_neutral,
            'game_id': game_line_dict['game_id']
        }

    if old_home_team == desired_away_team and old_away_team == desired_home_team:
        
        # New home team should receive 6 points
        adjustment_direction = 1 if desired_home_team == old_favorite else -1

        new_line = old_line + adjustment_direction * HOME_FIELD_ADVANTAGE * 2
        if new_line < 0:
            new_line = abs(new_line)
            new_favorite = old_home_team if old_favorite == old_away_team else old_away_team
        else:
            new_favorite = old_favorite

        return {
            'home_team': desired_home_team,
            'away_team': desired_away_team,
            'line': new_line,
            'favorite': new_favorite,
            'neutral': desired_neutral,
            'game_id': game_line_dict['game_id']
        }

    print(f'Uncovered case {desired_home_team} {desired_away_team} {desired_neutral} {game_line_dict}')
    return None

# First Goal: Calculate a line when possible between two teams
def calculate_line(home_team, away_team, neutral=False, lines_df=initial_lines_df):
    
    # Case 1: There is a line in our dataframe for this matchup
    direct_line_query = f'(home_team == "{home_team}" and away_team == "{away_team}") or (home_team == "{away_team}" and away_team == "{home_team}")'
    if DEBUG:
        print(f'Running direct_line_query: {direct_line_query}')
    
    direct_line_query_result = lines_df.query(direct_line_query)
    if DEBUG:
        print(f'direct_line_query found results {direct_line_query_result}')
    
    
    if len(direct_line_query_result) > 0:
        game_line_dict = dict(direct_line_query_result.iloc[0])

        if DEBUG:
            print(f'Found direct line {game_line_dict}')

        return adjust_line_for_location(home_team, away_team, neutral, game_line_dict)

    # Case 2: There is no line for this matchup, but we can calculate one based on one or more common opponents
    common_opponents_query = f'home_team == "{home_team}" or home_team == "{away_team}" or away_team == "{home_team}" or away_team == "{away_team}"'
    common_opponents_query_result = lines_df.query(common_opponents_query)

    if DEBUG:
        print(f'common_opponents_query_result {common_opponents_query_result}')
    
    # Get a set of common opponents
    involved_teams = [home_team, away_team]
    listed_matchups = {team: set() for team in involved_teams}
    for i in range(len(common_opponents_query_result)):
        game_line_dict = dict(common_opponents_query_result.iloc[i])

        if game_line_dict['home_team'] in involved_teams:
            listed_matchups[home_team].add(game_line_dict['away_team'])
        else:
            listed_matchups[away_team].add(game_line_dict['home_team'])
    common_opponents = listed_matchups[home_team].intersection(listed_matchups[away_team])

    if DEBUG:
        print(f'common_opponents {common_opponents}')

    if len(common_opponents) > 0:
        # For each common opponent, first adjust the lines to a neutral field, then compare these neutral field lines
        delta_nf_lines = []
        for co in common_opponents:
            home_team_line_dict = dict(common_opponents_query_result.query(
                f'(home_team == "{home_team}" and away_team == "{co}") or (home_team == "{co}" and away_team == "{home_team}")'
            ).iloc[0])
            away_team_line_dict = dict(common_opponents_query_result.query(
                f'(home_team == "{away_team}" and away_team == "{co}") or (home_team == "{co}" and away_team == "{away_team}")'
            ).iloc[0])

            home_team_neutral_line = adjust_line_for_location(home_team, co, True, home_team_line_dict)
            away_team_neutral_line = adjust_line_for_location(away_team, co, True, away_team_line_dict)

            if DEBUG:
                print(f'home_team_neutral_line {home_team_neutral_line}')
                print(f'away_team_neutral_line {away_team_neutral_line}')

            # For this common opponent, compare the home_team vs co on a neutral field to the away_team vs co on a neutral field
            # This discrepancy is counted as the line between home and away on a neutral field

            if home_team_neutral_line['favorite'] in involved_teams and away_team_neutral_line['favorite'] in involved_teams:
                home_team_favored_by = home_team_neutral_line['line'] - away_team_neutral_line['line']
            elif home_team_neutral_line['favorite'] not in involved_teams and away_team_neutral_line['favorite'] not in involved_teams:
                home_team_favored_by = home_team_neutral_line['line'] - away_team_neutral_line['line']
                if home_team_favored_by > 0 and home_team_neutral_line['line'] > away_team_neutral_line['line']:
                    home_team_favored_by = 0 - home_team_favored_by
                elif home_team_favored_by < 0 and home_team_neutral_line['line'] < away_team_neutral_line['line']:
                    home_team_favored_by = 0 - home_team_favored_by
            else:
                home_team_favored_by = home_team_neutral_line['line'] + away_team_neutral_line['line']
                # Only have accounted for the magnitude of the line, need to account for the direction
                if home_team_neutral_line['favorite'] not in involved_teams:
                    home_team_favored_by = 0 - home_team_favored_by

            if DEBUG:
                print(f'home_team_favored_by {home_team_favored_by}')
            
            delta_nf_lines.append(home_team_favored_by)

        if DEBUG:
            print(f'delta_nf_lines {delta_nf_lines}')

        home_team_favored_by = sum(delta_nf_lines) / len(delta_nf_lines)
        favorite = home_team if home_team_favored_by >= 0 else away_team
        line = abs(home_team_favored_by)

        neutral_field_line = {
            'home_team': home_team,
            'away_team': away_team,
            'line': line,
            'favorite': favorite,
            'neutral': True,
            'game_id': 'indirect'
        }

        return adjust_line_for_location(home_team, away_team, neutral, neutral_field_line)

    # Case 3: We have insufficient data to calculate a line for this matchup

    return None
