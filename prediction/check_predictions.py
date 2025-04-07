import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
# LEAGUES = ['poland', 'italy', 'france', 'japan']
# LEAGUES = ['vnl']
YEARS = ['2021', '2022', '2023', '2024']

players_per_role = {
    'OH': 2,
    'MB': 2,
    'S' : 1,
    'O' : 1
}

from helper.columns_starters import ALL_COLS
from helper.general_processing import process_team
from helper.general_processing import sort_starters
from sliding_window.predict_ml_class import SlidingWindow
from sliding_window_1.predict_ml_class import SlidingWindow_1
from base_1.predict_ml_class import Base1
from base.predict_ml_class import Base
from form.predict_ml_class import Form

TARGET_MODEL = Form

from ml_predictions.ml_helper import compute_serve
from ml_predictions.ml_helper import compute_spike

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i

def generate_processed_data(matches):
    all_teams = {}
    all_teams_processed = {}
    for match in matches:
        # print(match['match_id'])
        
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

def generate_actual_stats(players, match_id, year, league):
    spike_rates, serve_rates = [], []

    # Return spike --> OH1, OH2, MB1, MB2, O
    # Return serve --> OH1, OH2, MB1, MB2, O, S
    for role in players_per_role:
        players_that_role = [player for player in players if player[3] == role]
        assert len(players_that_role) == players_per_role[role]
        for player in players_that_role:
            serve_row = compute_serve(player, match_id, role, year, league) 
            serve_rates.append(serve_row)
            if role != 'S':
                spike_row = compute_spike(player, match_id, role, year, league) 
                spike_rates.append(spike_row)

    return spike_rates, serve_rates

def generate_predicted_stats(processed_matches, team, match_id, year, league):
    spike_rates, serve_rates = [], []
    for role in players_per_role:
        count = players_per_role[role]
        for i in range(count):
            player = processed_matches[team][role][i]
            serve_row = compute_serve(player, match_id, role, year, league) 
            serve_rates.append(serve_row)
            if role != 'S':
                spike_row = compute_spike(player, match_id, role, year, league) 
                spike_rates.append(spike_row)
    return spike_rates, serve_rates

def swap_if_equal(spike_actual, serve_actual, spike_pred, serve_pred, index):
    if spike_actual[index][3] == spike_pred[index + 1][3]:
        spike_pred[index], spike_pred[index + 1] = spike_pred[index + 1], spike_pred[index]
        serve_pred[index], serve_pred[index + 1] = serve_pred[index + 1], serve_pred[index]

def check_swap(spike_actual, serve_actual, spike_pred, serve_pred):
    swap_if_equal(spike_actual, serve_actual, spike_pred, serve_pred, 0)
    swap_if_equal(spike_actual, serve_actual, spike_pred, serve_pred, 2)

def compare_predictions(predict_matches, training_matches_processed, 
                        prediction_matches_processed, all_teams_matches, 
                        target_model, year, league):
    spike_results = []
    serve_results = []
    for match in predict_matches:
        match_id = match['match_id']
        teamA = match['teamA']
        teamB = match['teamB']

        if teamA not in training_matches_processed or teamB not in training_matches_processed:
            continue
        team_map = {
            teamA: match['teamA-players'],
            teamB: match['teamB-players']
        }
        
        all_teams_processed = target_model.ammend_sliding_window(all_teams_matches, match)
        
        for team in team_map:
            other_team = teamB if team == teamA else teamA
            spike_actual, serve_actual = generate_actual_stats(team_map[team], match_id, year, league)
            
            spike_pred, serve_pred = generate_predicted_stats(prediction_matches_processed, team, match_id, year, league)
            check_swap(spike_actual, serve_actual, spike_pred, serve_pred)

            spike_train, serve_train = generate_predicted_stats(training_matches_processed, team, match_id, year, league)
            check_swap(spike_actual, serve_actual, spike_train, serve_train)

            spike_ml, serve_ml = target_model.generate_analysis_stats(all_teams_processed, team, other_team, match_id, year, league)
            check_swap(spike_actual, serve_actual, spike_ml, serve_ml)

            return_spikes = [p1 + p2[3:] + p3[3:] + p4[3:] for p1,p2,p3,p4 in zip(spike_actual, spike_pred, spike_train, spike_ml)]
            return_serve = [p1 + p2[3:] + p3[3:] + p4[3:] for p1,p2,p3,p4 in zip(serve_actual, serve_pred, serve_train, serve_ml)]

            spike_results.append(return_spikes)
            serve_results.append(return_serve)
    
    return spike_results, serve_results



def preprocess():
    spike_file_name = 'spike_file.log'
    serve_file_name = 'serve_file.log'
    spike_file = open(spike_file_name, 'w', encoding='utf-8')
    serve_file = open(serve_file_name, 'w', encoding='utf-8')
    target_model = TARGET_MODEL()
    
    for league in LEAGUES:
        for year_index in range(len(YEARS) - 1):
            training_year = YEARS[year_index]
            prediction_year = YEARS[year_index + 1]
            
            # Preprocess data
            with open(f'data/{league}/{training_year}-{league}-data-final-v3.json') as f:
                matches = json.load(f)
                
            with open(f'data/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
                predict_matches = json.load(f)

            training_matches_processed = generate_processed_data(matches)
            prediction_matches_processed = generate_processed_data(predict_matches)
            all_teams_matches = target_model.generate_analysis_data(matches, predict_matches, training_year, league)

            spike_results, serve_results = compare_predictions(predict_matches, training_matches_processed, 
                                                               prediction_matches_processed, 
                                                               all_teams_matches, target_model, prediction_year, league)
            
            # Flatten
            for res in spike_results:
                for row in res:
                    str_row = [str(item) for item in row]
                    spike_file.write(','.join(str_row))
                    spike_file.write('\n')

            for res in serve_results:
                for row in res:
                    str_row = [str(item) for item in row]
                    serve_file.write(','.join(str_row))
                    serve_file.write('\n')

    spike_file.close()
    serve_file.close()

if __name__ == '__main__':
    preprocess()
