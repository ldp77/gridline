# GridLine

This project seeks to provide an objective preview of the 2023 College Football season by extrapolating the maximum amount of information possible through analysis of preseason betting lines. 

## Table of Contents

1. [Introduction](#introduction)
2. [The Model](#themodel)

# Introduction <a id="introduction"></a>

## Why Point Spreads?

This project is based on the idea that a point spread provides unbiased, thoroughly researched insight into the difference in relative strength between two college football teams. 

> __Point Spread:__ A bet on the margin of victory in a sporting event.
> 
> For example, "Texas A&M (-6.5) @ Miami" is a point spread which means that Texas A&M is favored by 6.5 points. "Texas A&M @ Miami (+6.5)" means the same thing.
> 
> Oddsmakers set the value of the point spread such that each team has an equal likelihood to "cover the spread", which means "win after the point spread is factored in."
> 
> In other words, Given the final score of a game, the value of the point spread is subtracted from the winning team's score, and the team that has more points after that subtraction is the team that covered the spread.
> 
> Ex. If Texas A&M beat Miami 30-21, since the point spread was Texas A&M -6.5, Texas A&M covers the spread because they have more points even after the 6.5 was subtracted from their score.

Sportsbooks are strongly incentivized to ensure their point spreads are as precise as possible, because inaccurate point spreads would enable people to bet on one side of the point spread and win money from the sportsbook. Because of this incentive, sportsbooks invest a tremendous amount of resources into machine learning models, consultants, and potentially insider information in order to ensure that they are able to generate the most precise line possible for a game. 

As most sportsbooks are very successful financial enterprises, we can see that, while not perfect for every matchup, point spreads are very strong indicators (I would argue the strongest indicators available short of a crystal ball) of the difference between the strength of two teams. 

## What Else Can Point Spreads Tell Us?

As stated above, point spreads indicate the predicted margin of victory for a given matchup. This is useful in and of itself for someone who wants an objective view of each team's chances to win the game, whether the game is likely to be close, etc. But it there is more information that point spreads can tell us, especially when we have access to a large number of them. 

First, point spreads are strongly correlated to a team's win probability. This should stand to reason, as a team who is favored by a large margin has a high probability to win the game, and a team favored by a narrow margin has a win probability of slightly over 50%. [This article](https://www.boydsbets.com/college-football-spread-to-moneyline-conversion/) provides a table which maps the value of a point spread to both the favorite's and the underdog's win probability. 

Now, instead of simply a predicted margin of victory, a point spread can indicate win probability as well.

Having the point spread and win probability for one game is good, but having this information for many games is better, as then you can start to analyze things like (to name a few):
- The expected number of wins for each team
- The number of games on a team's schedule in which they are favored, and the number in which they are the underdog
- The probability of a team winning N games for all possible values of N

And to reiterate, there are many models that seek to predict exactly this information. The difference here is the use of published point spreads, which are by their nature effective at being accurate and unbiased.

# The Model <a id="themodel"></a>

## Indirect / Transitive Lines

As of June 2023, there are preseason lines for 126 matchups that will take place this season. This means that for 126 games, we have access to the relative difference in strength between two teams, months before the season is set to begin. While this is powerful in and of itself, we can do a lot more with some knowledge about point spreads, and some basic math.

Let’s say I want to know the point spread for the Texas A&M vs. Mississippi State game. I look it up, but there is no point spread published for this game right now. However, there is a line published for Texas A&M vs. Ole Miss, and a line for Ole Miss vs. Mississippi State. Since a point spread is a measure the difference between relative strength between two teams, we can apply the transitive property to calculate the line between A&M and MSU. 

We’ll take the two published lines:
> Texas A&M +3.5 @ Ole Miss (Texas A&M is a 3.5 point underdog on the road vs Ole Miss)
> 
> Mississippi State +1.5 vs Ole Miss (MSU is a 1.5 point underdog at home vs Ole Miss)

Now we have to adjust for home field advantage. Oddsmakers factor in the location of the matchup because the team playing on their home field is thought to have an advantage. In college football, 3 points is often used as a good general estimate for the value of home field advantage in a point spread.

> Note: because of home field advantage, when you hear analysis of how two teams compare to each other, it is often phrased something like “This team would be favored over that team by (some amount) on a neutral field.” The point of this is to factor out any home field advantage and purely assess the two teams relative strengths against each other

So when we want to calculate the line between Texas A&M and Mississippi State, we first need to adjust the published lines to represent a neutral field. 

Texas A&M is a 3.5 point underdog on the road vs Ole Miss. If this game were moved to a neutral site, Ole Miss (formerly the home team) would lose home field advantage (3 points), so the new line would be:

Texas A&M +0.5 N Ole Miss

Applying the same logic to the other line, Mississippi State would lose home field advantage against Ole Miss, meaning their new line would be:

Mississippi State +4.5 N Ole Miss

We can now take the difference, and calculate that, on a neutral field, Texas A&M would be favored by 4 points against Mississippi State. 
Finally, we can circle all the way back to the upcoming season’s schedule, when Texas A&M will be the home team for their matchup vs Mississippi State. Texas A&M will gain home field advantage, so we can predict a line of

Texas A&M -7 vs Mississippi State.

The ability to calculate this line is powerful, as now we have an assessment of Texas A&M’s relative strength vs Mississippi State, based entirely on published point spreads, which we didn’t have before. With this approach we were able to take the initial 126 lines and calculate 131 additional lines. 

However, to calculate this line, we needed the two teams to have a common opponent (Ole Miss). Not all matchups had such a common opponent to use as a basis for this calculation. But after calculating the 131 new lines, there are now many more point spreads to consider when looking for common opponents. We can incorporate both the 126 original lines and the 131 new lines, and perform the calculation again to generate even more, and so on and so on. 

**In all, we took 126 original lines and calculated 2292 lines that are based only on published point spreads, and the above calculation using common opponents.**
