import os
import sys
import json
import subprocess

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

from pf2.predict_ml_class import PF2

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i


def generate_pat(year, train_matches, predict_matches, all_teams_processed_model, league, model):
    points_to_win = 5
    id = 0
    for match in predict_matches:
        teamA = match['teamA']
        teamB = match['teamB']

        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        teamA_players, teamB_players = model.model_get_players(teamA, teamB, train_matches, all_teams_processed_model, year)

        id_string = str(id)
        while len(id_string) != 3:
            id_string = '0' + id_string

        outpath = f"{ANALYSIS}/{league}/{year}/{id_string}_{teamA}vs{teamB}.pcsp"
        generate_pat_model_custom(id, teamA, teamB, teamA_players, teamB_players, 
                                  train_matches, points_to_win, outpath, league)
        id += 1


def preprocess():
    for league in LEAGUES:
        for year_index in range(len(YEARS) - 1):
            all_teams_processed = {}
            training_year = YEARS[year_index]
            prediction_year = YEARS[year_index + 1]
            
            # Preprocess data
            with open(f'data/{league}/{training_year}-{league}-data-final-v3.json') as f:
                matches = json.load(f)
                
            with open(f'data/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
                predict_matches = json.load(f)
                
            model = PF2()
            
            all_teams_processed_normalised, all_teams_processed_model = model.generate_ml_data(matches)
            
            league_dir = f"{ANALYSIS}/{league}"
            if not os.path.exists(league_dir):
                os.makedirs(league_dir)
            
            directory = f"{ANALYSIS}/{league}/{prediction_year}"
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            # Save processed
            with open(f'{ANALYSIS}/{league}/{prediction_year}/{prediction_year}-train-matches.json', 'w') as f:
                json.dump(all_teams_processed_normalised, f)
                
            # Generate pat files
            generate_pat(prediction_year, all_teams_processed_normalised, predict_matches, all_teams_processed_model, league, model)
            

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
