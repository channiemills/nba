"""
Look at NBA team performance based on opponent record.

Later can look at factors like back to back, weekend games, home or away etc

* Assumes main has been run
"""


def vs500teams(df, team, type):
    teamdf = df[df['Team'] == team]
    if type == 'above':
        above500_wins = teamdf[teamdf.Opponent_PCT >= 0.500].sum()['W/L']
        above500_games = teamdf[teamdf.Opponent_PCT >= 0.500].count()['W/L']
        return round(above500_wins/above500_games, 3)
    elif type == 'below':
        below500_wins = teamdf[teamdf.Opponent_PCT < 0.500].sum()['W/L']
        below500_games = teamdf[teamdf.Opponent_PCT < 0.500].count()['W/L']
        return round(below500_wins/below500_games, 3)

