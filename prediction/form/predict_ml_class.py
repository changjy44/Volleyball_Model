import os
import sys
import json
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']
ANALYSIS = 'form'

from helper.columns_starters import ALL_COLS
from helper.general_processing import process_team
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

def compute_target_league(all_teams_processed, league):
    target_ret = {league: {}}
    target = target_ret[league]
    for team in all_teams_processed:
        roles = ['OH', 'MB', 'O', 'S', 'L']
        for role in roles:
            players_that_role = all_teams_processed[team][role]
            for player in players_that_role:
                name = player[1]
                jersey = player[0]
                player_big = {
                    'player_details': player,
                    'num_sets_played': 1 if jersey not in all_teams_processed[team]['num_sets_played'] else all_teams_processed[team]['num_sets_played'][jersey]
                }
                target[name] = player_big
    return target_ret

def compute_training_leagues(training_year, league):
    all_teams_processed = {}
    
    if league == 'vnl':
        leagues_data = {
            'poland': {},
            'italy': {},
            'france': {},
            'japan': {}
        }
        # We use other leagues in the following year
        training_year = str(int(training_year) + 1)
    else:
        leagues_data = {
            'vnl': {}
        }
    
    for league_2 in leagues_data:
        all_teams = {}
        with open(f'data/{league_2}/{training_year}-{league_2}-data-final-v3.json') as f:
            matches = json.load(f)

        for match in matches:
            teamA = match['teamA']
            teamB = match['teamB']
            teamA_players = match['teamA-players']
            teamB_players = match['teamB-players']
            teamA_starters = match['teamA-starting']
            teamB_starters = match['teamB-starting']
            process_team(all_teams, teamA, teamA_players, teamA_starters, mapping)
            process_team(all_teams, teamB, teamB_players, teamB_starters, mapping)
        
        all_teams_processed = sort_starters(all_teams, all_teams_processed, mapping)
        
        target_all_teams = leagues_data[league_2] 
        for team in all_teams_processed:
            roles = ['OH', 'MB', 'O', 'S', 'L']
            for role in roles:
                players_that_role = all_teams_processed[team][role]
                for player in players_that_role:
                    jersey = player[0]
                    name = player[1]
                    if name in target_all_teams:
                        new_player = {
                            'player_details' : player,
                            'num_sets_played': 1 if jersey not in all_teams_processed[team]['num_sets_played'] else all_teams_processed[team]['num_sets_played'][jersey]
                        }
                        combined_player = combine_player_data(target_all_teams[name], new_player)
                        target_all_teams[name] = combined_player
                    else:
                        target_all_teams[name] = {
                            'player_details' : player,
                            'num_sets_played': 1 if jersey not in all_teams_processed[team]['num_sets_played'] else all_teams_processed[team]['num_sets_played'][jersey]
                        }
    return leagues_data

def compute_stats(leagues_data, source_league):
    ret_arr = [leagues_data[source_league][player]['player_details'] for player in leagues_data[source_league]]
    sets_played = [leagues_data[source_league][player]['num_sets_played'] for player in leagues_data[source_league]]

    player_front = [player[:4] for player in ret_arr]
    player_stats = [player[4:] for player in ret_arr]
    clean_stats = [[float(col) if col is not None else 0.0 for col in player] for player in player_stats]
    return player_front, np.array(clean_stats), sets_played

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

def normalise_leagues_data(leagues_data, target_data, target_league):
    for league in leagues_data:

        source_players, source_stats, source_sets_played = compute_stats(leagues_data, league)
        target_players, target_stats, target_sets_played = compute_stats(target_data, target_league)

        standardised_stats_numpy = standardise_columns(target_stats, source_stats)
        standardised_stats = [row.tolist() for row in standardised_stats_numpy]
        combined_players = [{
                'player_details' : r1 + r2,
                'num_sets_played': r3
            } for r1, r2, r3 in zip(source_players, standardised_stats, source_sets_played)]

        # combined_players = [p1 + p2 for p1, p2 in zip(source_players, standardised_stats)]
        for player in leagues_data[league].keys():
            filtered_stats = [stat for stat in combined_players if stat['player_details'][1] == player]
            assert len(filtered_stats) == 1
            leagues_data[league][player] = filtered_stats[0]
                
    return leagues_data

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
def combine_player_data(original_player, new_player):
    num_sets_orig, original = original_player['num_sets_played'], original_player['player_details']
    num_sets_new, new = new_player['num_sets_played'], new_player['player_details']
    combined = []
    for p1,p2 in zip(original, new):
        curr = 0
        if p1 is None or p2 is None:
            curr = p1 if p2 is None else p2
        elif is_float(p1) and is_float(p2):
            curr = int(float(p1) + float(p2))
        else:
            curr = p1
        combined.append(curr)
    return_player = {
        'num_sets_played': num_sets_orig + num_sets_new,
        'player_details': combined
    }
    return return_player

def combine_and_average(original_player, new_player):
    num_sets_orig, original = original_player['num_sets_played'], original_player['player_details']
    num_sets_new, new = new_player['num_sets_played'], new_player['player_details']
    combined = []
    for p1,p2 in zip(original, new):
        curr = 0
        if p1 is None or p2 is None:
            curr = p1 if p2 is None else p2
        elif is_float(p1) and is_float(p2):
            curr = int((num_sets_orig * float(p1) + num_sets_new * float(p2)) / (num_sets_orig + num_sets_new))
        else:
            curr = p1
        combined.append(curr)
    return combined

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
        sorted_other_leagues = sorted(other_leagues, key=lambda p: int(p[1]['player_details'][mapping['attack_total']]) + int(p[1]['player_details'][mapping['serve_total']]), reverse=True)
        top_league, top_player_stat = sorted_other_leagues[0]
        for curr_league, player_stats in sorted_other_leagues[1:]:
            top_player_stat = combine_player_data(top_player_stat, player_stats)
            
        new_shuffled_leagues_data[top_league][player] = top_player_stat
    
            
    return new_shuffled_leagues_data


class Form:
    def __init__(self):
        pass
    
    def model_get_players(self, teamA, teamB, matches_processed):
        pass
    
    def ammend_sliding_window(self, all_teams_matches, new_match):
        # Ammends sliding window
        return all_teams_matches
    
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
        all_teams = {}
        all_teams_processed = {}
        
        for match in matches:            
            teamA = match['teamA']
            teamB = match['teamB']
            teamA_players = match['teamA-players']
            teamB_players = match['teamB-players']
            teamA_starters = match['teamA-starting']
            teamB_starters = match['teamB-starting']
            process_team(all_teams, teamA, teamA_players, teamA_starters, mapping)
            process_team(all_teams, teamB, teamB_players, teamB_starters, mapping)
            
        all_teams_processed = sort_starters(all_teams, all_teams_processed, mapping)

        league_data = compute_training_leagues(training_year, league)
        target_data = compute_target_league(all_teams_processed, league)

        league_data = normalise_leagues_data(league_data, target_data, league)
        
        if len(league_data.keys()) > 1: # Not VNL
            league_data_reshuffled = shuffle_leagues_data(league_data)
        else:
            league_data_reshuffled = league_data
        
        

        for team in all_teams_processed:
            roles = ['OH', 'MB', 'O', 'S', 'L']
            for role in roles:
                players_that_role = all_teams_processed[team][role]
                for i in range(len(players_that_role)):
                    player = players_that_role[i]
                    name = player[1]
                    jersey = player[0]
                    player_big = {
                        'player_details' : player,
                        'num_sets_played': 1 if jersey not in all_teams_processed[team]['num_sets_played'] else all_teams_processed[team]['num_sets_played'][jersey]
                    }
                    for league in league_data_reshuffled:
                        if name in league_data_reshuffled[league]:
                            new_player_data = league_data_reshuffled[league][name]
                            combined_data = combine_and_average(player_big, new_player_data)
                            players_that_role[i] = combined_data
                            
        return all_teams_processed