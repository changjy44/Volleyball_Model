BLOCK_CONSTANT = 150

def process_team(all_teams, team, players, starters, mapping):
    if team not in all_teams:
        all_teams[team] = {
            "OH_hits": 0,
            "MB_hits": 0,
            "O_hits": 0,
            "S_hits": 0,
            "L_hits": 0,
            "num_sets": 0,
            "players_stats": {},
            "players_details": {},
            "counts": {
                "OH": {},
                "MB": {},
                "O": {},
                "S": {},
                "L": {}
            },
            'num_sets_played' : {}
        }
    
    players_stats = all_teams[team]["players_stats"]
    players_details = all_teams[team]["players_details"]
    counts = all_teams[team]["counts"]

    num_sets = len(starters[0]) - 2
    all_teams[team]['num_sets'] += num_sets
    
    for i in range(len(players)):
        player = players[i]
        jersey = player[0]
        volleybox_role = player[2]
        player_role = player[3]
        curr_details = player[0:4]
        curr_stats = player[4:]
        
        adapted_role = volleybox_role if player_role == 'U' or player_role == 'L' else player_role
        all_teams[team][f"{adapted_role}_hits"] += int(player[mapping['attack_total']])
        
        for set in range(2, len(starters[0])):
            set_role = starters[i][set]
            if set_role != '0':
                counts[set_role][jersey] = 1 if jersey not in counts[set_role] else 1 + counts[set_role][jersey]
                all_teams[team]['num_sets_played'][jersey] = 1 if jersey not in all_teams[team]['num_sets_played'] else 1 + all_teams[team]['num_sets_played'][jersey]

        if player_role == 'L':
            counts[player_role][jersey] = num_sets if jersey not in counts[player_role] else num_sets + counts[player_role][jersey]
            all_teams[team]['num_sets_played'][jersey] = num_sets if jersey not in all_teams[team]['num_sets_played'] else num_sets + all_teams[team]['num_sets_played'][jersey]

        
        if jersey not in players_stats:
            players_stats[jersey] =  [int(col2) if col2 is not None else 0 for col2 in curr_stats]
            players_details[jersey] = curr_details
        else:
            players_stats[jersey] = [col1 + int(col2) if col2 is not None else 0 for col1, col2, in zip(players_stats[jersey], curr_stats)]
    
    return all_teams

def process_team_reception_serve_agg(all_teams, team, players, starters, other_spikes, other_serves, mapping, block_dig_cols, reception_cols):
    if team not in all_teams:
        all_teams[team] = {
            "OH_hits": 0,
            "MB_hits": 0,
            "O_hits": 0,
            "S_hits": 0,
            "L_hits": 0,
            "num_sets": 0,
            "players_stats": {},
            "players_details": {},
            "counts": {
                "OH": {},
                "MB": {},
                "O": {},
                "S": {},
                "L": {}
            },
            "num_sets_played": {}
        }
    
    players_stats = all_teams[team]["players_stats"]
    players_details = all_teams[team]["players_details"]
    counts = all_teams[team]["counts"]

    num_sets = len(starters[0]) - 2
    all_teams[team]['num_sets'] += num_sets
    
    for i in range(len(players)):
        old_player = players[i]
        player = old_player.copy()
        for col in block_dig_cols:
            player[mapping[col]] = BLOCK_CONSTANT * int(player[mapping[col]]) / other_spikes 
        for col in reception_cols:
            player[mapping[col]] = BLOCK_CONSTANT * int(player[mapping[col]]) / other_serves
        
        jersey = player[0]
        volleybox_role = player[2]
        player_role = player[3]
        curr_details = player[0:4]
        curr_stats = player[4:]
        
        adapted_role = volleybox_role if player_role == 'U' or player_role == 'L' else player_role
        all_teams[team][f"{adapted_role}_hits"] += int(player[mapping['attack_total']])
        
        for set in range(2, len(starters[0])):
            set_role = starters[i][set]
            if set_role != '0':
                counts[set_role][jersey] = 1 if jersey not in counts[set_role] else 1 + counts[set_role][jersey] 

        if player_role == 'L':
            counts[player_role][jersey] = num_sets if jersey not in counts[player_role] else num_sets + counts[player_role][jersey] 
        
        if jersey not in players_stats:
            players_stats[jersey] =  [float(col2) if col2 is not None else 0 for col2 in curr_stats]
            players_details[jersey] = curr_details
        else:
            players_stats[jersey] = [col1 + float(col2) if col2 is not None else 0 for col1, col2, in zip(players_stats[jersey], curr_stats)]
    
    return all_teams

def my_numeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def aggregate_stats(players, num_sets):
    agg = [col for col in zip(*players)]
    for i in range(len(agg)):
        col = agg[i]
        total = 0
        for item in col:
            if not my_numeric(str(item)):
                total = 0
            else:
                total += float(item)
        agg[i] = total
    
    agg_sets = [item / num_sets for item in agg]
    return agg, agg_sets


def sort_starters(all_teams, all_teams_processed, mapping):
    for team in all_teams:
        players_stats = all_teams[team]["players_stats"]
        players_details = all_teams[team]["players_details"]
        counts = all_teams[team]["counts"]
        
        all_teams_processed[team] = {}
        all_teams_processed[team]["OH_hits"] = all_teams[team]["OH_hits"]
        all_teams_processed[team]["MB_hits"] = all_teams[team]["MB_hits"]
        all_teams_processed[team]["O_hits"] = all_teams[team]["O_hits"]
        all_teams_processed[team]['num_sets'] = all_teams[team]['num_sets']
        all_teams_processed[team]['num_sets_played'] = all_teams[team]['num_sets_played']
        
        for jersey in players_details:
            max_count = max([counts[role][jersey] if jersey in counts[role] else 0 for role in counts])
            max_seen = False
            for role in counts:
                if jersey in counts[role] and max_seen:
                    counts[role].pop(jersey)  
                elif jersey in counts[role] and counts[role][jersey] == max_count:
                    max_seen = True
                elif jersey in counts[role] and counts[role][jersey] != max_count:
                    counts[role].pop(jersey)
                    
            if not any(jersey in counts[role] for role in counts):
                full_details = players_details[jersey]
                counts[full_details[2]][jersey] = 1

        all_players = []
        for role in counts:
            values = counts[role].items()
            sorted_values = sorted(values, 
                                key=lambda p: (p[1], players_stats[p[0]][mapping['attack_total']] +  players_stats[p[0]][mapping['serve_total']]), 
                                reverse=True)
            player_that_role = [players_details[jersey] + players_stats[jersey] for jersey, _ in sorted_values]
            all_teams_processed[team][role] = player_that_role
            all_players += player_that_role
        
        all_players_names = [player[1] for player in all_players]
        setted = set(all_players_names)
            
        assert len(setted) == len(all_players_names)

        stats, stats_per_set = aggregate_stats(all_players, all_teams_processed[team]['num_sets'])
        
        all_teams_processed[team]['all_stats'] = stats
        all_teams_processed[team]['all_stats_per_set'] = stats_per_set
        
        num_per_role = {
            'OH': 2,
            'MB': 2,
            'S': 1,
            'O': 1
        }
        
        starting_names = []
        for role in num_per_role:
            num_role = num_per_role[role]
            people = [player[1] for player in all_teams_processed[team][role]][:num_role]
            starting_names += people
        
        assert len(starting_names) == len(set(starting_names))
    
    return all_teams_processed

def normalise_block_dig_v2(away_players, num_sets, num_spikes, mapping, block_dig_cols):
    block_dig = []
    for col in block_dig_cols:
        stat =  BLOCK_CONSTANT * sum([int(player[mapping[col]]) for player in away_players]) / (num_sets * num_spikes)
        block_dig.append(stat)
    return block_dig
    
def normalise_reception_v2(away_players, num_sets, num_service, mapping, reception_cols):
    reception = []
    for col in reception_cols:
        stat =  BLOCK_CONSTANT * sum([int(player[mapping[col]]) for player in away_players]) / (num_sets * num_service)
        reception.append(stat)
    return reception

def add_matches(all_teams_processed, matches):
    for match in matches:
        teamA = match['teamA']
        teamB = match['teamB']
        num_sets = int(match['teamA_score']) + int(match['teamB_score'])
        rebased_match_A = {
            'match_id' : match['match_id'],
            'other_team': teamB,
            'num_sets': int(match['teamA_score']) + int(match['teamB_score']),
            'home_players': match['teamA-players'],
            'away_players': match['teamB-players'],
        }
        rebased_match_B = {
            'match_id' : match['match_id'],
            'other_team': teamA,
            'num_sets': int(match['teamA_score']) + int(match['teamB_score']),
            'home_players': match['teamB-players'],
            'away_players': match['teamA-players'],
        }
        if 'matches' not in all_teams_processed[teamA]:
            all_teams_processed[teamA]['total_sets'] = 0
            all_teams_processed[teamA]['matches'] = []
        
        if 'matches' not in all_teams_processed[teamB]:
            all_teams_processed[teamB]['total_sets'] = 0
            all_teams_processed[teamB]['matches'] = []
            
        all_teams_processed[teamA]['total_sets'] += num_sets
        all_teams_processed[teamB]['total_sets'] += num_sets
        all_teams_processed[teamA]['matches'].append(rebased_match_A)
        all_teams_processed[teamB]['matches'].append(rebased_match_B)
        
    return all_teams_processed