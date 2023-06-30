'''
This parser is meant to act as a translation layer between the HTML content scraped from draftkings,
and the calculation engine.

It is responsible for parsing the HTML content from the input file (ex. draftkings.html which has 
already been scraped by the draftkings scraper).

As it parses the HTML data, it keeps track of the lines it finds and when the whole file has been 
processed, it saves these lines as json data which the calculation engine is able to use.

The calculation engine assumes standardized team names and rounded lines, so the parser is responsible 
for these tasks as well.

TODO: Use a command line argument to specify an output file or directory

'''
#***************************************************************************************************
import requests
import re
import json
from bs4 import BeautifulSoup
import common_utils

DATA_BASE_DIRECTORY = '623-01'

class MatchupSide:
    '''
    Basic data structure to hold information about one side of a matchup.
    '''
    def __init__(self, game_id, team_name, line, source_idx):
        self.game_id = game_id
        self.team_name = common_utils.standardize_name(team_name)
        self.line = line
        self.source_idx = source_idx

    def __repr__(self):
        return f'game_id={self.game_id}, team_name={self.team_name}, line={self.line}'

def parse_table_record(tr, source_idx):
    # Not all tr we find will correspond to a line, so filter them out
    if 'sportsbook-outcome-cell__body' not in str(tr):
        return None
    
    # find relevant information
    relevant_div = tr.find('div', class_='sportsbook-outcome-cell__body')

    line_text = re.findall('aria-label="(.+?)"', str(relevant_div))
    if len(line_text) > 0:
        line_text = line_text[0]
        line_text_split = line_text.split()
        team_name = ' '.join(line_text_split[:-1])
        line = line_text_split[-1]

    id_text = re.findall('"eventId":"(.+?)"', str(relevant_div))[0]

    return MatchupSide(
        game_id=id_text,
        team_name=team_name,
        line=line,
        source_idx=source_idx
    )

class GameLine:
    def __init__(self, side_home, side_away, neutral=False):
        self.home_team = common_utils.standardize_name(side_home.team_name)
        self.away_team = common_utils.standardize_name(side_away.team_name)
        self.game_id = side_home.game_id
        self.favorite = common_utils.standardize_name(self.home_team if float(side_home.line) < 0 else self.away_team)
        self.line = common_utils.round_decimal_line(abs(float(side_home.line)))

        self.neutral = {self.home_team, self.away_team} in common_utils.NEUTRAL_SITE_MATCHUPS

    def __repr__(self):
        return f'game_id={self.game_id}, home_team={self.home_team}, away_team={self.away_team}, favorite={self.favorite}, line={self.line}'
    
    def __dict__(self):
        return {
            'home_team': self.home_team,
            'away_team': self.away_team,
            'game_id': self.game_id,
            'favorite': self.favorite,
            'line': self.line,
            'neutral': self.neutral
        }

def process_matchup_sides(matchup_sides):
    # Pair matchup sides up by game id
    paired_sides = {
        game_id: [] for game_id in set([side.game_id for side in matchup_sides])
    }

    for side in matchup_sides:
        paired_sides[side.game_id].append(side)

    game_lines_list = []

    for game_id, side_list in paired_sides.items():
        side1, side2 = side_list[0], side_list[1]
        is_side1_home = side1.source_idx > side2.source_idx

        side_home = side1 if is_side1_home else side2
        side_away = side2 if is_side1_home else side1

        # Will need an external reference for neutral site games

        gl = GameLine(side_home, side_away)
        game_lines_list.append(gl)

    return game_lines_list

infilename = f'{DATA_BASE_DIRECTORY}/html/draftkings.html'
with open(infilename, 'r') as infile:
    html_content = infile.read()

soup = BeautifulSoup(html_content, 'html.parser')
sportsbook_tables = soup.find_all('table', class_='sportsbook-table')

all_tr = []
for table in sportsbook_tables:
    trs_found = table.find_all('tr')
    all_tr = all_tr + trs_found

all_matchup_sides = []

# Home team is listed second, so crude solution to identifying the home team is
# Keep track of the order that the teams come in, we can use this when constructing the line object
source_idx = 0
for tr in all_tr:
    ms = parse_table_record(tr, source_idx)
    if ms is not None:
        all_matchup_sides.append(ms)
    source_idx += 1

all_game_lines = process_matchup_sides(all_matchup_sides)
# for line in all_game_lines:
#     print(line)

with open(f'{DATA_BASE_DIRECTORY}/json/draftkings.json', 'w') as outfile:
    outfile.write(json.dumps([gl.__dict__() for gl in all_game_lines]))