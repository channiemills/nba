### 1.0.1
* Add columns to each game for opponent and opponent record
* Rounds record percentages to three decimal places
* Adjust PCT columns to reflect record going into the game
  * Look for better ways to do this
  * Adjusted imprecision with opponent score not matching team score for same GameID
    * Resolved issue with W/L only calculated for team in Team column, never shows opponent as winner
* Calculate team's average score against below and above .500 teams
  * Discovered initial assumption about Bulls was incorrect
  * Discovered record above and below 0.500 calculated online is based on end of season record and not record at that game
* Moved functions into module to simplify main.py


### 1.0.0
* Returns all 82 games for each team in 2016-17 season.
* Two records for each game, home team and away team
* Calculates record for each team throughout the season