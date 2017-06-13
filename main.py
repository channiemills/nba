"""
Project to get the records of all teams after each game. Will later be used to predict team performance 
based on opponent record.
"""

import pandas as pd
import glob, os
import timeit
import helpers as h

# Start timer
start_time = timeit.default_timer()

# Read in and transform data
# source = pd.read_csv('./gamedata/oct1617.csv')

game_files = glob.glob(os.path.join('./gamedata', "*.csv"))
df_each_file = (pd.read_csv(f) for f in game_files)
source = pd.concat(df_each_file, ignore_index=True)

# Create and transform columns
source = h.column_transforms(source)
source['Winner'] = source.apply(h.who_won, axis=1)
source['PT_Diff'] = source.apply(h.point_diff, axis=1)

# Initialize and populate empty data frames of home and away teams for each game
df_away = pd.DataFrame()
df_home = pd.DataFrame()

df_away = h.reform_df(source, df_away, 4, 'Away', 6)
df_home = h.reform_df(source, df_home, 6, 'Home', 4)

# Add W/L column
df_away['W/L'] = df_away.apply(lambda row: h.win_or_loss(source, row, 'Away'), axis=1)
df_home['W/L'] = df_home.apply(lambda row: h.win_or_loss(source, row, 'Home'), axis=1)

# Combine into one df to get all games sorted by gameid and w/l
df = pd.concat([df_away, df_home])
df.sort_values(['GameID', 'W/L'], ascending=[1, 0], inplace=True)

# Clean combined data
output_df = h.clean_result(df)

# Write data
output_df.to_csv('result.csv')

# Sanity check by calculating top 10 teams in league
check = h.season_totals(df)

execution_time = timeit.default_timer() - start_time
print check.head(10)
print 'Completed in ' + str(format(execution_time, '.2f')) + ' seconds.'
