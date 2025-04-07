import json

LEAGUES = ['france']
YEARS = ['2021', '2022', '2023', '2024']

seen = {
    
}

def check_team(match_id, team, players):
    for player in players:
        if player[1] not in seen:
            seen[player[1]] = team
        elif seen[player[1]] != team:
            print(match_id, seen[player[1]], team)

for league in LEAGUES:
    for year_index in range(len(YEARS)):
        
        training_year = YEARS[year_index]
        seen[training_year] = set()
         
        # Preprocess data
        with open(f'data/{league}/{training_year}-{league}-data-final-v3.json') as f:
            matches = json.load(f)

        allmatch = []
        
        for match in matches:
            new_match = match
            teamA = match['teamA']
            teamB = match['teamB']
            if teamA not in seen[training_year]:
                seen[training_year].add(teamA)
                
            if teamB not in seen[training_year]:
                seen[training_year].add(teamB)
                
            allmatch.append(new_match)

for yr in seen:
    print('==============')
    for team in seen[yr]:
        print(team)