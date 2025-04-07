import os
import sys
from statistics import mean

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']
ANALYSIS = 'base_1'

from helper.columns_starters import ALL_COLS
from helper.general_processing import process_team
from helper.general_processing import sort_starters
from helper.general_processing import add_matches


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


def modify_player(original_player, team, train_matches, attack_predictions, is_setter):
    player = original_player.copy()
    
    all_stats = train_matches[team]['all_stats']
    
    # Modify attack
    if not is_setter:
        if attack_predictions[0] == 1:
            # Do not change
            pass
        else:
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
            
    return player


def normalise_attack_all(home_players):
    attack_cols = ['attack_points', 'attack_errors', 'attack_total']
    attack_with_total = []
    for col in attack_cols:
        stat =  sum([int(player[mapping[col]]) for player in home_players])
        attack_with_total.append(stat)
    total_service = attack_with_total[2]
    return [attack_with_total[0] / total_service, attack_with_total[1] / total_service]

# Returns players from team playing, with modified stats
def get_players(team, other_team, other_aggregated_stats, train_matches,  year):
    all_other_matches = [(match['home_players'], match['num_sets']) for match in train_matches[team]['matches'] if match['other_team'] == other_team]
    
    if len(all_other_matches) == 0:
        teamA_attack = [1, 1]
    else:
        all_other_matches_normalised = [normalise_attack_all(players) for players, num_sets in all_other_matches]
        teamA_attack = [mean(stats) for stats in zip(*all_other_matches_normalised)]
        
    players = []
    for role in players_per_role:
        count = players_per_role[role]
        for i in range(count):
            player = train_matches[team][role][i]
            modified_player = modify_player(player, team, train_matches, teamA_attack, role == 'S')
            players.append(modified_player)
   
    return players


class Base1:
    def __init__(self):
        pass
    
    def model_get_players(self, teamA, teamB, matches_processed):
        pass
    
    def ammend_sliding_window(self, all_teams_matches, new_match):
        # Ammends sliding window
        return all_teams_matches
    
    def generate_analysis_stats(self, all_teams_processed, team, other_team, match_id, year, league):
        spike_rates, serve_rates = [], []
                
        team_aggregated_stats = all_teams_processed[team]['all_stats_per_set']
        other_aggregated_stats = all_teams_processed[other_team]['all_stats_per_set']
                
        team_players = get_players(team, other_team, other_aggregated_stats, all_teams_processed, year)
        
        index = 0
        for role in players_per_role:
            count = players_per_role[role]
            for i in range(count):
                player = team_players[index]
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

        prediction_year = str(int(training_year) + 1)
              
        for match in matches:            
            teamA = match['teamA']
            teamB = match['teamB']
            teamA_players = match['teamA-players']
            teamB_players = match['teamB-players']
            teamA_starters = match['teamA-starting']
            teamB_starters = match['teamB-starting']
            all_teams = process_team(all_teams, teamA, teamA_players, teamA_starters, mapping)
            all_teams = process_team(all_teams, teamB, teamB_players, teamB_starters, mapping)
        
        all_teams_processed = sort_starters(all_teams, all_teams_processed, mapping)
        add_matches(all_teams_processed, matches)

        return all_teams_processed