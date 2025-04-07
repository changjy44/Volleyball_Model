import os
import sys
import json
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']
ANALYSIS = 'base_1'

from helper.columns_starters import ALL_COLS
from helper.generate_pat import generate_pat_model_custom
from base_1.predict_ml_class import get_players
from base_1.predict_ml_class import Base1

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i

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

def generate_pat(year, train_matches, predict_matches, league):
    points_to_win = 5
    id = 0
    for match in predict_matches:
        teamA = match['teamA']
        teamB = match['teamB']

        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        teamA_aggregated_stats = train_matches[teamA]['all_stats_per_set']
        teamB_aggregated_stats = train_matches[teamB]['all_stats_per_set']
                
        teamA_players = get_players(teamA, teamB, teamB_aggregated_stats, train_matches, year)
        teamB_players = get_players(teamB, teamA, teamA_aggregated_stats, train_matches, year)

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
            training_year = YEARS[year_index]
            prediction_year = YEARS[year_index + 1]
            
            print(f'doing {league}/{prediction_year}')
            
            # Preprocess data
            with open(f'data/{league}/{training_year}-{league}-data-final-v3.json') as f:
                matches = json.load(f)
                
            with open(f'data/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
                predict_matches = json.load(f)
                
            model = Base1()
            
            all_teams_processed = model.generate_analysis_data(matches, predict_matches, training_year, league)

            league_dir = f"{ANALYSIS}/{league}"
            if not os.path.exists(league_dir):
                os.makedirs(league_dir)
            
            directory = f"{ANALYSIS}/{league}/{prediction_year}"
            if not os.path.exists(directory):
                os.makedirs(directory)
                
            # Save processed
            with open(f'{ANALYSIS}/{league}/{prediction_year}/{prediction_year}-train-matches.json', 'w') as f:
                json.dump(all_teams_processed, f)

            # Generate pat files
            generate_pat(prediction_year, all_teams_processed, predict_matches, league)
        
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '1':
        execute_pat()
    else:
        preprocess()


        


        