from team_report import *
import common_utils

all_reports = ''
fbs_teams = list(common_utils.TEAM_ALIASES.keys())
for team in fbs_teams:
    print(team)
    report = TeamReport(team)
    all_reports += str(report)
    print(len(report.ranked_lines))

with open('fbs-reports.txt', 'w') as outfile:
    outfile.write(all_reports)
