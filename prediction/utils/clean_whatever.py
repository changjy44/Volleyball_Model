import os
import sys
import json
import csv


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']
# LEAGUES = ['japan']
# LEAGUES = ['poland', 'italy', 'france', 'japan']
# LEAGUES = ['italy', 'france', 'japan']

YEARS = ['2021', '2022', '2023', '2024']
players_per_role = {
    'OH': 2,
    'MB': 2,
    'S' : 1,
    'O' : 1
}


from helper.columns_starters import ALL_COLS

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i

def compute_team(leagues_data, players, starters, team, league):
    for player, starter in zip(players, starters):
        player_name = player[1]

        if player_name not in leagues_data[league]:
            leagues_data[league][player_name] = team
        elif leagues_data[league][player_name] != team:
            print(f'{player_name}, {leagues_data[league][player_name]}, {team}') 
        

    return leagues_data

def clean(team, players, starters, match_id):
    
    for role in players_per_role:
        # for num in range(players_per_role[role]):
        players_that_role = [player for player in players if player[3] == role]
        if len(players_that_role) != players_per_role[role]:
            print(f'{match_id}, {team}, {role},  {len(players_that_role)}, {players_per_role[role]}')
        
    for i in range(len(players)):
        player = players[i]
        starter = starters[i]
        name = player[1]
        
            
    return players, starters


for league in LEAGUES:
    for year_index in range(len(YEARS)):

        prediction_year = YEARS[year_index]
        
        # Preprocess data
        with open(f'data/{league}/{prediction_year}-{league}-data-final-v3.json') as f:
            matches = json.load(f)
            
        if prediction_year != '2021':
            with open(f'data/{league}/{prediction_year}_odds.csv') as f:
                csv_obj = csv.reader(f)
                odds_all = []
                for line in csv_obj:
                    odds_all.append(line)
        else:
            odds_all = [None] * len(matches)


        teams = {}
        
        new_matches = []

        for match, odd in zip(matches, odds_all):
            new_match = match
            if prediction_year != '2021':
                teamAOdd, teamBOdd, oddsA, oddsB = odd
                new_match['oddsA'] = oddsA
                new_match['oddsB'] = oddsB
                new_match['teamAOdd'] = teamAOdd
                new_match['teamBOdd'] = teamBOdd
            
            # match_id = match['match_id']
            
            # teamA = match['teamA']
            # teamB = match['teamB']
            # teamA_players = match['teamA-players']
            # teamB_players = match['teamB-players']
            # teamA_starters = match['teamA-starting']
            # teamB_starters = match['teamB-starting']
            
            # new_A_players, new_A_starters = clean(teamA, teamA_players, teamA_starters, match_id)
            # new_B_players, new_B_starters = clean(teamB, teamB_players, teamB_starters, match_id)
            
            # new_match['teamA-players'] = new_A_players
            # new_match['teamB-players'] = new_B_players
            # new_match['teamA-starting'] = new_A_starters
            # new_match['teamB-starting'] = new_B_starters

            new_matches.append(new_match)
        
        # sorted_new_matches = sorted(new_matches, key=lambda x: datetime.strptime(x["match_date"], "%Y-%m-%d"))
        
        with open(f'data_better/{league}/{prediction_year}-{league}-data-final-v3.json', 'w') as f:
            json.dump(new_matches, f)
            

            
        
            
        
                
            


