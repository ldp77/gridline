# GridLine

This project seeks to provide an objective preview of the 2023 College Football season by extrapolating the maximum amount of information possible through analysis of preseason betting lines. 

Rather than making predictions, in this project, betting lines will be used to paint a probabilistic picture of the 2023 season. This picture will include a game by game breakdown of the schedule, the probability of each possible win total from 0-12, neutral field lines for hypothetical matchups across college football, and more for each team in the FBS.

A web interface is a work in progress, but for now, the report, which contains a breakdown for every FBS team can be found [here](fbs-reports.txt)

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