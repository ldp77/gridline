# GridLine

This project seeks to provide an objective preview of the 2023 College Football season by extrapolating the maximum amount of information possible through analysis of preseason betting lines. 

Rather than making predictions, in this project, betting lines will be used to paint a probabilistic picture of the 2023 season. This picture will include a game by game breakdown of a team's schedule, the probability of each possible win total from 0-12 for that team, hypothetical point spreads for matchups against opponents across college football, and more for each team in the FBS.

Here's an example:
```
Team Name: Texas A&M

Games Breakdown: 
vs New Mexico : Texas A&M Favored by 39.5 : Win Pct: 99.000
@ Miami (FL) : Texas A&M Favored by 6.5 : Win Pct: 67.700
vs Louisiana-Monroe : Texas A&M Favored by 31.0 : Win Pct: 99.000
vs Auburn : Texas A&M Favored by 8.0 : Win Pct: 73.800
N Arkansas : Texas A&M Favored by 3.0 : Win Pct: 57.400
vs Alabama : Alabama Favored by 8.5 : Win Pct: 25.400
@ Tennessee : Tennessee Favored by 8.5 : Win Pct: 25.400
vs South Carolina : Texas A&M Favored by 7.5 : Win Pct: 73.000
@ Ole Miss : Ole Miss Favored by 3.5 : Win Pct: 39.400
vs Mississippi State : Texas A&M Favored by 7.0 : Win Pct: 70.300
vs Abilene Christian : Texas A&M Favored by 32.5 : Win Pct: 99.000
@ LSU : LSU Favored by 10.5 : Win Pct: 20.700

Favored in 8 games 
Underdog in 4 games 

Expected Wins: 7.501

Pct Chance of Each Possible Win Total:
0 : 0.000% 
1 : 0.000% 
2 : 0.003% 
3 : 0.106% 
4 : 1.132% 
5 : 5.691% 
6 : 16.000% 
7 : 26.805% 
8 : 27.141% 
9 : 16.367% 
10 : 5.656% 
11 : 1.025% 
12 : 0.075% 

On a Neutral Field: 
Georgia -17.0 vs Texas A&M
Ohio State -13.0 vs Texas A&M
Michigan -12.5 vs Texas A&M
Alabama -11.5 vs Texas A&M
LSU -7.5 vs Texas A&M
Texas -7.5 vs Texas A&M
Tennessee -5.5 vs Texas A&M
Penn State -5.5 vs Texas A&M
Florida State -4.5 vs Texas A&M
Clemson -4.5 vs Texas A&M
USC -4.5 vs Texas A&M
Oregon -3.0 vs Texas A&M
Notre Dame -2.0 vs Texas A&M
Oklahoma -1.5 vs Texas A&M
Kansas State -1.0 vs Texas A&M
Washington -1.0 vs Texas A&M
Utah -0.5 vs Texas A&M
Ole Miss -0.5 vs Texas A&M
Wisconsin -0.0 vs Texas A&M
Texas A&M -1.5 vs TCU
Texas A&M -1.5 vs Oregon State
Texas A&M -2.0 vs Texas Tech
Texas A&M -3.0 vs Arkansas
Texas A&M -3.5 vs Iowa
Texas A&M -3.5 vs Baylor
Texas A&M -3.5 vs North Carolina
Texas A&M -4.0 vs UCLA
Texas A&M -4.0 vs Mississippi State
Texas A&M -4.5 vs Minnesota
Texas A&M -4.5 vs South Carolina
Texas A&M -5.0 vs Auburn
Texas A&M -5.0 vs Florida
Texas A&M -5.0 vs Iowa State
Texas A&M -7.0 vs Kansas
Texas A&M -8.5 vs Michigan State
Texas A&M -8.5 vs Boise State
Texas A&M -8.5 vs Nebraska
Texas A&M -9.0 vs North Carolina State
Texas A&M -9.5 vs Miami (FL)
Texas A&M -9.5 vs Oklahoma State
Texas A&M -9.5 vs Pittsburgh
Texas A&M -10.0 vs Tulane
Texas A&M -10.0 vs Duke
Texas A&M -12.0 vs Arizona State
Texas A&M -14.0 vs South Alabama
Texas A&M -14.5 vs West Virginia
Texas A&M -17.5 vs Colorado
Texas A&M -17.5 vs Coastal Carolina
Texas A&M -18.0 vs Navy
Texas A&M -18.5 vs Indiana
Texas A&M -19.0 vs Wyoming
Texas A&M -21.5 vs Utah State
Texas A&M -21.5 vs East Carolina
Texas A&M -22.0 vs San Jose State
Texas A&M -22.5 vs Virginia
Texas A&M -22.5 vs Central Michigan
Texas A&M -23.5 vs Middle Tennessee
Texas A&M -23.5 vs Miami (OH)
Texas A&M -24.0 vs Rice
Texas A&M -24.5 vs Buffalo
Texas A&M -26.0 vs Texas State
Texas A&M -28.5 vs UConn
Texas A&M -29.0 vs Arkansas State
Texas A&M -30.0 vs Nevada
Texas A&M -36.0 vs New Mexico State
Texas A&M -36.5 vs New Mexico
Texas A&M -41.5 vs UMass
```

A web interface is a work in progress, but for now, the full report, which contains a breakdown for every FBS team can be found [here](fbs-reports.txt) (ctrl+F, followed by searching for "Team Name: <...>" highly recommended)

## Table of Contents

1. Introduction
2. The Model
3. Technical Implementation

# Context

The basic idea behind this project is that betting lines listed by sportsbooks provide a well researched and unbiased view of the difference in strength between two teams, with the reasoning that if oddsmakers were inaccurate on average, then people could win money from the sportsbook by exploiting that inaccuracy (which does not happen).

> __Point Spread:__ A number of points, determined by oddsmakers, by which the favorite is projected to beat the underdog. Indicates the difference in strength between the two teams.
> 
> Example: Texas A&M is a 3 point favorite against Arkansas, the point spread is 3, and oddsmakers would list this as "Arkansas +3 vs. Texas A&M" (or equivalently "Texas A&M -3 vs Arkansas")

This project uses point spreads that have been listed ahead of the upcoming season to create what should be an accurate and unbiased forecast of how each team could perform this year.

# The Model

Sportsbooks have published lines for quite a few games for the upcoming season (126 as of June), but they have not listed lines for every game. The published lines are a good start for analysis, but there is a way to get even more reliable lines to analyze. 

If we have two point spreads involving a common opponent, let's say Georgia -10 vs LSU and LSU -2 vs Florida State, then we can apply the transitive property and say that Georgia would be about a 12 point favorite over Florida State.

> Note: The transitive property is famously ineffective when applied to __outcomes of games__ in sports. But Point spreads are not outcomes of games, they are estimates in the difference in relative strength between two teams. The transitive property works much better here

> Note: In point spreads for actual games, home field advantage is a factor, and the actual model takes this into account. For the sake of simplicity, the given example assumes all neutral site games

**Using this idea, the number of lines available for analysis increased from 126 to 2296.**

# Implementation

The technical implementation involved numerous components intended to accomplish necessary tasks such as:

### Scraping Data from the Internet

- The point spreads for the project came from 2 sources: [Draftkings Sportsbook](https://sportsbook.draftkings.com/leagues/football/ncaaf) and [VegasInsider](https://www.vegasinsider.com/college-football/odds/las-vegas/)
- Data on the 2023 season schedule was scraped from [FBSchedules](https://fbschedules.com/)

Data from these sources was saved as HTML

- Data from the [ESPN FPI](https://www.espn.com/college-football/fpi) was used for the subset of games for which no line could be calculated (saved as CSV)

### Parsing the HTML data

For each source of HTML data, there is a Python script to parse the data and extract all of the desired data type therein (either point spread or matchup on schedule). Once all of the parsing is done, the data is saved as JSON

### Performing Calculations

The calculation engine reads the JSON data and creates a pandas DataFrame of all known point spreads.

This is then used to calculate all possible transitive lines. New transitive lines are saved as JSON and fed back into the calculation engine, and so on until all possible lines have been calculated from the original set of lines.

### Generating Team Reports

Referring to the known set of lines, the schedule, and the FPI as needed, calculates a report (via a Python class) containing the following information:

- Team Name
- Game by Game breakdown of the team's schedule: Calculated point spread, and team's probability to win
- Number of games in which the team is favored, and number in which they are the underdog
- Statistically expected number of wins
- Percent chance of each possible win total from 0-12
- List of all lines that could be calculated for that team, adjusted to a neutral field