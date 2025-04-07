import os
import sys
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

ANALYSIS = 'sliding_window'
LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']

DATA_PATH = 'data_sorted'

from helper.columns_starters import ALL_COLS
from helper.generate_pat import generate_pat_model
from helper.general_processing import sort_starters

from ml_predictions.ml_helper import compute_serve
from ml_predictions.ml_helper import compute_spike

players_per_role = {
    'OH': 2,
    'MB': 2,
    'S' : 1,
    'O' : 1
}

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i

def generate_pat_one_match(id, year, train_matches, match, league):
    points_to_win = 5
    teamA = match['teamA']
    teamB = match['teamB']

    league_dir = f"{ANALYSIS}/{league}"
    if not os.path.exists(league_dir):
        os.makedirs(league_dir)
    
    directory = f"{ANALYSIS}/{league}/{year}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    id_string = str(id)
    while len(id_string) != 3:
        id_string = '0' + id_string

    outpath = f"{ANALYSIS}/{league}/{year}/{id_string}_{teamA}vs{teamB}.pcsp"
    generate_pat_model(id, teamA, teamB, train_matches, points_to_win, outpath, league)

def create_match(match):
    rebased_match_A = {
        'match_id' : match['match_id'],
        'match_date': match['match_date'],
        'other_team': match['teamB'],
        'num_sets': int(match['teamA_score']) + int(match['teamB_score']),
        'home_players': match['teamA-players'],
        'away_players': match['teamB-players'],
        'home_starters': match['teamA-starting'],
        'away_starters': match['teamB-starting']
    }
    rebased_match_B = {
        'match_id' : match['match_id'],
        'match_date': match['match_date'],
        'other_team': match['teamA'],
        'num_sets': int(match['teamA_score']) + int(match['teamB_score']),
        'home_players': match['teamB-players'],
        'away_players': match['teamA-players'],
        'home_starters': match['teamB-starting'],
        'away_starters': match['teamA-starting']
    }

    return rebased_match_A, rebased_match_B

def handle_match(team_data, match, weight):
    players_stats = team_data["players_stats"]
    players_details = team_data["players_details"]
    counts = team_data["counts"]
    starters = match['home_starters']
    players = match['home_players']

    num_sets = len(starters[0]) - 2
    team_data['num_sets'] += num_sets

    for i in range(len(players)):
        player = players[i]
        volleybox_role = player[2]
        player_role = player[3]
        curr_details = player[0:4]
        curr_stats = player[4:]
        player_name = player[1]
        
        adapted_role = volleybox_role if player_role == 'U' or player_role == 'L' else player_role
        team_data[f"{adapted_role}_hits"] += int(player[mapping['attack_total']]) * weight
        
        for set in range(2, len(starters[0])):
            set_role = starters[i][set]
            if set_role != '0':
                counts[set_role][player_name] = 1 * weight if player_name not in counts[set_role] else 1 * weight + counts[set_role][player_name] 

        if player_role == 'L':
            counts[player_role][player_name] = num_sets * weight if player_name not in counts[player_role] else num_sets * weight + counts[player_role][player_name] 
        
        if player_name not in players_stats:
            players_stats[player_name] =  [weight * int(col2) if col2 is not None else 0 for col2 in curr_stats]
            players_details[player_name] = curr_details
        else:
            players_stats[player_name] = [col1 + weight * int(col2) if col2 is not None else 0 for col1, col2, in zip(players_stats[player_name], curr_stats)]


def process_data(all_teams_processed):
    all_teams = {}

    for team in all_teams_processed:
        team_data = {
            "OH_hits": 0,
            "MB_hits": 0,
            "O_hits": 0,
            "S_hits": 0,
            "L_hits": 0,
            "num_sets": 0,
            "players_stats": {},
            "players_details": {},
            "counts": {
                "OH": {},
                "MB": {},
                "O": {},
                "S": {},
                "L": {}
            },
            "num_sets_played": {}
        }

        old_matches = all_teams_processed[team]['old_matches']
        new_matches = all_teams_processed[team]['new_matches']

        for match in old_matches:
            handle_match(team_data, match, 1)
        for match in new_matches:
            handle_match(team_data, match, 2)

        all_teams[team] = team_data

    all_teams_processed = sort_starters(all_teams, {}, mapping)
    return all_teams_processed

def ammend_sliding_window(predict_match, all_teams_matches):
    teamA = predict_match['teamA']
    teamB = predict_match['teamB']
    A_match, B_match = create_match(predict_match)


    if teamA in all_teams_matches:
        all_teams_matches[teamA]['new_matches'].append(A_match)

        if len(all_teams_matches[teamA]['old_matches']) > 0:
            all_teams_matches[teamA]['old_matches'].pop(0)

    if teamB in all_teams_matches:
        all_teams_matches[teamB]['new_matches'].append(B_match)

        if len(all_teams_matches[teamB]['old_matches']) > 0:
            all_teams_matches[teamB]['old_matches'].pop(0)



class SlidingWindow:
    def __init__(self):
        pass
    
    def model_get_players(self, teamA, teamB, matches_processed):
        pass
    
    def ammend_sliding_window(self, all_teams_matches, new_match):
        # Ammends sliding window
        all_teams_processed = process_data(all_teams_matches)
        ammend_sliding_window(new_match, all_teams_matches)
        return all_teams_processed
    
    def generate_analysis_stats(self, all_teams_processed, team, other_team, match_id, year, league):
        spike_rates, serve_rates = [], []
        
        team_object = all_teams_processed[team]
        
        index = 0
        for role in players_per_role:
            count = players_per_role[role]
            for i in range(count):
                player = team_object[role][i]
                serve_row = compute_serve(player, match_id, role, year, league)
                serve_rates.append(serve_row)
                if role != 'S':
                    spike_row = compute_spike(player, match_id, role, year, league) 
                    spike_rates.append(spike_row)
                    
                index += 1
                    
        return spike_rates, serve_rates

    def generate_analysis_data(self, matches, predict_matches, training_year, league):
        # Compute data from other leagues
        all_teams_matches = {}
        
        for predict_match in matches:
            teamA = predict_match['teamA']
            teamB = predict_match['teamB']
            A_match, B_match = create_match(predict_match)
            if teamA not in all_teams_matches:
                all_teams_matches[teamA] = {
                    'old_matches': [],
                    'new_matches' : []
                }
            if teamB not in all_teams_matches:
                all_teams_matches[teamB] = {
                    'old_matches': [],
                    'new_matches' : []
                }
            all_teams_matches[teamA]['old_matches'].append(A_match)
            all_teams_matches[teamB]['old_matches'].append(B_match)
        
        for team in all_teams_matches:
            old_matches = all_teams_matches[team]['old_matches']
            sorted_top_matches = sorted(old_matches, key=lambda x: datetime.strptime(x["match_date"], "%Y-%m-%d"))
            all_teams_matches[team]['old_matches'] = sorted_top_matches

        return all_teams_matches