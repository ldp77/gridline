from calc_engine import *
import pandas as pd
import json
import math

DATA_BASE_DIRECTORY = '824-01'

with open(f'{DATA_BASE_DIRECTORY}/json/fpi.json', 'r') as infile:
    team_fpi = json.loads(infile.read())

with open(f'{DATA_BASE_DIRECTORY}/json/schedule.json', 'r') as infile:
    global_schedule = json.loads(infile.read()) 

def determine_line(home_team, away_team, neutral=False):
    '''Get the line for a matchup based on the home_team and away_team factoring in neutral site.
    
    In contrast to calculate_line, this function should ALWAYS return a line.
    
    Looks first at calculated lines (direct and indirect), then at FPI if no line is available.'''
    home_team = common_utils.standardize_name(home_team)
    away_team = common_utils.standardize_name(away_team)
    first_try = calculate_line(home_team, away_team, neutral)
    if first_try:
        return first_try

    second_try = handle_no_line(home_team, away_team)
    if second_try:
        return adjust_line_for_location(home_team, away_team, neutral, second_try)



def handle_no_line(team1, team2):
    '''Return a neutral site line between 2 teams using the FPI'''
    fpis = [fpi for fpi in team_fpi if fpi['team_name'] in {team1, team2}]
    fpis = {fpi['team_name']: fpi['fpi'] for fpi in fpis}

    # Accounting for FCS teams
    # We don't currently have FPI data for FCS teams, so we assign an FPI of -17 to any FCS team
    # This is roughly equivalent to the worst FBS team
    if team1 not in fpis:
        fpis[team1] = -17
    if team2 not in fpis:
        fpis[team2] = -17

    favorite = team1 if fpis[team1] > fpis[team2] else team2
    line = abs(fpis[team1] - fpis[team2])
    neutral = True

    neutral_site_line = {
        'home_team': team1,
        'away_team': team2,
        'neutral': True,
        'line': common_utils.round_decimal_line(line),
        'favorite': favorite,
        'game_id': 'fpi'
    }
    return neutral_site_line


class TeamReport:
    def __init__(self, team_name):
        self.team_name = common_utils.standardize_name(team_name)
        self.schedule = self.get_schedule()
        self.lines = self.get_lines()
        self.favored = len([line for line in self.lines if line['favorite'] == self.team_name])
        self.underdog = len(self.lines) - self.favored
        self.win_probabilities = self.get_win_probabilities()
        self.expected_wins = sum(self.win_probabilities)
        self.win_total_probabilities = self.get_win_total_probabilities()
        self.ranked_lines = self.get_ranked_lines()

    def get_schedule(self):
        schedule = []
        for matchup in global_schedule:
            if matchup['home_team'] == self.team_name or matchup['away_team'] == self.team_name:
                schedule.append(matchup)
        return schedule
    
    def get_lines(self):
        lines = []
        for matchup in self.schedule:
            home_team = matchup['home_team']
            away_team = matchup['away_team']
            neutral = matchup['neutral']
            lines.append(determine_line(home_team, away_team, neutral))
        for line in lines:
            line['line'] = common_utils.round_decimal_line(line['line'])
        return lines
    
    def get_win_probabilities(self):
        win_probabilities = []
        for line in self.lines:
            favorite = line['favorite']
            favored_by = line['line'] if favorite == self.team_name else 0-line['line']
            win_prob = common_utils.convert_line_to_win_probability(favored_by)
            win_probabilities.append(win_prob)
        return win_probabilities
    
    def get_win_total_probabilities(self):
        all_scenarios = []
        probs = self.win_probabilities

        scenario = 0b000000000000
        while scenario <= 0b111111111111:
            scenario_probs = []
            scenario_wins = 0
            for i in range(12):
                win = bool((scenario & (1 << i)) >> i)
                if win:
                    scenario_wins += 1
                    scenario_probs.append(probs[i])
                else:
                    scenario_probs.append(1 - probs[i])
            all_scenarios.append((scenario_wins, math.prod(scenario_probs)))
            scenario += 1

        win_total_probs = {}
        for win_total, prob in all_scenarios:
            if win_total not in win_total_probs.keys():
                win_total_probs[win_total] = [prob]
            else:
                win_total_probs[win_total].append(prob)

        win_total_probs = {
            win_total: sum(probs)*100 for win_total, probs in win_total_probs.items()
        }
        return win_total_probs

    def get_ranked_lines(self):
        all_lines_query = f'home_team == "{self.team_name}" or away_team == "{self.team_name}"'
        all_lines = initial_lines_df.query(all_lines_query)

        favored = []
        underdog = []
        for i in range(len(all_lines)):
            line = dict(all_lines.iloc[i])
            opponent = line['home_team'] if line['home_team'] != self.team_name else line['away_team']
            line = adjust_line_for_location(self.team_name, opponent, True, line)
            if line['favorite'] == self.team_name:
                favored.append(line)
            else:
                underdog.append(line)

        all_ranked_lines = []
        for line in sorted(underdog, key=lambda x: 0-x['line']):
            all_ranked_lines.append(line)
        for line in sorted(favored, key=lambda x: x['line']):
            all_ranked_lines.append(line)

        return all_ranked_lines
    
    def __repr__(self):
        retval = ''
        retval += f'Team Name: {self.team_name}'
        retval += '\n\n'

        retval += f'Games Breakdown: \n'
        for i in range(len(self.schedule)):
            line = self.lines[i]
            opponent = line['away_team'] if self.team_name == line['home_team'] else line['home_team']
            win_prob = self.win_probabilities[i]
            location_string = ''
            if line['neutral']:
                location_string = 'N'
            elif self.team_name == line['home_team']:
                location_string = 'vs'
            else:
                location_string = '@'
            retval += f'{location_string} {opponent} : {line["favorite"]} Favored by {line["line"]} : Win Pct: {(win_prob*100):.3f}\n'

        retval += '\n'
        retval += f'Favored in {self.favored} games \n'
        retval += f'Underdog in {self.underdog} games \n'

        retval += '\n'
        retval += f'Expected Wins: {self.expected_wins:.3f}\n'
        
        retval += '\n'
        retval += f'Pct Chance of Each Possible Win Total:\n'
        for num_wins, probability in self.win_total_probabilities.items():
            retval += f'{num_wins} : {probability:.3f}% \n'

        retval += '\n'
        retval += 'On a Neutral Field: \n'
        for line in self.ranked_lines:
            if line['favorite'] == self.team_name:
                opponent = line['home_team'] if line['home_team'] != self.team_name else line['away_team']
                retval += f'{self.team_name} -{common_utils.round_decimal_line(line["line"])} vs {opponent}\n'
            else:
                retval += f'{line["favorite"]} -{common_utils.round_decimal_line(line["line"])} vs {self.team_name}\n'
        retval += '\n\n'

        return retval