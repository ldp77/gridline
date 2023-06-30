from bs4 import BeautifulSoup
import re
import statistics
import sortedcollections
import common_utils
import json

DATA_BASE_DIRECTORY = '623-01'

# infilenames = [
#     f'first-run/from_vegasinsider/week-{n}.html' for n in range(1,16)
# ]

infilenames = [
    f'{DATA_BASE_DIRECTORY}/html/vegasinsider-week-{n}.html' for n in range(1,16)
]

id_matchup_mapping = {}
team_line_mapping = {}
all_lines_found = []


def tr_parser(tr, class_):
    soup_tr = tr
    tr = str(tr)

    # Check for a game_id
    find_id = re.findall('data-event="ncaaf/(.+?)"', tr)
    game_id = find_id[0] if len(find_id) > 0 else None

    # Check for a team_name
    team_name_a = soup_tr.find_all('a', class_='team-name')
    if len(team_name_a) > 0:
        team_name_list = re.findall('aria-label="(.+?)"', str(team_name_a[0]))
        if len(team_name_list) > 0:
            team_name = team_name_list[0]
        else:
            team_name = None
    else:
        team_name = None


    # Check for lines
    dv_span = soup_tr.find_all('span', class_='data-value')
    line_values_found = []
    if len(dv_span) > 0:
        for dv in dv_span:
            lines_found = re.findall('<span class="data-value"> ([-\+]?\d+\.?\d?) </span>', str(dv))
            if len(lines_found) > 0:
                line_values = [float(line) for line in lines_found]
                line_values_found = line_values_found + line_values

    # Make possible updates
    # If we find a game_id, and a team name, we can update
    if game_id is not None and team_name is not None:
        if game_id not in id_matchup_mapping:
            id_matchup_mapping[game_id] = sortedcollections.OrderedSet()
        id_matchup_mapping[game_id].add(team_name)

    # If we find a team name and lines, we can update
    if team_name is not None and len(line_values_found) > 0:
        if team_name not in team_line_mapping:
            team_line_mapping[team_name] = []
        team_line_mapping[team_name] = team_line_mapping[team_name] + line_values_found


def build_line_from_sides(side1, side2):
    home_side = side1 if side1['source_class'] == 'footer' else side2
    away_side = side2 if side1['source_class'] == 'footer' else side1
    
    favorite = side1 if side1['line'] < 0 else side2
    line = abs(side1[line])

    return {
        'home_team': home_side['team_name'],
        'away_team': away_side['team_name'],
        'favorite': favorite['team_name'],
        'neutral': False, # Need to implement
        'line': line # Need to round
    }

for infilename in infilenames:
    with open(infilename, 'r') as infile:
        html_content = infile.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    all_divided = soup.find_all('tr', class_='divided')
    all_footer = soup.find_all('tr', class_='footer')

    for i in range(len(all_divided)):
        tr_parser(all_divided[i], 'divided')

    for i in range(len(all_footer)):
        tr_parser(all_footer[i], 'footer')

    matchups_to_process = {id: matchup for id, matchup in id_matchup_mapping.items() if len(matchup) == 2}
    # print(matchups_to_process)
    # print(team_line_mapping)
    lines_found = []
    for id, matchup in matchups_to_process.items():
        away_team = matchup[0]
        home_team = matchup[1]

        # Revisit this to see if we are letting lines go uncaptured
        if home_team not in team_line_mapping and away_team not in team_line_mapping:
            continue
        elif home_team in team_line_mapping:
            home_lines = team_line_mapping[home_team]
        else:
            away_lines = team_line_mapping[away_team]
            home_lines = -1 * away_lines
        home_line = statistics.median(home_lines)
        favorite = home_team if home_line < 0 else away_team

        line = abs(home_line)

        matchup = {common_utils.standardize_name(home_team), common_utils.standardize_name(away_team)}
        neutral = matchup in common_utils.NEUTRAL_SITE_MATCHUPS


        line_dict = {
            'home_team': common_utils.standardize_name(home_team),
            'away_team': common_utils.standardize_name(away_team),
            'favorite': common_utils.standardize_name(favorite),
            'line': common_utils.round_decimal_line(line),
            'neutral': neutral, 
            'game_id': id
        }
        lines_found.append(line_dict)
    all_lines_found = all_lines_found + lines_found

    # Reset for next input file
    id_matchup_mapping = {}
    team_line_mapping = {}

with open(f'{DATA_BASE_DIRECTORY}/json/vegasinsider.json', 'w') as outfile:
    outfile.write(json.dumps(all_lines_found))


    
       

    # Pair up all line sides by game id, and then calculate lines for all pairs
    # matching_sides = {}
    # for side in matchup_sides:
    #     if side['game_id'] not in matching_sides:
    #         matching_sides[side['game_id']] = []
    #     matching_sides[side['game_id']].append(side)

    # print(matching_sides)








# def parse_tr_divided(tr):
#     soup_tr = tr
#     tr = str(tr)
#     find_id = re.findall('data-event="ncaaf/(.+?)"', tr)
#     game_id = find_id[0] if len(find_id) > 0 else None

#     # find_team_name = re.findall('aria-label="(.+?)" class="team-name"', tr)
#     team_name_a = soup_tr.find_all('a', class_='team-name')
#     if len(team_name_a) > 0:
#         team_name_list = re.findall('aria-label="(.+?)"', str(team_name_a[0]))
#         if len(team_name_list) > 0:
#             team_name = team_name_list[0]
#         else:
#             team_name = None
#     else:
#         team_name = None

#     find_line_values = re.findall('<span class="data-value"> (-?\d+\.?\d?) </span>', tr)
#     if len(find_line_values) > 0:
#         for i in range(len(find_line_values)):
#             if find_line_values[i] == 'PK':
#                 find_line_values[i] = 0
#         line_values = [float(line) for line in find_line_values]
#         line_value = statistics.median(line_values)
#     else:
#         line_value = None

#     if not game_id:
#         return None
#     if not team_name:
#         return None
#     if not line_value:
#         return None
    
#     return {
#         'game_id': game_id,
#         'team_name': team_name,
#         'line': line_value,
#         'source_class': 'divided'
#     }

# def parse_tr_footer(tr):
#     soup_tr = tr
#     tr = str(tr)
#     find_id = re.findall('data-event="ncaaf/(.+?)"', tr)
#     game_id = find_id[0] if len(find_id) > 0 else None

#     team_name_a = soup_tr.find_all('a', class_='team-name')
#     if len(team_name_a) > 0:
#         team_name_list = re.findall('aria-label="(.+?)"', str(team_name_a[0]))
#         if len(team_name_list) > 0:
#             team_name = team_name_list[0]
#         else:
#             team_name = None
#     else:
#         team_name = None

#     find_line_values = re.findall('<span class="data-value"> (-?\d+\.?\d?) </span>', tr)
#     if len(find_line_values) > 0:
#         for i in range(len(find_line_values)):
#             if find_line_values[i] == 'PK':
#                 find_line_values[i] = 0
#         line_values = [float(line) for line in find_line_values]
#         line_value = statistics.median(line_values)
#     else:
#         line_value = None

#     if not game_id:
#         return None
#     if not team_name:
#         return None
#     if not line_value:
#         return None
    
#     return {
#         'game_id': game_id,
#         'team_name': team_name,
#         'line': line_value,
#         'source_class': 'footer'
#     }