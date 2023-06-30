from bs4 import BeautifulSoup
import re
import json

with open('cfb-lines-html-save.html', 'r') as infile:
    html_content = infile.read()

soup = BeautifulSoup(html_content, 'html.parser')
teams_table_div = soup.find_all('div', class_='content-sports-hierarchy')[0]
team_names = re.findall('title="(.+?)"', str(teams_table_div))

for i in range(len(team_names)):
    if team_names[i] == 'Texas A&amp;M':
        team_names[i] = 'Texas A&M'

with open('standardized-teamnames.json', 'w') as outfile:
    outfile.write(json.dumps(team_names))