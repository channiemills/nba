"""
Functions needed to transform source data from basketball reference.
"""

import pandas as pd

def column_transforms(source):
    """
    Performs column transformations on basketball reference columns
    :param source: Data frame of game data from bball ref
    :return: Data frame with transformed columns
    """
    # Order by game date, time
    source['Date'] = pd.to_datetime(source['Date'])
    source['Start (ET)'] = pd.to_datetime(source['Start (ET)'], format='%I:%M %p').dt.time
    source.sort_values(['Date', 'Start (ET)'], ascending=[1, 1], inplace=True)

    # Add GameID column to the beginning
    source.insert(0, 'GameID', range(1, len(source['Date'])+1))

    # Rename Columns
    source = source.rename(columns={
        'Visitor/Neutral': 'Away',
        'Home/Neutral': 'Home',
        'Unnamed: 7': 'Overtime',
        'Start (ET)': 'Start_EST'
    })

    # Drop Unnecessary Columns
    source = source.drop(['Unnamed: 6', 'Notes'], 1)

    # Update Overtime Column w/ 1 and 0
    source['Overtime'].fillna(0, inplace=True)
    source.loc[source['Overtime'] == 'OT', 'Overtime'] = 1

    return source


def who_won(row):
    """
    Determines which team won based on point totals.
    :param row: Row in nba data frame it is applied to
    :return: Returns strings 'Home' or 'Away'
    """
    if row['PTS.1'] > row['PTS']:
        winner = 'Home'
    else:
        winner = 'Away'
    return winner


def point_diff(row):
    """
    Calculates point differential for a game
    :param row: Row in nba data frame function is applied to
    :return: Returns differnce in points between home and away team
    """
    return abs(row['PTS.1']-row['PTS'])


def reform_df(source_df, empty_df, x, y, z):
    """
    Creates new df using index of home and away team and strings 'Home' and 'Away'
    Used to build game level data for each team.
    Note: Need to pass column indices for columns containing team names because couldn't make it a string variable
    :param source_df: Source nba data frame
    :param empty_df: Empty data frame to populate for either home or away team
    :param x: Populates team. Expects column of home team (4) if reforming home df or away if reforming away (6) df
    :param y: String either 'Home' or 'Away'
    :param z: Populates opponent. Expects column of away team (6) if reforming home df or home if reforming away (4) df
    :return: A data frame with relevant columns for either the home team or away team for each game. 
    """
    for i, r in enumerate(source_df.itertuples(), 1):
        empty_df = empty_df.append({'GameID': r.GameID,
                                    'Team': r[x],
                                    'H/A': y,
                                    'PT_Diff': r.PT_Diff,
                                    'Overtime': r.Overtime,
                                    'Date': r.Date,
                                    'Opponent': r[z],
                                    'Start_EST': r.Start_EST}, ignore_index=True)
    return empty_df


def win_or_loss(source, row, winning_team):
    """Add win/loss column to each game"""
    a = source['GameID'][source['Winner'] == winning_team]
    a = a.tolist()
    if row['GameID'] in a:
        return 1
    else:
        return 0


def clean_result(df):
    """Add record before each game for each team and clean up. May want to group by seasons in future"""
    # Reverse pt diff for losing team
    df['PT_Diff'] = df['PT_Diff'].where(df['W/L'] == 1, -df['PT_Diff'])

    # Calculate wins and GP for team in Team column
    df['Wins'] = (df['W/L']).groupby(df['Team']).cumsum()-1  # subtracting one to calc record coming into the game
    df['GP'] = df.groupby('Team').cumcount()  # got rid of +1 to not count first instance

    # Set negatives to 0 to clean up for teams that start on losing streak
    df.loc[df['Wins'] < 0, 'Wins'] = 0

    # Calculate Record PCT #
    df['PCT'] = df['Wins']/df['GP']

    # Clean NaNs #
    df.PCT = df.PCT.fillna(0)

    # Repeat with opponent record // should be able to find a better way to do this or combine with above
    # Opponent wins will actually just be the opposite of team wins
    df['Opponent_W/L'] = df['W/L'].apply(lambda x: 1 if x == 0 else 0)
    df['Opponent_Wins'] = (df['Opponent_W/L']).groupby(df['Opponent']).cumsum()-1
    df['Opp_GP'] = df.groupby('Opponent').cumcount()
    df.loc[df['Opponent_Wins'] < 0, 'Opponent_Wins'] = 0
    df['Opponent_PCT'] = df['Opponent_Wins']/df['Opp_GP']
    df.Opponent_PCT = df.Opponent_PCT.fillna(0)

    # Round records
    df = df.round({'PCT': 3, 'Opponent_PCT': 3})

    # Reorder columns for clarity

    df = df[['GameID', 'Date', 'Start_EST', 'H/A', 'Team', 'W/L', 'Overtime',
             'PT_Diff', 'Wins', 'GP', 'PCT', 'Opponent', 'Opponent_PCT']]

    return df


def season_totals(df):
    """Calculates team record after each game and returns records for each team on the season"""
    wins = df.copy()
    wins['Wins'] = (wins['W/L']).groupby(wins['Team']).cumsum()  # Changing wins to account for wins after game played
    wins['GP'] = wins.groupby('Team').cumcount()+1  # Adding 1 to include initial instance
    wins['PCT'] = ((wins['W/L']).groupby(wins['Team']).cumsum()/(wins.groupby('Team').cumcount()+1))
    wins['Losses'] = wins['GP']-wins['Wins']
    check = wins[['Team', 'Wins', 'Losses', 'PCT']][wins['GP'] == 82]
    check.sort_values(['PCT', 'Team'], ascending=[0, 1], inplace=True)
    check = check.round({'PCT': 3})
    return check
