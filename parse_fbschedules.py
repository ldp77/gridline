from bs4 import BeautifulSoup
import re
import common_utils
import json

DATA_BASE_DIRECTORY = '824-01'

'''
def parse_td(td):
    soup_td = td
    td = str(td)
    matchup = re.findall(r'<span class="school-name-content">(.+?)</span>\s*<span>\s*(at|vs\.)\s*</span>\s*<span class="school-name-content">(.+?)</span>', td)
    if matchup:
        matchup = matchup[0]
        
        # TODO: Neutral site matchups
        # if ' at ' in matchup:
        #     away_home = matchup.split(' at ')
        #     away_team = away_home[0]
        #     home_team = away_home[1]
        # elif ' vs. ' in matchup:
        #     away_home = matchup.split(' vs. ')
        #     away_team = away_home[0].strip()
        #     home_team = away_home[1].strip()

        team1, vs_at, team2 = matchup
        if vs_at == 'at':
            home_team = team2
            away_team = team1
        else:
            home_team = team1
            away_team = team2

        matchup_dict = {
            'home_team': common_utils.standardize_name(home_team),
            'away_team': common_utils.standardize_name(away_team),
            'neutral': False
        }
        return matchup_dict
    return None
'''

def parse_td(td):
    teams = td.find_all('span', class_='school-name-content')
    teams = [team.get_text() for team in teams if 'team-rank' not in str(team)]

    if len(teams) != 2:
        return
    
    str_td = str(td)
    if ' at ' in str_td:
        away_team = teams[0]
        home_team = teams[1]
    elif ' vs ' in str_td:
        away_team = teams[1]
        home_team = teams[0]

    home_team = common_utils.standardize_name(home_team)
    away_team = common_utils.standardize_name(away_team)
    neutral = {home_team, away_team} in common_utils.NEUTRAL_SITE_MATCHUPS

    matchup_dict = {
            'home_team': home_team,
            'away_team': away_team,
            'neutral': neutral
        }
    return matchup_dict

all_matchups = []
for i in range(15):

    with open(f'{DATA_BASE_DIRECTORY}/html/fbschedules/week-{i}.html' , 'r') as infile:
        html_content = infile.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # all_td = soup.find_all('td', class_='spring1')
    all_td = soup.find_all('td', class_=re.compile(r'spring1'))
    for i in range(len(all_td)):
        matchup = parse_td(all_td[i])
        if matchup:
            all_matchups.append(matchup)

outfilename = f'{DATA_BASE_DIRECTORY}/json/schedule.json'
with open(outfilename, 'w') as outfile:
    outfile.write(json.dumps(all_matchups))
print(f'Saved {len(all_matchups)} matchups to {outfilename}')
    