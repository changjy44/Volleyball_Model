import os
import sys
import json
from collections import Counter


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']
ANALYSIS = 'base_1'

from helper.columns_starters import ALL_COLS

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i


def process(teams, teamA, players):
    pairs = [(player[0], player[1]) for player in players]
    if teamA not in teams:
        teams[teamA] = {}
    
    for jersey, name in pairs:
        if name not in teams[teamA]:
            teams[teamA][name] = {}
        
        if jersey not in teams[teamA][name]:
            teams[teamA][name][jersey] = 0
        
        teams[teamA][name][jersey] += 1


def clean(teams, match_id, team, players, starting):
    for i in range(len(players)):
        player = players[i]
        jersey = player[0]
        name = player[1]
        angry = teams[team]
        
        data = teams[team][name]
        highest_jersey = max(data, key=data.get)
        if jersey != highest_jersey:
            player[0] = highest_jersey
        
        starting[i][0] = highest_jersey
    
    new_numbers = [player[0] for player in players]
        
    dup_numbers = []
    counts = Counter(new_numbers)
    for num, count in counts.items():
        if count > 1:
            dup_numbers.append(num)
            
    for dup in dup_numbers:
        filtered_players = [player for player in players if player[0] == dup]
        filtered_starters = [player for player in starting if player[0] == dup]
        names = all(player[1] == filtered_players[0][1] for player in filtered_players)
        if names:
            players.remove(filtered_players[0])
            starting.remove(filtered_starters[0])
            
    new_numbers = [player[0] for player in players]
    new_starting = [player[0] for player in starting]
    
    assert len(set(new_numbers)) == len(new_numbers)
    assert len(set(new_starting)) == len(new_starting)
    
    sorted_players = sorted(players, key=lambda p:int(p[0]))
    sorted_starting = sorted(starting, key=lambda p:int(p[0]))
    
    return sorted_players, sorted_starting

for league in LEAGUES:
    for year_index in range(len(YEARS)):
        prediction_year = YEARS[year_index]
    
        # Preprocess data
        with open(f'data/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
            matches = json.load(f)

        teams = {}
        
        new_matches = []
        
        for match in matches:
            teamA = match['teamA']
            teamB = match['teamB']
            teamA_players = match['teamA-players']
            teamB_players = match['teamB-players']
            teamA_starters = match['teamA-starting']
            teamB_starters = match['teamB-starting']
            process(teams, teamA, teamA_players)
            process(teams, teamB, teamB_players) 
        
        for team in teams:
            for name in teams[team]:
                if len(teams[team][name].keys()) > 1:
                    print(league, team, name, teams[team][name].items())
            
        # for match in matches:
        #     new_match = match
        #     match_id = match['match_id']
            
        #     teamA = match['teamA']
        #     teamB = match['teamB']
        #     teamA_players = match['teamA-players']
        #     teamB_players = match['teamB-players']
        #     teamA_starters = match['teamA-starting']
        #     teamB_starters = match['teamB-starting']
            
        #     new_A_players, new_A_starters = clean(teams, match_id, teamA, teamA_players, teamA_starters)
        #     new_B_players, new_B_starters = clean(teams, match_id, teamB, teamB_players, teamB_starters)
            
        #     new_match['teamA-players'] = new_A_players
        #     new_match['teamB-players'] = new_B_players
        #     new_match['teamA-starting'] = new_A_starters
        #     new_match['teamB-starting'] = new_B_starters
        #     new_matches.append(new_match)
        
        # with open(f'data_better/{league}/{prediction_year}-{league}-data-final-v3.json', 'w') as f:
        #     json.dump(new_matches, f)
            

            
        
            
        
                
            


