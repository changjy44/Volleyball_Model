import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
YEARS = ['2021', '2022', '2023', '2024']
DATA_PATH = 'data'

from helper.betting_helper import random_betting
from helper.betting_helper import favourite_betting
from helper.betting_helper import against_betting
from helper.betting_helper import model_betting
from helper.betting_helper import kellybet
from helper.betting_helper import difference_betting

MAGIC_NUMBER = 5
print_var = False

def analyse_bet(analysis, betting):
    for league in LEAGUES:
        prediction_success = []
        model_percents = []
        kelly_percents = []
        
        random_percents = []
        favourite_percents = []
        against_percents = []
        
        for year_index in range(len(YEARS) - 1):
            training_year = YEARS[year_index]
            prediction_year = YEARS[year_index + 1]
            
            if print_var:
                print(f"============={league}/{prediction_year}===============")
            
            with open(f'base/{league}/{prediction_year}/{prediction_year}-train-matches.json') as f:
                train_matches_processed = json.load(f)
                
            with open(f'{DATA_PATH}/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
                predict_matches = json.load(f)

            with open(f'{analysis}/{league}/{prediction_year}/output.txt') as f:
                splitted = f.read().split(".pcsp")[1:]
                pre_probability_arr = [prob.split("[")[1].split(",")[0] for prob in splitted]
                probability_arr = pre_probability_arr
                probability_arr = [0.5 + ((MAGIC_NUMBER * (float(prob) - 0.5)) / 5) for prob in pre_probability_arr]
                    
            odds_all = [[match['teamAOdd'], match['teamBOdd'], match['oddsA'], match['oddsB']] for match in predict_matches]

            id = 0
            correctly_predicted = 0

            for match in predict_matches:
                teamA = match['teamA']
                teamB = match['teamB']

                teamA_score = match['teamA_score']
                teamB_score = match['teamB_score']
                teamA_wins_result = teamA_score > teamB_score
                
                
                if teamA not in train_matches_processed or teamB not in train_matches_processed:
                    continue
            
                probability = float(probability_arr[id])

                teamA_wins_predicted = probability > 0.5

                if teamA_wins_predicted == teamA_wins_result:
                    correctly_predicted += 1

                id += 1
            
            if print_var:
                print(f"Prediction result {prediction_year}: {correctly_predicted}/{id}")
                print(f"Prediction rate {prediction_year}: {correctly_predicted/id}")
            
            prediction_success.append(correctly_predicted)
                
            if betting:
                random_percent = random_betting(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr)
                favourite_percent = favourite_betting(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr)
                against_percent = against_betting(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr)
                model_percent = model_betting(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr)
                # kellybet(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr, limit=1)
                kelly_percent = kellybet(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr, limit=0.02)
                # difference_betting(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr, margin=0.05)
                # difference_betting(league, prediction_year, predict_matches, train_matches_processed, odds_all, probability_arr, margin=0.1)
                
                model_percents.append(round(model_percent, 2))
                kelly_percents.append(round(kelly_percent, 2))
                random_percents.append(round(random_percent, 2))
                favourite_percents.append(round(favourite_percent, 2))
                against_percents.append(round(against_percent, 2))
            
                                                
                        
        combined =  [str(item) for item in random_percents + favourite_percents + against_percents]
        print(','.join(combined))

                
if __name__ == '__main__':
    # LEAGUES = ['poland', 'italy', 'france', 'japan']
    # LEAGUES = ['vnl']
    # DATA_PATH = 'data_sorted'
    analysis_list = ['base']
    # analysis_list = ['base_1']
    # analysis_list = ['sliding_window_1']
    # analysis_list = ["sliding_window"]
    # analysis_list = ['form']
    
    for analysis in analysis_list:
        analyse_bet(analysis, True)