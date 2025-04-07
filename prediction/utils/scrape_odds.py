import json
import csv
from datetime import datetime
from unidecode import unidecode

LEAGUES = ['poland', 'italy', 'france', 'japan']
# LEAGUES = ['japan']
YEARS = ['2021', '2022', '2023', '2024']

def remove_accents(text):
    return unidecode(text)

def map_name(name1):
    if name1 == 'Osaka Sakai':
        name1 = 'SAKAI Blazers'
    elif name1 == 'Osaka Bluteon':
        name1 = 'Panasonic PANTHERS'
    elif name1 == 'Cuprum Gorzow':
        name1 = 'Cuprum Lubin'
    elif name1 == 'Norwid Czestochowa':
        name1 = 'Exact Systems Hemarpol Częstochowa'
    elif name1 == 'Saturnia Acicastello':
        name1 = 'Farmitalia Catania'
    elif name1 == 'Illacaise':
        name1 = "saint-jean d'illac"
    return name1

def process_team_name(name):
    name1 = name.strip()
    name2 = remove_accents(name1)
    name3 = name2.lower()
    name4 = name3.replace('.', ' ').replace('-', ' ')
    name5 = ' '.join(name4.split())
    return name5

def check_name(bet_name, game_names):
    split_bet = bet_name.strip().split()
    split_game = [name.split() for name in game_names]
    target = list(filter(lambda arr: 
        all(elem in arr for elem in split_bet) if len(split_bet) < len(arr) else all(elem in split_bet for elem in arr)
        , split_game))
    target_nice = [' '.join(name) for name in target]
    return target_nice

def get_teams_bets(matches):
    seen = set()
    
    for odd in matches:
        teamA, teamB, oddsA, oddsB = odd
        teamA_processed = teamA.strip()
        teamB_processed = teamB.strip()
        if teamA_processed not in seen:
            seen.add(teamA_processed)
            
        if teamB_processed not in seen:
            seen.add(teamB_processed)
            
    return list(seen)

def get_teams_matches(matches):
    seen = set()
    
    for match in matches:
        teamA = match['teamA']
        teamB = match['teamB']
        teamA_processed = process_team_name(teamA.strip())
        teamB_processed = process_team_name(teamB.strip())
        if teamA_processed not in seen:
            seen.add(teamA_processed)
            
        if teamB_processed not in seen:
            seen.add(teamB_processed)
        
    return list(seen)

def assign_bets(matches, bets, unique_teams):
    # first_p = 0
    seen_bets = [False for bet in bets]
    assign = [() for match in matches]
    
    for i in range(len(matches)):
        match = matches[i]
        
        if int(match['match_id']) == 27429 or int(match['match_id']) == 27428:
            continue
        
        teamA = match['teamA']
        teamB = match['teamB']
        teamA_processed = process_team_name(teamA.strip())
        teamB_processed = process_team_name(teamB.strip())
        
        pointer = 0
        while pointer < len(seen_bets):
            if seen_bets[pointer]:
                pointer += 1
            else:
                teamA_bet, teamB_bet, oddsA, oddsB = bets[pointer]
                processed_betA = process_team_name(map_name(teamA_bet.strip()))
                processed_betB = process_team_name(map_name(teamB_bet.strip()))
                if (check_name(processed_betA, unique_teams)[0] == teamA_processed and 
                    check_name(processed_betB, unique_teams)[0] == teamB_processed):
                    assign[i] = (teamA_bet, teamB_bet, oddsA, oddsB)
                    seen_bets[pointer] = True
                    break
                else:
                    pointer += 1
        
    return assign, seen_bets

def order_bets(matches, sorted_matches, bets_all):
    mapping = {}
    
    for match, bet in zip(sorted_matches, bets_all):
        if bet[0] == '':
            bet = [match['teamA'], match['teamB'], 0, 0]
            
        bet[1] = bet[1].strip()
            
        mapping[match['match_id']] = bet
    
    csvFile = []
    for match in matches:
        csvFile.append(mapping[match['match_id']])
    
    return csvFile 

for league in LEAGUES:
    for year_index in range(len(YEARS) - 1):
        prediction_year = YEARS[year_index + 1]
        
        with open(f'data/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
            predict_matches = json.load(f)
            
        with open(f'data/{league}/{prediction_year}_odds.csv', encoding='utf-8-sig') as f:
            csv_obj = csv.reader(f)
            odds_all = []
            for line in csv_obj:
                odds_all.append(line)
                
        sorted_matches = sorted(predict_matches, key=lambda match:(datetime.strptime(match['match_date'], "%Y-%m-%d") , int(match['match_id'])), reverse=True)
        
        unique_teams = get_teams_matches(sorted_matches)
        bet_teams = get_teams_bets(odds_all)
        
        csvFile = order_bets(predict_matches, sorted_matches, odds_all)
        
        with open(f'data/{league}/{prediction_year}_odds_v2.csv', 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(csvFile)
        
        