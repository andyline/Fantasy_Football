"""
Created on Tue Aug  7 11:26:38 2018

"""

import pandas as pd
import numpy as np 

data = pd.read_excel('FPLData.xlsx') 
#%%
data['metric'] = data['Form'].add(data['TotalPoints']*4, fill_value=1)
data['Pts_Per_Cost'] = (data['metric'].divide(data['Cost'], fill_value=1))*100000
#teams = data.Team.unique()

# 
weight = {'BOU':1.25, 'WHU':1.00, 'MCI':1.75, 'LEI':1.25, 'TOT':1.5, 'LIV':1.75, 'CHE':1.75, 
               'BHA':1.0, 'SOU':1.0, 'NEW':1.00, 'ARS':1.5, 'FUL':1.00, 'HUD':1.00, 'MUN':1.5, 
               'EVE':1.50, 'CAR':1.0, 'BUR':1.25, 'WOL':1.25, 'CRY':1.25, 'WAT':1.50}

data['Team_weight'] = [weight[item] for item in data.Team]

fixtures = {'Cardiff City':1.0, 'Liverpool':1.75, 'Arsenal':1.5, 'Man Utd':1.5, 'Newcastle':1.00,
       'West Ham':1.00, 'Huddersfield':1.00, 'Watford':1.50, 'Burnley':1.25, 'Tottenham':1.5,
       'Man City':1.75, 'Crystal Palace':1.25, 'Chelsea':1.75, 'Leicester':1.25,
       'Wolverhampton':1.25, 'Bournemouth':1.25, 'Southampton':1.0, 'Everton':1.50, 'Fulham':1.00,
       'Brighton':1.0}

data['Next1'] = [fixtures[item] for item in data.NextFixture1]
data['Next2'] = [fixtures[item] for item in data.NextFixture2]
data['Next3'] = [fixtures[item] for item in data.NextFixture3]
data['Next4'] = [fixtures[item] for item in data.NextFixture4]
data['Next5'] = [fixtures[item] for item in data.NextFixture5]

data['Next1'] *= 1.2
data['Next2'] *= 1.1
data['Next3'] *= 1.0
data['Next4'] *= 0.9
data['Next5'] *= 0.8

data['Next_Fixtures_Weighted_avg'] = data[['Next1','Next2','Next3','Next4','Next5']].mean(axis=1)
data['Upcoming'] = (data['Team_weight'].divide(data['Next_Fixtures_Weighted_avg'], fill_value=1))
data['FLScore'] = (data['Upcoming'].multiply(data['Pts_Per_Cost'], fill_value=1))

#%%

# element_type is a value from 1 to 4 representing position
# convert this into binary values for each position, as well as a 'position' string
Pos = {'GLK':1.0, 'DEF':2.0, 'MID':3.0, 'FWD':4.0}
data['Position'] = [Pos[item] for item in data.PositionsList]

data['GLK'] = data['Position'].map(lambda x: 1 if x == 1 else 0)
data['DEF'] = data['Position'].map(lambda x: 1 if x == 2 else 0)
data['MID'] = data['Position'].map(lambda x: 1 if x == 3 else 0)
data['FWD'] = data['Position'].map(lambda x: 1 if x == 4 else 0)

#%%
# costs is an array with the cost of each player
costs = data['Cost']
# keepers is an array with a 1 if a player increases the number of keepers or 0 otherwise
keepers = data['GLK']
# defenders is an array with a 1 if a player increases the number of defenders or 0 otherwise
defenders = data['DEF']
# midfielders is an array with a 1 if a player increases the number of midfielders or 0 otherwise
midfielders = data['MID']
# forwards is an array with a 1 if a player increases the number of forwards or 0 otherwise
forwards = data['FWD']
#%%
# players is an array with a 1 if a player increases the number of players or 0 otherwise
# ie, all ones

players = np.ones(len(data))

params = np.array([
  costs,
  keepers,
  defenders,
  midfielders,
  forwards,
  ])

upper_bounds = np.array([
  10000000000, # max cost
  1,    # max keepers
  4,    # max defenders
  5,    # max midfielders
  3,    # max fowards
])

# total_points is an array of total points per player
# this is what we want to maximize
total_points = data['FLScore']

from scipy.optimize import linprog

#%% Greedy algo

bounds = [(0, 1) for x in range(len(data))]

data['selected'] = linprog(
  -total_points, # negative profit so linprog will maximize, not minimize
  params,
  upper_bounds,
  bounds=bounds
).x
        
Team_Selection = data.loc[data['selected'] != 0] \
  [['Surname', 'PositionsList', 'Cost', 'FLScore', 'Pts_Per_Cost']] \
  .sort_values(by=['FLScore'], ascending=False)

print(Team_Selection) 
print("Total Squad Cost: %.2f" % np.sum(Team_Selection.Cost))
#%% Rankings
  
Rank_GLK = data.loc[data['Position'] == 1] \
    [['Surname', 'PositionsList', 'Cost', 'FLScore', 'Pts_Per_Cost']] \
    .sort_values(by=['FLScore'], ascending=False)
    
Rank_DEF = data.loc[data['Position'] == 2] \
    [['Surname', 'PositionsList', 'Cost', 'FLScore', 'Pts_Per_Cost']] \
    .sort_values(by=['FLScore'], ascending=False)
    
Rank_MID = data.loc[data['Position'] == 3] \
    [['Surname', 'PositionsList', 'Cost', 'FLScore', 'Pts_Per_Cost']] \
    .sort_values(by=['FLScore'], ascending=False)
    
Rank_FWD = data.loc[data['Position'] == 4] \
    [['Surname', 'PositionsList', 'Cost', 'FLScore', 'Pts_Per_Cost']] \
    .sort_values(by=['FLScore'], ascending=False)
