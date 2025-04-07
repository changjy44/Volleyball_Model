# in pf2, we remove the error columns

import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

ANALYSIS = 'pf2'
# LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
LEAGUES = ['vnl']
YEARS = ['2021', '2022', '2023', '2024']

block_dig_cols = ['block_points', 'block_touches', 'dig_sucess']
reception_cols = ['reception_perfect', 'reception_attempts']

from helper.columns_starters import ALL_COLS
from helper.generate_pat import generate_pat_model_custom
from helper.general_processing import sort_starters
from ml_predictions.bayesian_model import BayesianModel

from helper.general_processing import process_team_reception_serve_agg
from helper.general_processing import normalise_block_dig_v2
from helper.general_processing import normalise_reception_v2

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

def modify_player(original_player, team, train_matches, attack_predictions, serve_predictions, is_setter):
    player = original_player.copy()
    
    all_stats = train_matches[team]['all_stats']
    
    # Modify attack
    if not is_setter:
        attack_total_all = int(all_stats[mapping['attack_total']])
        att_succ = max(attack_predictions[0], 0)
        att_err = max(attack_predictions[1], 0)
        
        new_attack_points = attack_total_all * float(att_succ)
        new_attack_errors = attack_total_all * float(att_err)
        
        new_att_points = int(new_attack_points * (int(player[mapping['attack_points']]) / int(all_stats[mapping['attack_points']])))
        new_att_errors = int(new_attack_errors * (int(player[mapping['attack_errors']]) / int(all_stats[mapping['attack_errors']])))
                
        player[mapping['attack_points']] = int((int(player[mapping['attack_points']]) + new_att_points) / 2)
        player[mapping['attack_errors']] = int((int(player[mapping['attack_errors']]) + new_att_errors) / 2)
        player[mapping['attack_attempts']] = int(player[mapping['attack_total']]) - player[mapping['attack_points']] - player[mapping['attack_errors']]

        assert player[mapping['attack_attempts']] > 0
    else:
        player[mapping['attack_points']] = int(player[mapping['attack_points']])
        player[mapping['attack_errors']] = int(player[mapping['attack_errors']])
        player[mapping['attack_attempts']] = int(player[mapping['attack_attempts']])
    
    # Modify service
    service_total_all = int(all_stats[mapping['serve_total']])
    svc_succ = max(serve_predictions[0], 0)
    svc_err = max(serve_predictions[1], 0)
    new_serve_points = service_total_all * float(svc_succ)
    new_serve_errors = service_total_all * float(svc_err)
    
    new_svc_points = int(new_serve_points * (int(player[mapping['serve_points']]) / int(all_stats[mapping['serve_points']])))
    new_svc_errors = int(new_serve_errors * (int(player[mapping['serve_errors']]) / int(all_stats[mapping['serve_errors']])))
    
    player[mapping['serve_points']] = int((int(player[mapping['serve_points']]) + new_svc_points) / 2)
    player[mapping['serve_errors']] = int((int(player[mapping['serve_errors']]) + new_svc_errors) / 2)
    player[mapping['serve_attempts']] = int(player[mapping['serve_total']]) - player[mapping['serve_points']] - player[mapping['serve_errors']]
    
    assert player[mapping['serve_attempts']] > 0
    
    return player

# Returns players from team playing, with modified stats
def get_players(team, other_aggregated_stats, train_matches, all_teams_processed_model, year):
    model = all_teams_processed_model[team]
    block_dig_other = [other_aggregated_stats[mapping[col]] for col in block_dig_cols]
    reception_other = [other_aggregated_stats[mapping[col]] for col in reception_cols]
    
    teamA_attack = model.predict_attack(block_dig_other)[0]
    teamA_service = model.predict_service(reception_other)[0]
    
    if not all([att > 0 for att in teamA_attack]):
        print(team, year, 'att')
    if not all([svc > 0 for svc in teamA_service]):
        print(team, year, 'svc')

    players = []
    for role in players_per_role:
        count = players_per_role[role]
        for i in range(count):
            player = train_matches[team][role][i]
            modified_player = modify_player(player, team, train_matches, teamA_attack, teamA_service, role == 'S')
            players.append(modified_player)
   
    return players
    

def generate_pat(year, train_matches, predict_matches, all_teams_processed_model, league):
    points_to_win = 5
    id = 0
    for match in predict_matches:
        teamA = match['teamA']
        teamB = match['teamB']

        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        teamA_aggregated_stats = train_matches[teamA]['all_stats_per_set']
        teamB_aggregated_stats = train_matches[teamB]['all_stats_per_set']
        
        teamA_players = get_players(teamA, teamB_aggregated_stats, train_matches, all_teams_processed_model, year)
        teamB_players = get_players(teamB, teamA_aggregated_stats, train_matches, all_teams_processed_model, year)
            
        id_string = str(id)
        while len(id_string) != 3:
            id_string = '0' + id_string

        outpath = f"{ANALYSIS}/{league}/{year}/{id_string}_{teamA}vs{teamB}.pcsp"
        generate_pat_model_custom(id, teamA, teamB, teamA_players, teamB_players, 
                                  train_matches, points_to_win, outpath, league)
        id += 1

def add_matches(all_teams_processed, matches):
    for match in matches:
        teamA = match['teamA']
        teamB = match['teamB']
        num_sets = int(match['teamA_score']) + int(match['teamB_score'])
        rebased_match_A = {
            'match_id' : match['match_id'],
            'num_sets': int(match['teamA_score']) + int(match['teamB_score']),
            'home_players': match['teamA-players'],
            'away_players': match['teamB-players'],
        }
        rebased_match_B = {
            'match_id' : match['match_id'],
            'num_sets': int(match['teamA_score']) + int(match['teamB_score']),
            'home_players': match['teamB-players'],
            'away_players': match['teamA-players'],
        }
        if 'matches' not in all_teams_processed[teamA]:
            all_teams_processed[teamA]['total_sets'] = 0
            all_teams_processed[teamA]['matches'] = []
        
        if 'matches' not in all_teams_processed[teamB]:
            all_teams_processed[teamB]['total_sets'] = 0
            all_teams_processed[teamB]['matches'] = []
            
        all_teams_processed[teamA]['total_sets'] += num_sets
        all_teams_processed[teamB]['total_sets'] += num_sets
        all_teams_processed[teamA]['matches'].append(rebased_match_A)
        all_teams_processed[teamB]['matches'].append(rebased_match_B)
        
    return all_teams_processed

def normalise_attacks(all_teams_processed_matches, team, home_players):
    attacks = [0 for i in range(6)]
    attack_roles = ['OH', 'MB', 'O']
    for i in range(len(attack_roles)):
        role = attack_roles[i]
        jerseys =  [player[0] for player in all_teams_processed_matches[team][role]]
        role_players = [player for player in home_players if player[3] == role or (player[3] not in attack_roles and player[0] in jerseys)]
        attack_points = sum([int(player[mapping['attack_points']]) for player in role_players])
        attack_errors = sum([int(player[mapping['attack_errors']]) for player in role_players])
        attack_total = sum([int(player[mapping['attack_total']]) for player in role_players])
        attacks[i] = attack_points / attack_total
        attacks[i + 3] = attack_errors / attack_total
    
    return attacks

def normalise_service(all_teams_processed_matches, team, home_players):
    service_roles = ['OH', 'MB', 'O', 'S']
    service = [0 for i in range(8)]
    for i in range(len(service_roles)):
        role = service_roles[i]
        jerseys =  [player[0] for player in all_teams_processed_matches[team][role]]
        role_players = [player for player in home_players if player[3] == role or (player[3] not in service_roles and player[0] in jerseys)]
        service_points = sum([int(player[mapping['serve_points']]) for player in role_players])
        service_errors = sum([int(player[mapping['serve_errors']]) for player in role_players])
        service_total = sum([int(player[mapping['serve_total']]) for player in role_players])
        service[i] = service_points / service_total
        service[i + 4] = service_errors / service_total 
    return service

def normalise_attack_all(all_teams_processed_matches, team, home_players):
    attack_cols = ['attack_points', 'attack_errors', 'attack_total']
    attack_with_total = []
    for col in attack_cols:
        stat =  sum([int(player[mapping[col]]) for player in home_players])
        attack_with_total.append(stat)
    total_service = attack_with_total[2]
    return [attack_with_total[0] / total_service, attack_with_total[1] / total_service]

def normalise_serve_all(all_teams_processed_matches, team, home_players):
    service_cols = ['serve_points', 'serve_errors', 'serve_total']
    service_with_total = []
    for col in service_cols:
        stat =  sum([int(player[mapping[col]]) for player in home_players])
        service_with_total.append(stat)
    total_service = service_with_total[2]
    return [service_with_total[0] / total_service, service_with_total[1] / total_service]

def normalise_block_dig(away_players, num_sets):
    block_dig = []
    for col in block_dig_cols:
        stat =  sum([int(player[mapping[col]]) for player in away_players]) / num_sets
        block_dig.append(stat)
    return block_dig
    
def normalise_reception(away_players, num_sets):
    reception = []
    for col in reception_cols:
        stat =  sum([int(player[mapping[col]]) for player in away_players]) / num_sets
        reception.append(stat)
    return reception


def normalise_matches(all_teams_processed_matches): 
    for team in all_teams_processed_matches:
        all_attacks = []
        all_service = []
        all_block_dig = []
        all_reception = []
        for match in all_teams_processed_matches[team]['matches']:
            home_players = match['home_players']
            away_players = match['away_players']
            num_sets = match['num_sets']
            
            away_spikes = sum([int(player[mapping['attack_total']]) for player in away_players])
            away_service = sum([int(player[mapping['serve_total']]) for player in away_players])
            
            # print(match['match_id'])
            attacks = normalise_attack_all(all_teams_processed_matches, team, home_players)
            service = normalise_serve_all(all_teams_processed_matches, team, home_players)
            block_dig = normalise_block_dig_v2(away_players, num_sets, away_spikes, mapping, block_dig_cols)
            reception = normalise_reception_v2(away_players, num_sets, away_service, mapping, reception_cols)

            all_attacks.append(attacks)
            all_service.append(service)
            all_block_dig.append(block_dig)
            all_reception.append(reception)
            
        all_teams_processed_matches[team]['attack'] = all_attacks
        all_teams_processed_matches[team]['service'] = all_service
        all_teams_processed_matches[team]['block_dig'] = all_block_dig
        all_teams_processed_matches[team]['reception'] = all_reception
        
    return all_teams_processed_matches

def train_model(all_teams_processed):
    all_teams_model = {}
    
    for team in all_teams_processed:
        print('========' + team + '============')
        attack, block_dig = all_teams_processed[team]['attack'], all_teams_processed[team]['block_dig']
        service, reception = all_teams_processed[team]['service'], all_teams_processed[team]['reception']
    
        model = BayesianModel()
        model.fit_attack(attack, block_dig)
        model.fit_service(service, reception)
        all_teams_model[team] = model
        
    return all_teams_model

class PF2:
    def __init__(self):
        pass
    
    def model_get_players(self, teamA, teamB, matches_processed, ml_models, year):
        teamA_aggregated_stats = matches_processed[teamA]['all_stats_per_set']
        teamB_aggregated_stats = matches_processed[teamB]['all_stats_per_set']
                
        teamA_players = get_players(teamA, teamB_aggregated_stats, matches_processed, ml_models, year)
        teamB_players = get_players(teamB, teamA_aggregated_stats, matches_processed, ml_models, year)
        
        return teamA_players, teamB_players

    def generate_ml_stats(self, ml_processed, ml_models, team, other_team, match_id, year, league):
        spike_rates, serve_rates = [], []

        team_aggregated_stats = ml_processed[team]['all_stats_per_set']
        other_aggregated_stats = ml_processed[other_team]['all_stats_per_set']
        model = ml_models[team]
        block_dig_other = [other_aggregated_stats[mapping[col]] for col in block_dig_cols]
        reception_other = [other_aggregated_stats[mapping[col]] for col in reception_cols]
        
        team_attack = model.predict_attack(block_dig_other)[0]
        team_service = model.predict_service(reception_other)[0]
        for role in players_per_role:
            count = players_per_role[role]
            for i in range(count):
                player = ml_processed[team][role][i]
                modified_player = modify_player(player, team, ml_processed, team_attack, team_service, role == 'S')
                serve_row = compute_serve(modified_player, match_id, role, year, league)
                serve_rates.append(serve_row)
                if role != 'S':
                    spike_row = compute_spike(modified_player, match_id, role, year, league)
                    spike_rates.append(spike_row)

        return spike_rates, serve_rates


    def generate_ml_data(self, matches):
        all_teams = {}
        all_teams_processed = {}
        for match in matches:            
            teamA = match['teamA']
            teamB = match['teamB']
            teamA_players = match['teamA-players']
            teamB_players = match['teamB-players']
            teamA_starters = match['teamA-starting']
            teamB_starters = match['teamB-starting']
            
            teamA_spikes = sum([int(player[mapping['attack_total']]) for player in teamA_players])
            teamA_service = sum([int(player[mapping['serve_total']]) for player in teamA_players])
            teamB_spikes = sum([int(player[mapping['attack_total']]) for player in teamB_players])
            teamB_service = sum([int(player[mapping['serve_total']]) for player in teamB_players])
            
            all_teams = process_team_reception_serve_agg(all_teams, teamA, teamA_players, teamA_starters, teamB_spikes, teamB_service, mapping, block_dig_cols, reception_cols)
            all_teams = process_team_reception_serve_agg(all_teams, teamB, teamB_players, teamB_starters, teamA_spikes, teamA_service, mapping, block_dig_cols, reception_cols)
        
        # Sort values
        all_teams_processed = sort_starters(all_teams, all_teams_processed, mapping)
        
        # Add opposing matches
        all_teams_processed_matches = add_matches(all_teams_processed, matches)
        
        # Process matches
        all_teams_processed_normalised = normalise_matches(all_teams_processed_matches)
        
        # Train model
        all_teams_processed_model = train_model(all_teams_processed_normalised)

        return all_teams_processed_normalised, all_teams_processed_model