import pandas as pd
import common_utils
import json

DATA_BASE_DIRECTORY = '623-01'
df = pd.read_csv(f'{DATA_BASE_DIRECTORY}/csv/espn-fpi.csv')

# Create a mapping between a team's standardized name and their FPI
team_fpi = []
for i in range(len(df)):
    row = df.iloc[i]
    teamname = row['TEAM']
    fpi = row['FPI']

    teamname_split = teamname.split(' ')[:-1]
    for i in range(len(teamname_split)):
        tryname = ' '.join(teamname_split)
        if common_utils.standardize_name(tryname) in common_utils.TEAM_ALIASES.keys():
            teamname = common_utils.standardize_name(tryname)
            break
        teamname_split = teamname_split[:-1]

    team_fpi.append({
        'team_name': teamname,
        'fpi': fpi
    })

with open(f'{DATA_BASE_DIRECTORY}/json/fpi.json', 'w') as outfile:
    outfile.write(json.dumps(team_fpi))