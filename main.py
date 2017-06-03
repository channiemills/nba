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

# Order by Game Date, Time
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

# Identify Winner #

def who_won(row):
    if row['PTS.1'] > row['PTS']:
        winner = 'Home'
    else:
        winner = 'Away'
    return winner


source['Winner'] = source.apply(who_won, axis=1)


def point_diff(row):
    return abs(row['PTS.1']-row['PTS'])

source['PT_Diff'] = source.apply(point_diff, axis=1)

# Initialize empty data frames of home and away teams for each game to combine later

df_away = pd.DataFrame()
df_home = pd.DataFrame()


def reform_df(source_df, empty_df, x, y):
    for i, r in enumerate(source_df.itertuples(),1):
        empty_df = empty_df.append({'GameID': r.GameID,
                                    'Team': r[x],
                                    'H/A': y,
                                    'PT_Diff': r.PT_Diff,
                                    'Overtime': r.Overtime,
                                    'Date': r.Date,
                                    'Start_EST': r.Start_EST}, ignore_index=True)
    return empty_df


df_away = reform_df(source, df_away, 4, 'Away')
df_home = reform_df(source, df_home, 6, 'Home')

# print df_away.head(), df_home.head()

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
df = pd.concat([df_away,df_home])
df.sort_values(['GameID', 'W/L'], ascending=[1, 0], inplace=True)


# Change sign of pt diff for losing team
df['PT_Diff'] = df['PT_Diff'].where(df['W/L'] == 1, -df['PT_Diff'])


# Add record PCT #

df['Wins'] = (df['W/L']).groupby(df['Team']).cumsum()
df['GP'] = df.groupby('Team').cumcount()+1
df['PCT'] = df['Wins']/df['GP']

# Reorder columns for clarity

df = df[['GameID', 'Date', 'Start_EST', 'H/A', 'Team', 'W/L', 'Overtime', 'PT_Diff', 'Wins', 'GP', 'PCT']]

df.to_csv('result.csv')

# Sanity check

wins = df[['Team', 'Wins', 'GP', 'PCT']][df['GP'] == 82]
wins.sort_values(['PCT','Team'], ascending=[0, 1], inplace=True)
wins['Losses'] = wins['GP']-wins['Wins']
check = wins[['Team', 'Wins', 'Losses', 'PCT']]

execution_time = timeit.default_timer() - start_time
print check.head(10)
print 'Completed in ' + str(format(execution_time, '.2f')) + ' seconds.'



