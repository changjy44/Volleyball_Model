import os
import sys
import json
import subprocess

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
from helper.generate_pat import generate_pat_model_custom

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i

def generate_pat_one_match(id, year, train_matches, match, league, model):
    points_to_win = 5
    teamA = match['teamA']
    teamB = match['teamB']
    
    teamA_players, teamB_players = model.model_get_players(teamA, teamB, train_matches)

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

    generate_pat_model_custom(id, teamA, teamB, teamA_players, teamB_players, 
                                train_matches, points_to_win, outpath, league)
    
from sliding_window_1.predict_ml_class import SlidingWindow_1
from sliding_window_1.predict_ml_class import process_data
from sliding_window_1.predict_ml_class import ammend_sliding_window

def preprocess():
    for league in LEAGUES:
        for year_index in range(len(YEARS) - 1):
            # all_teams = {}

            training_year = YEARS[year_index]
            prediction_year = YEARS[year_index + 1]

            print(f'doing {league}/{prediction_year}')

            with open(f'{DATA_PATH}/{league}/{training_year}-{league}-data-final-v3.json') as f:
                matches = json.load(f)
                
            with open(f'{DATA_PATH}/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
                predict_matches = json.load(f)
                
            model = SlidingWindow_1()
            
            all_teams_matches = model.generate_analysis_data(matches, predict_matches, training_year, league)

            # Run sliding window
            id = 0
            for match in predict_matches:
                teamA = match['teamA']
                teamB = match['teamB']

                all_teams_processed = process_data(all_teams_matches)
                ammend_sliding_window(match, all_teams_matches)
                
                if teamA not in all_teams_processed or teamB not in all_teams_processed:
                    continue
                else:
                    generate_pat_one_match(id, prediction_year, all_teams_processed, match, league, model)
                    id += 1
            

executable = r"C:\\Program Files\\Process Analysis Toolkit\\Process Analysis Toolkit 3.5.1\\PAT3.Console.exe"

def execute_pat():
# Run pat files
    for league in LEAGUES:
        for year_index in range(len(YEARS) - 1):
            training_year = YEARS[year_index]
            prediction_year = YEARS[year_index + 1]
            print(f'doing {league} {prediction_year}')
            
            args = ["-pcsp", "-d", f"C:\\Users\\Jingyan\\Desktop\\fyp\\prediction\\{ANALYSIS}\\{league}\\{prediction_year}", 
                    f"C:\\Users\\Jingyan\\Desktop\\fyp\\prediction\\{ANALYSIS}\\{league}\\{prediction_year}\\output.txt"]
            
            result = subprocess.run([executable] + args, capture_output=True, text=True)

            
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '1':
        execute_pat()
    else:
        preprocess()

