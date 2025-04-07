import os
import sys
import json
import csv

statistics_cols = [
    'league',
    'match_id',
    'season',
    'match_date',
    'team',
    'player_id',
    'jersey_number',
    'player_name',
    'volleybox_role',
    'starter_role',
    'attack_points',
    'attack_errors',
    'attack_attempts',
    'attack_blocked',
    'attack_total',
    'attack_kill_efficiency',
    'attack_efficiency',
    'block_points',
    'block_errors',
    'block_touches',
    'block_total',
    'block_efficiency',
    'serve_points',
    'serve_errors',
    'serve_attempts',
    'serve_total',
    'serve_efficiency',
    'reception_perfect',
    'reception_positive',
    'reception_errors',
    'reception_attempts',
    'reception_total',
    'reception_positive_%',
    'reception_perfect_%',
    'reception_efficiency',
    'dig_sucess',
    'dig_error',
    'dig_total',
    'dig_efficiency',
    'set_success',
    'set_errors',
    'set_attempts',
    'set_total',
    'set_efficiency',
    'back_attack_points',
    'back_attack_errors',
    'back_attack_total',
    'back_attack_kill_efficiency'
]

LEAGUE_MAPPING = {
    'vnl': "Nation's League",
    'poland': "Plusliga",
    'italy': "Superlega",
    'france': "Ligue Nationale de Volley",
    'japan': "SV-League"
}

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']

from helper.columns_starters import ALL_COLS

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i
    
statistics = []
PLAYER_MAPPING = {}
PLAYER_REFERENCE = {}

with open('player_mappings.csv','r', encoding='utf-8-sig') as f:
    player_mapping_table = csv.reader(f)
    for entry in player_mapping_table:
        name = entry[0]
        pid = entry[2]
        PLAYER_MAPPING[name] = pid

with open('player_volleybox.csv', 'r',encoding='utf-8-sig') as f:
    table = csv.reader(f)
    for entry in table:
        pid = entry[0]
        rest = entry[1:]
        PLAYER_REFERENCE[pid] = rest
        
def find(name):
    for key in PLAYER_REFERENCE:
        if PLAYER_REFERENCE[key][1] == name:
            return key
    assert False
        
def handle_statistics(match, league, season):

    league_name = LEAGUE_MAPPING[league]
    match_id = match["match_id"]
    match_date = match["match_date"]
    
    teamA_name = match['teamA']
    teamB_name = match["teamB"]
    teamA_players = match['teamA-players']
    teamB_players = match['teamB-players']

    teamA_stats = []
    teamB_stats = []

    for player in teamA_players:
        name = player[1]        
        player_id = find(name)
        
        temp = [league_name, match_id, season, match_date, teamA_name, player_id] + player
        teamA_stats.append(temp)

    for player in teamB_players:
        name = player[1]
        player_id = find(name)

        temp = [league_name, match_id, season, match_date, teamB_name, player_id] + player
        teamB_stats.append(temp)

    return teamA_stats, teamB_stats

    

for league in LEAGUES:
    for year_index in range(len(YEARS)):
        year = YEARS[year_index]

        # Preprocess data
        with open(f'data/{league}/{year}-{league}-data-final-v3.json') as f:
            matches = json.load(f)

        teams = {}
        
        for match in matches:
            teamA = match['teamA']
            teamB = match['teamB']
            teamA_players = match['teamA-players']
            teamB_players = match['teamB-players']
            teamA_starters = match['teamA-starting']
            teamB_starters = match['teamB-starting']
            teamA_stats, teamB_stats = handle_statistics(match, league, year)
            curr_statistics = teamA_stats + teamB_stats
            statistics.append(curr_statistics)

        

    with open('statistics.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(statistics_cols)
        for stat in statistics:
            writer.writerows(stat)

            
        
            
        
                
            


