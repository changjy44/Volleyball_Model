def circular_shift(lst, i):
    n = len(lst)
    i %= n
    return lst[i:] + lst[:i]

def generate_permutations():
    permutation = ['OH', 'MB', 'O', 'OH', 'MB', 'S']
    permuations = []
    
    for i in range(6):
        new_permutation = circular_shift(permutation, i)
        permuations.append(tuple(new_permutation))
        copy = new_permutation.copy()
        copy[0], copy[1] = copy[1], copy[0]
        copy[3], copy[4] = copy[4], copy[3]
        permuations.append(tuple(copy))
        copy2 = new_permutation.copy()
        copy2[2], copy2[5] = copy2[5], copy2[2]
        permuations.append(tuple(copy2))
    
    dic = {}
    for perm in permuations:
        dic[perm] = 0
        
    return dic


def simple_algorithm(players, player_stats, starter_numbers, mapping):
    # starter numbers and player numbers should be strings
    # returns a list of players, with the simple role determined
    player_combined = [player + player_stat for player, player_stat in zip(players, player_stats)]

    serveless = [player for player in player_combined if int(player[mapping['serve_total']]) == 0]
    receptions = sorted(serveless, key=lambda p: int(p[mapping['reception_total']]), reverse=True)
    libero = receptions[0]
    
    starter_players_2 = [player for player in player_combined if player[0] in starter_numbers]
    
    seen = set()
    starter_players = []
    for player in starter_players_2:
        if player[0] not in seen:
            seen.add(player[0])
            starter_players.append(player)
            
    assert len(starter_players) == 6

    receptions_starters = sorted(starter_players, key=lambda p: int(p[mapping['reception_total']]), reverse=True)
    OH_players = receptions_starters[:2]
    other_players_2 = receptions_starters[2:]

    spikes_starters = sorted(other_players_2, key=lambda p: int(p[mapping['attack_total']]), reverse=True)
    opposite = spikes_starters[0]
    setter = spikes_starters[-1]
    blockers = spikes_starters[1:3]
    
    all_players = [libero, OH_players[0], OH_players[1], setter, opposite, blockers[0], blockers[1]]
    all_players_num = [player[0] for player in all_players]
    assert len(all_players_num) == len(set(all_players_num))
    
    starting_7_mapping = {}
    starting_7_mapping[libero[0]] = 'L'
    starting_7_mapping[OH_players[0][0]] = 'OH'
    starting_7_mapping[OH_players[1][0]] = 'OH'
    starting_7_mapping[blockers[0][0]] = 'MB'
    starting_7_mapping[blockers[1][0]] = 'MB'
    starting_7_mapping[opposite[0]] = 'O'
    starting_7_mapping[setter[0]] = 'S'

    return_players = []

    for player, player_stat in zip(players, player_stats):
        curr_player = []
        curr_player += player
        if player[0] in starting_7_mapping:
            curr_player.append(starting_7_mapping[player[0]])
        else:
            curr_player.append('U')
        curr_player += player_stat

        return_players.append(curr_player)

    return return_players


def vnl_simple_algorithm(players, player_stats, starter_numbers, mapping):
    # starter numbers and player numbers should be strings
    # returns a list of players, with the simple role determined
    player_combined = [player + player_stat for player, player_stat in zip(players, player_stats)]

    serveless = [player for player in player_combined if int(player[mapping['serve_total']]) == 0]
    receptions = sorted(serveless, key=lambda p: int(p[mapping['reception_total']]), reverse=True)
    libero = receptions[0]
    
    starter_players_2 = [player for player in player_combined if player[0] in starter_numbers]
    
    seen = set()
    starter_players = []
    for player in starter_players_2:
        if player[0] not in seen:
            seen.add(player[0])
            starter_players.append(player)
            
    assert len(starter_players) == 6
    
    setter_starters = sorted(starter_players, key=lambda p: int(p[mapping['set_total']]), reverse=True)
    setter = setter_starters[0]
    others = setter_starters[1:]
    

    receptions_starters = sorted(others, key=lambda p: int(p[mapping['reception_total']]), reverse=True)
    OH_players = receptions_starters[:2]
    other_players_2 = receptions_starters[2:]

    spikes_starters = sorted(other_players_2, key=lambda p: int(p[mapping['attack_total']]), reverse=True)
    opposite = spikes_starters[0]
    # setter = spikes_starters[-1]
    blockers = spikes_starters[1:3]
    
    all_players = [libero, OH_players[0], OH_players[1], setter, opposite, blockers[0], blockers[1]]
    all_players_num = [player[0] for player in all_players]
    assert len(all_players_num) == len(set(all_players_num))
    
    starting_7_mapping = {}
    starting_7_mapping[libero[0]] = 'L'
    starting_7_mapping[OH_players[0][0]] = 'OH'
    starting_7_mapping[OH_players[1][0]] = 'OH'
    starting_7_mapping[blockers[0][0]] = 'MB'
    starting_7_mapping[blockers[1][0]] = 'MB'
    starting_7_mapping[opposite[0]] = 'O'
    starting_7_mapping[setter[0]] = 'S'

    return_players = []

    for player, player_stat in zip(players, player_stats):
        curr_player = []
        curr_player += player
        if player[0] in starting_7_mapping:
            curr_player.append(starting_7_mapping[player[0]])
        else:
            curr_player.append('U')
        curr_player += player_stat

        return_players.append(curr_player)

    return return_players


