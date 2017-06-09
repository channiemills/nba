"""
Look at NBA team performance based on opponent record.

Later can look at factors like back to back, weekend games, home or away etc

* Assumes main has been run. Perhaps we can pass pct as a variable in future...
"""


def vs500teams(df, team, type):
    teamdf = df[df['Team'] == team]
    if type == 'above':
        above500_wins = teamdf[teamdf.Opponent_PCT >= 0.500].sum()['W/L']
        above500_games = teamdf[teamdf.Opponent_PCT >= 0.500].count()['W/L']
        return above500_wins/above500_games
    elif type == 'below':
        below500_wins = teamdf[teamdf.Opponent_PCT < 0.500].sum()['W/L']
        below500_games = teamdf[teamdf.Opponent_PCT < 0.500].count()['W/L']
        return below500_wins/below500_games

