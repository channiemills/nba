# "Big Game" NBA Data

This project is born out of my _weathered_ relationship with the Chicago Bulls. They've had the reputation of only "showing up"
for big games for a few seasons now and after some motivation I decided to try my hand at putting data around the question of
how teams perform, based on their opponent's record.

So far it's just a modest data transformation effort, taking the game level data from [basketball reference](http://www.basketball-reference.com/leagues/NBA_2017_games.html)
and storing each game with a cumulative tally of wins, losses, and win percentage for each team. Naturally, it took longer than I anticipated.

## Initial Data

Basketball Reference is a fantastic source of hoops info. I couldn't find what I needed in the format I wanted but I found
all the pieces needed to make it happen. The first step was pulling down all the data for the 2016-17 NBA season in a CSV.

![init data](./screenshots/init-data.PNG?raw=true, "Initial Dataset")

## Transformation Steps

* Adding GameID column, column renaming, dropping unnecessary columns
* Adding columns for calculated data
  * Winner ```Winner```
  * Point Differential ```PT_Diff```
* Create restructured temporary data frame for home and away teams to combine into one master list
  * This included game level data (from source data) for each team
* Adding columns to temporary data frame for columns calculated by game by team
  * Whether it was a win or a loss ```W/L``` (Win = 1, Loss = 0)
* Combining home and away data frames into a single data frame containing two records (home and away team) for each game with some additional calculated fields.
  * Cumulative sum of wins ```Wins```
  * Cumulative sum of games played ```GP```
  * ```Opponent``` and ```Opponent_PCT```

## Analysis Ready Data

The resultant data frame contains data for all 1230 games played in the 2016-17 season. For each game, it retains the initial
information (date, time, home and away team, whether it went into overtime). It also includes the new data of the point differential,
and the critical points for this analysis:

* Record of both teams at that point in the season ```PCT```
* Outcome of that game for both teams, whether it was a win or loss ```W/L```

#### Final data showing the start of the season
![final data](./screenshots/res-data1v1.PNG?raw=true, "First ten rows of result")

#### Final data showing the end of the season
![final data](./screenshots/res-data2v2.PNG?raw=true, "Last ten rows of result")


_Developer Note_: The record ```PCT``` at each game is actually including that game, not going into that game. For analysis
may need to grab the ```PCT``` for both teams from the game before. This should be easy to grab using ```GameID```

## Sanity Check

#### Comparing basketball reference top 10 teams to top 10 teams returned from this data transformation.

Basketball Reference Top 10                                        | Resultant Top 10
:------------------------------------------------------------------|:------------------------------------------------------------:
![](./screenshots/bball_ref_top10.PNG?raw=true, "Bball Ref top 10")|![](./screenshots/script_top10.PNG?raw=true, "Outcome top 10")

_Note_: This script runs in about 15 seconds, compiling a season's worth of games.

### Clean Up Steps Still Needed

1. Clean up file structure
2. Unit tests
3. Coding style tests

### Analysis Steps Still Needed
1. Look for relationships between team performance and opponent performance
2. Attempt to fit (hidden) markov model to performance data for a team with the observation being W/L and the hidden state being opponent win pct.

### Installing

Nothing special needed for installation.

```
python 2.7
pandas
```

## Authors

* **channiemills** - *Initial work* - [channiemills](https://github.com/channiemills)


## Acknowledgments

* People that believe I can do anything