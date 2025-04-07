import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']
ANALYSIS = 'base'

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

# Returns players from team playing, with modified stats
def get_players(team, other_team, other_aggregated_stats, train_matches, year):
    players = []
    for role in players_per_role:
        count = players_per_role[role]
        for i in range(count):
            player = train_matches[team][role][i]
            players.append(player)
   
    return players

class Base:
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