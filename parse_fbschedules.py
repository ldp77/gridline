from bs4 import BeautifulSoup
import re
import common_utils
import json

DATA_BASE_DIRECTORY = '623-01'

def parse_td(td):
    soup_td = td
    td = str(td)
    matchup = re.findall('<span>(.+? [at|vs\.].+?)</span>', td)
    if matchup:
        matchup = matchup[0]
        neutral = 'neutral-site' in matchup
        if neutral:
            matchup = matchup.split('<span')[0]
        if ' at ' in matchup:
            away_home = matchup.split(' at ')
            away_team = away_home[0]
            home_team = away_home[1]
        elif ' vs. ' in matchup:
            away_home = matchup.split(' vs. ')
            away_team = away_home[0].strip()
            home_team = away_home[1].strip()

        matchup_dict = {
            'home_team': common_utils.standardize_name(home_team),
            'away_team': common_utils.standardize_name(away_team),
            'neutral': neutral
        }
        return matchup_dict
    return None




with open(f'{DATA_BASE_DIRECTORY}/html/fbschedules.html' , 'r') as infile:
    html_content = infile.read()
soup = BeautifulSoup(html_content, 'html.parser')

all_td = soup.find_all('td', class_='spring1')
all_matchups = []
for i in range(len(all_td)):
    matchup = parse_td(all_td[i])
    if matchup:
        all_matchups.append(matchup)

outfilename = f'{DATA_BASE_DIRECTORY}/json/schedule.json'
with open(outfilename, 'w') as outfile:
    outfile.write(json.dumps(all_matchups))
print(f'Saved {len(all_matchups)} matchups to {outfilename}')
    