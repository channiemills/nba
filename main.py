"""
Project to get the records of all teams after each game. Will later be used to predict team performance 
based on opponent record.
"""
"""
- Read CSV into DF
- Create a new DF for all 1230 games with two records for each game
||GameID||Team||H/A||W/L||Record||
|1|New York Knicks|A|L|0.00|
|1|Cleveland Cavaliers|H|W|1.00|


Functions: 
- Get the Winner of a game
    - Find max of two scores
    - if max score belongs to home team, return home else return away
- Calculate the record of each team after each game
    - Sum wins / Total games
    - Add to DF
    
Later
- Normalize data frames
    - Store date, time, and gameID
    - Store team and city
"""
import pandas as pd
import glob, os
import timeit

start_time = timeit.default_timer()
# Clean Data #

# Read in data
# source = pd.read_csv('./gamedata/oct1617.csv')

game_files = glob.glob(os.path.join('./gamedata', "*.csv"))
df_each_file = (pd.read_csv(f) for f in game_files)
source = pd.concat(df_each_file, ignore_index=True)


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

source = column_transforms(source)


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


source['Winner'] = source.apply(who_won, axis=1)


def point_diff(row):
    """
    Calculates point differential for a game
    :param row: Row in nba data frame function is applied to
    :return: Returns differnce in points between home and away team
    """
    return abs(row['PTS.1']-row['PTS'])


source['PT_Diff'] = source.apply(point_diff, axis=1)

# Initialize empty data frames of home and away teams for each game to combine later

df_away = pd.DataFrame()
df_home = pd.DataFrame()


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


df_away = reform_df(source, df_away, 4, 'Away', 6)
df_home = reform_df(source, df_home, 6, 'Home', 4)

# Add W/L column


def win_or_loss(row,winning_team):
    a = source['GameID'][source['Winner'] == winning_team]
    a = a.tolist()
    if row['GameID'] in a:
        return 1
    else:
        return 0


df_away['W/L'] = df_away.apply(lambda row: win_or_loss(row, 'Away'), axis=1)
df_home['W/L'] = df_home.apply(lambda row: win_or_loss(row, 'Home'), axis=1)

# Combine into one df to get all games
df = pd.concat([df_away, df_home])

## Function for result df cleanup ## 
df.sort_values(['GameID', 'W/L'], ascending=[1, 0], inplace=True)


# Change sign of pt diff for losing team
df['PT_Diff'] = df['PT_Diff'].where(df['W/L'] == 1, -df['PT_Diff'])


# Add fields needed for record PCT. This will be different if I want the season total or game level. #
# May want to group by seasons one day

df['Wins'] = (df['W/L']).groupby(df['Team']).cumsum()-1  # subtracting one to calc record coming into the game
df['GP'] = df.groupby('Team').cumcount()  # got rid of +1 to not count first instance

# Set negatives to 0 to clean up for teams that start on losing streak
df.loc[df['Wins'] < 0, 'Wins'] = 0

# Calculate Record PCT #
df['PCT'] = df['Wins']/df['GP']

# Clean NaNs #
df.PCT = df.PCT.fillna(0)

# Repeat with opponent record // should be able to find a better way to do this
df['Opponent_Wins'] = (df['W/L']).groupby(df['Opponent']).cumsum()-1
df['Opp_GP'] = df.groupby('Opponent').cumcount()
df.loc[df['Opponent_Wins'] < 0, 'Opponent_Wins'] = 0
df['Opponent_PCT'] = 1-df['Opponent_Wins']/df['Opp_GP']
df.Opponent_PCT = df.Opponent_PCT.fillna(0)


# Round records
df = df.round({'PCT': 3, 'Opponent_PCT': 3})

# Reorder columns for clarity

df = df[['GameID', 'Date', 'Start_EST', 'H/A', 'Team', 'W/L', 'Overtime',
         'PT_Diff', 'Wins', 'GP', 'PCT', 'Opponent', 'Opponent_PCT']]

#df.to_csv('result.csv')

## /end function ## 

# Sanity check

## If I want to know who won I can just make a function that does different column calculations ##

def season_totals(df):

    wins = df.copy()
    wins['Wins'] = (wins['W/L']).groupby(wins['Team']).cumsum()  # Changing wins to account for wins after game played
    wins['GP'] = wins.groupby('Team').cumcount()+1  # Adding 1 to include initial instance
    wins['PCT'] = ((wins['W/L']).groupby(wins['Team']).cumsum()/(wins.groupby('Team').cumcount()+1))
    wins['Losses'] = wins['GP']-wins['Wins']
    check = wins[['Team', 'Wins', 'Losses', 'PCT']][wins['GP'] == 82]
    check.sort_values(['PCT', 'Team'], ascending=[0, 1], inplace=True)
    check = check.round({'PCT': 3})
    return check

# wins = df[['Team', 'Wins', 'GP', 'PCT', 'Opponent', 'Opponent_PCT']][df['GP'] == 82]

check = season_totals(df)

execution_time = timeit.default_timer() - start_time
print check.head(10)
print 'Completed in ' + str(format(execution_time, '.2f')) + ' seconds.'



