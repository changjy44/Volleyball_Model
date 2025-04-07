import os
import sys
import json
import numpy as np
from datetime import datetime 

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

ANALYSIS = 'sliding_window_1'
LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
# This analysis only works for other leagues
LEAGUES = ['poland', 'italy', 'france', 'japan'] 

YEARS = ['2021', '2022', '2023', '2024']

DATA_PATH = 'data_sorted'

from helper.columns_starters import ALL_COLS
from helper.general_processing import sort_starters
from helper.general_processing import process_team

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


def get_players(team, train_matches):
    pointers = {
        'OH': 0,
        'MB': 0,
        'O' : 0,
        'S' : 0,
    }

    curr_role_pointer = 0

    players = []
    for role in players_per_role:
        count = players_per_role[role]
        for i in range(count):
            counter = 0
            loop_role = role
            while i >= len(train_matches[team][loop_role]):

                counter += 1
                new_role = list(pointers.keys())[curr_role_pointer]
                print(f"{team} no more {loop_role}, finding {new_role}")
                loop_role = new_role
                curr_role_pointer += 1
                if curr_role_pointer == 3:
                    curr_role_pointer = 0
                if counter > 6:
                    raise Exception('Encountered infinite loop, not enough players')

            player = train_matches[team][loop_role][i]
            
            if int(player[mapping['attack_points']]) + int(player[mapping['attack_errors']]) + int(player[mapping['attack_attempts']]) == 0:
                player[mapping['attack_attempts']] = 1

            if int(player[mapping['serve_points']]) + int(player[mapping['serve_errors']]) + int(player[mapping['serve_attempts']]) == 0:
                player[mapping['serve_attempts']] = 1
                
            players.append(player)
            pointers[loop_role] += 1
        
    return players

def handle_entry(team_data, entry, weight):
    starter_data = entry['starter_details']
    player = entry['player_details']

    players_stats = team_data["players_stats"]
    players_details = team_data["players_details"]
    counts = team_data["counts"]
    num_sets = len(starter_data) - 2

    volleybox_role = player[2]
    player_role = player[3]
    player_name = player[1]
    curr_details = player[0:4]
    curr_stats = player[4:]

    team_data['num_sets'] += num_sets
    adapted_role = volleybox_role if player_role == 'U' or player_role == 'L' else player_role
    team_data[f"{adapted_role}_hits"] += int(player[mapping['attack_total']]) * weight

    for set in range(2, len(starter_data)):
        set_role = starter_data[set]
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
            'num_sets_played' : {}
        }

        num_players = 0
        for name in all_teams_processed[team]:
            num_players += 1
            old_matches_entry = all_teams_processed[team][name]['old_matches']
            new_matches_entry = all_teams_processed[team][name]['new_matches']

            for entry in old_matches_entry:
                handle_entry(team_data, entry, 1)
            for entry in new_matches_entry:
                handle_entry(team_data, entry, 2)

        team_data['num_sets'] = int(team_data['num_sets'] / num_players)

        all_teams[team] = team_data

    all_teams_processed = sort_starters(all_teams, {}, mapping)
    return all_teams_processed



def compute_team(leagues_data, players, starters, league, match_date, num_sets):
    for player, starter in zip(players, starters):
        player_name = player[1]
        combine_data = {
            'match_date': match_date,
            'num_sets': num_sets,
            'player_details': player,
            'starter_details' : starter
        }
        if player_name not in leagues_data[league]:
            leagues_data[league][player_name] = []
        
        leagues_data[league][player_name].append(combine_data)
    return leagues_data

# Returns an object containing each player and an array of all their matches
def compute_training_leagues(training_year):
    leagues_data = {
        'poland': {},
        'italy': {},
        'france': {},
        'japan': {}
    }

    for league in LEAGUES:
        with open(f'{DATA_PATH}/{league}/{training_year}-{league}-data-final-v3.json') as f:
            matches = json.load(f)

        for match in matches:
            teamA_players = match['teamA-players']
            teamB_players = match['teamB-players']
            teamA_starters = match['teamA-starting']
            teamB_starters = match['teamB-starting']
            match_date = match['match_date']
            num_sets = int(match['teamA_score']) + int(match['teamB_score'])

            compute_team(leagues_data, teamA_players, teamA_starters, league, match_date, num_sets)
            compute_team(leagues_data, teamB_players, teamB_starters, league, match_date, num_sets)
    
    return leagues_data

def compute_stats(league_data, league):
    combined = [ [(mini_match['player_details'], mini_match['num_sets']) for mini_match in league_data[league][player]] for player in league_data[league]]
    flattend = []
    for player in combined:
        for match in player:
            flattend.append(match)

    player_front = [player[0][:4] for player in flattend]
    player_stats = [(player[0][4:], player[1]) for player in flattend]
    num_sets_col = [player[1] for player in flattend]
    clean_stats = [[float(col) / num_sets if col is not None else 0.0 for col in player] for player, num_sets in player_stats]

    return player_front, np.array(clean_stats), num_sets_col


def standardise_columns(source, target):
    new_target = target.copy()
    
    for col in range(target.shape[1]):
        src_col = source[:, col]
        tgt_col = target[:, col]
        
        src_mask = src_col != 0
        tgt_mask = tgt_col != 0
        
        src_mean = src_col[src_mask].mean() if np.any(src_mask) else 0
        src_std  = src_col[src_mask].std() if np.any(src_mask) else 1
        
        tgt_mean = tgt_col[tgt_mask].mean() if np.any(tgt_mask) else 0
        tgt_std  = tgt_col[tgt_mask].std() if np.any(tgt_mask) else 1
        
        if np.any(tgt_mask):
            new_target[tgt_mask, col] = ((tgt_col[tgt_mask] - tgt_mean) / tgt_std) * src_std + src_mean
            
    return new_target


def normalise_leagues_data(league_data, target_league):
    for league in LEAGUES:
        if league == target_league:
            continue

        _, original_stats, original_num_sets = compute_stats(league_data, target_league)
        transfer_players, transfer_stats, transfer_num_sets = compute_stats(league_data, league)

        standardised_stats_numpy = standardise_columns(original_stats, transfer_stats)
        standardised_stats = [row.tolist() for row in standardised_stats_numpy]
        multiply_num_sets =  [[col  * num_sets for col in row] for row, num_sets in zip(standardised_stats, transfer_num_sets)]
            

        combined_players = [p1 + p2 for p1, p2 in zip(transfer_players, multiply_num_sets)]
        for player in league_data[league].keys():
            filtered_stats = [stat for stat in combined_players if stat[1] == player]

            assert len(filtered_stats) == len(league_data[league][player])
            for i in range(len(league_data[league][player])):
                entry = league_data[league][player][i]
                stat = filtered_stats[i]
                entry['player_details'] = stat
                
    return league_data

def compute_prediction_starters(prediction_matches):
    all_teams = {}
    all_teams_processed = {}

    for match in prediction_matches:    
        teamA = match['teamA']
        teamB = match['teamB']
        teamA_players = match['teamA-players']
        teamB_players = match['teamB-players']
        teamA_starters = match['teamA-starting']
        teamB_starters = match['teamB-starting']
        process_team(all_teams, teamA, teamA_players, teamA_starters, mapping)
        process_team(all_teams, teamB, teamB_players, teamB_starters, mapping)
    
    all_teams_processed = sort_starters(all_teams, all_teams_processed, mapping)

    return all_teams_processed

def precompute_sliding_window(prediction_processed, training_processed, league_data_normalised, league):
    all_teams_matches = {}
    seen = set()

    for team in prediction_processed:
        if team not in training_processed:
            # We ignore the team if it did not play in the training year
            continue
        all_teams_matches[team] = {}

        for role in ['OH', 'MB', 'O', 'S', 'L']:
            players_that_role = prediction_processed[team][role]
            for player in players_that_role:
                name = player[1]

                old_matches = []
                for league_2 in league_data_normalised:
                    if name in league_data_normalised[league_2]:
                        old_matches = league_data_normalised[league_2][name]
                        seen.add(name)

                all_teams_matches[team][name] = {
                    'old_matches': old_matches,
                    'new_matches' : []
                }
            
    for team in training_processed:
        if team not in all_teams_matches:
            # We ignore the team if it did not play in the prediction year
            continue

        for role in ['OH', 'MB', 'O', 'S', 'L']:
            players_that_role = training_processed[team][role]
            for player in players_that_role:
                name = player[1]
                if name not in seen:
                    old_matches = [] if name not in  league_data_normalised[league] else league_data_normalised[league][name]
                    all_teams_matches[team][name] = {
                        'old_matches': old_matches,
                        'new_matches' : []
                    }
    return all_teams_matches

def ammend_sliding_window_players(all_teams_matches, team, players, starters):
    for p1, p2 in zip(players, starters):
        combine_data = {
            'player_details': p1,
            'starter_details' : p2
        }
        name = p1[1]

        if name not in all_teams_matches[team]:
            print(f'{name} played 0 sets')
            all_teams_matches[team][name] = {
                'old_matches': [],
                'new_matches' : []
            }

        all_teams_matches[team][name]['new_matches'].append(combine_data)
    
    for player in all_teams_matches[team]:
        if len(all_teams_matches[team][player]['old_matches']) > 0:
            all_teams_matches[team][player]['old_matches'].pop(0)
            

def ammend_sliding_window(match, all_teams_matches):
    teamA = match['teamA']
    teamB = match['teamB']
    teamA_players = match['teamA-players']
    teamB_players = match['teamB-players']
    teamA_starters = match['teamA-starting']
    teamB_starters = match['teamB-starting']

    if teamA in all_teams_matches:
        ammend_sliding_window_players(all_teams_matches, teamA, teamA_players, teamA_starters)

    if teamB in all_teams_matches:
        ammend_sliding_window_players(all_teams_matches, teamB, teamB_players, teamB_starters)

def shuffle_leagues_data(leagues_data):
    new_shuffled_leagues_data = {
        'poland': {},
        'italy': {},
        'france': {},
        'japan': {}
    }
    
    all_players = set([player for league in leagues_data for player in leagues_data[league].keys()])

    for player in all_players:
        other_leagues = [(league_2, leagues_data[league_2][player])
                            for league_2 in leagues_data 
                            if player in leagues_data[league_2]]
        sorted_other_leagues = sorted(other_leagues, key=lambda p: len(p[1]), reverse=True)
        top_league, top_matches = sorted_other_leagues[0]
        for curr_league, matches in sorted_other_leagues[1:]:
            top_matches += matches
        
        sorted_top_matches = sorted(top_matches, key=lambda x: datetime.strptime(x["match_date"], "%Y-%m-%d"))
        new_shuffled_leagues_data[top_league][player] = sorted_top_matches
    
            
    return new_shuffled_leagues_data

class SlidingWindow_1:
    def __init__(self):
        pass
    
    def model_get_players(self, teamA, teamB, matches_processed):
        teamA_players = get_players(teamA, matches_processed)
        teamB_players = get_players(teamB, matches_processed)
        
        return teamA_players, teamB_players
    
    def ammend_sliding_window(self, all_teams_matches, new_match):
        # Ammends sliding window
        all_teams_processed = process_data(all_teams_matches)
        ammend_sliding_window(new_match, all_teams_matches)
        return all_teams_processed
    
    def generate_analysis_stats(self, all_teams_processed, team, other_team, match_id, year, league):
        spike_rates, serve_rates = [], []
        
        players = get_players(team, all_teams_processed)
        
        index = 0
        for role in players_per_role:
            count = players_per_role[role]
            for i in range(count):
                player = players[index]
                serve_row = compute_serve(player, match_id, role, year, league)
                serve_rates.append(serve_row)
                if role != 'S':
                    spike_row = compute_spike(player, match_id, role, year, league) 
                    spike_rates.append(spike_row)
                    
                index += 1
                    
        return spike_rates, serve_rates

    def generate_analysis_data(self, matches, predict_matches, training_year, league):
        # Compute data from other leagues
        league_data = compute_training_leagues(training_year)
        
        # Normalise data
        league_data_normalised = normalise_leagues_data(league_data, league)
        
        league_data_reshuffled = shuffle_leagues_data(league_data_normalised)
        
        # Compute data from prediction league to obtain actual players
        training_processed = compute_prediction_starters(matches)
        prediction_processed = compute_prediction_starters(predict_matches)

        all_teams_matches = precompute_sliding_window(prediction_processed, training_processed, league_data_reshuffled, league)
        
        return all_teams_matches