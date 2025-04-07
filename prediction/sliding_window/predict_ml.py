import os
import sys
import json
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

ANALYSIS = 'sliding_window'
LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']

DATA_PATH = 'data_sorted'

from helper.columns_starters import ALL_COLS
from helper.generate_pat import generate_pat_model

from sliding_window.predict_ml_class import SlidingWindow
from sliding_window.predict_ml_class import process_data
from sliding_window.predict_ml_class import ammend_sliding_window

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


def preprocess():
    for league in LEAGUES:
        for year_index in range(len(YEARS) - 1):
            all_teams_matches = {}
            training_year = YEARS[year_index]
            prediction_year = YEARS[year_index + 1]

            print(f'doing {league}/{prediction_year}')
            
            # Preprocess data
            with open(f'{DATA_PATH}/{league}/{training_year}-{league}-data-final-v3.json') as f:
                matches = json.load(f)
                
            with open(f'{DATA_PATH}/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
                predict_matches = json.load(f)
                
            model = SlidingWindow()
            all_teams_matches = model.generate_analysis_data(matches, predict_matches, training_year, league)

            id = 0
            for predict_match in predict_matches:
                teamA = predict_match['teamA']
                teamB = predict_match['teamB']
                
                all_teams_processed = process_data(all_teams_matches)
                ammend_sliding_window(predict_match, all_teams_matches)
                
                if teamA not in all_teams_processed or teamB not in all_teams_processed:
                    continue
                else:
                    generate_pat_one_match(id, prediction_year, all_teams_processed, predict_match, league)
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
