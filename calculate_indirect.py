from calc_engine import *
import itertools
import hashlib
import common_utils

SAVE_INDIRECT_LINES = True
BASE_DIRECTORY = "623-01/json"

# Initialize the table to keep track of known lines
all_team_names = set(list(initial_lines_df['home_team']) + list(initial_lines_df['away_team']))
all_possible_matchups = [(tm1, tm2) for tm1, tm2 in itertools.product(all_team_names, all_team_names) if tm1 != tm2]

known_lines = set()

# Have to store the lines from the initial df as known so we don't save over them
for i in range(len(initial_lines_df)):
    row = initial_lines_df.iloc[i]
    known_lines.add(common_utils.get_id_for_matchup(row['home_team'], row['away_team']))

# Iterative process whereby we calculate any new lines that we can, then incorporate these new lines during the next iteration
n = 1
current_lines_df = initial_lines_df
while True: # For now, go forever, but eventually will change this
    print(f'Iteration {n}')

    new_lines = []
    for tm1, tm2 in all_possible_matchups:
        matchup_id = common_utils.get_id_for_matchup(tm1, tm2)
        if matchup_id not in known_lines:
            line = calculate_line(tm1, tm2, neutral=True, lines_df=current_lines_df)
            if line:
                new_lines.append(line)
                known_lines.add(matchup_id)

    print(f'Found {len(new_lines)} new lines')

    if SAVE_INDIRECT_LINES:
        outfilename = f'{BASE_DIRECTORY}/indirectlines-{n}.json'
        try:
            with open(outfilename, 'w') as outfile:
                outfile.write(json.dumps(new_lines))
        except TypeError:
            for line in new_lines:
                line['neutral'] = bool(line['neutral'])
            with open(outfilename, 'w') as outfile:
                outfile.write(json.dumps(new_lines))
        print(f'Saved to file {outfilename}')
        infilenames.append(outfilename)

    current_lines_df = lines_df_from_input_files_list(infilenames)
    n += 1