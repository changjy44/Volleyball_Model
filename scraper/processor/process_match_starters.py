import json
import csv

from columns_raw import vnl_cols
from columns_raw import poland_cols
from columns_raw import italy_cols
from columns_raw import france_cols
from columns_raw import japan_cols

from utils import generate_permutations
from collections import Counter


PLAYER_MAPPING = {}
PLAYER_REFERENCE = {}
ROLE_MAPPING = {
    "Outside Hitter": "OH",
    "Middle-blocker": "MB",
    "Opposite": "O",
    "Setter": "S",
    "Libero": "L"
}

with open('sql/player_mappings.csv','r', encoding='utf-8-sig') as f:
    player_mapping_table = csv.reader(f)
    for entry in player_mapping_table:
        name = entry[0]
        pid = entry[2]
        PLAYER_MAPPING[name] = pid

with open('sql/player_volleybox.csv', 'r',encoding='utf-8-sig') as f:
    table = csv.reader(f)
    for entry in table:
        pid = entry[0]
        rest = entry[1:]
        PLAYER_REFERENCE[pid] = rest

def compute_value(permutation, player_col):
    sorted_col = sorted(player_col, key=lambda p:p[1])
    actual_roles = tuple([col[2] for col in sorted_col])
    return sum(1 for a, b in zip(permutation, actual_roles) if a == b)

def get_player(team, jersey_num):
    for player in team:
        if player[0] == jersey_num:
            return player

def intOrzero(num):
    try:
        ans = int(num)
        return ans
    except Exception:
        return 0
    
def lowercase_first_char(s):
    return s[:1].lower() + s[1:] if s else s

def handle_france_name(name):
    if name in PLAYER_MAPPING:
        return name
    elif ' '.join(name.lower().split()) in PLAYER_MAPPING:
        return ' '.join(name.lower().split())
    elif ' '.join(name.upper().split()) in PLAYER_MAPPING:
        return ' '.join(name.upper().split())
    elif ' '.join(name.split()) in PLAYER_MAPPING:
        return ' '.join(name.split())
    else:
        print(f'player {name} not in mapping')
        tokens = name.split()
        tokens[0] = tokens[0].lower()
        for j in range(len(tokens)):
            if j != len(tokens) - 1:
                tokens[j] = tokens[j].lower()
                
            tokens[j] = lowercase_first_char(tokens[j])
            
        ret =  ' '.join(tokens)
        return ret
    

def handle_team(team, starting, num_sets, match_id, name):
    seen = {
        'S': [],
        'OH': [],
        'MB': [],
        'O': []
    }
    
    final_roles = {}
    
    if LEAGUE == 'france' or LEAGUE  == 'japan':
        for i in range(len(team)):
            player = team[i]
            process_name = handle_france_name(player[1])
            team[i][1] = process_name
            starting[i][1] = process_name
            
    modified_sets = [player[:] for player in starting]
    
    printed = False
    
    for set in range(num_sets):            
        permuations_dic = generate_permutations()
        player_col = []
        for player in starting:
            curr = [player[0], player[set + 2], ROLE_MAPPING[PLAYER_REFERENCE[PLAYER_MAPPING[player[1]]][3]]] 
            if player[set + 2] != '0' or player[set + 2] == '':
                player_col.append(curr)

        assert len(player_col) == 6
        
        for permutation in permuations_dic:
            permuations_dic[permutation] = compute_value(permutation, player_col)
        
        max_value = max(permuations_dic.values())
        largest_perms = [perm for perm in permuations_dic if permuations_dic[perm] == max_value]
        best_permutation = largest_perms[0]
        
        for player in modified_sets:
            num = player[set + 2]
            if num == '' or num == '.':
                player[set + 2] = '0' 
            elif num != '0':
                intended_role = best_permutation[int(num) - 1]
                player[set + 2] = intended_role

        if max_value < 6:
            debug_file.write(f'<MATCH_ID> {match_id} <TEAM> {name} <SET> {set} <VALUE> {max_value} <PERM> {best_permutation}\n')
        if len(largest_perms) > 1:
            debug_file_2.write(f'<MATCH_ID> {match_id} <TEAM> {name} <SET> {set} <VALUE> {max_value} <PERMS> {largest_perms}\n')
        
        sorted_player_col = sorted(player_col, key=lambda p:p[1])
        for i in range(len(sorted_player_col)):
            role = best_permutation[i]
            seen[role].append(sorted_player_col[i][0])
    
    for item in seen:
        lst = seen[item]
        counts = Counter(lst)

        unsorted_player_numbers = counts.items()
        player_numbers = sorted(unsorted_player_numbers, key=lambda p:p[1], reverse=True)
        sorted_numbers = sorted(player_numbers, key=lambda pair:(pair[1], get_player(team, pair[0])[mapping['serve_total']], get_player(team, pair[0])[mapping['attack_total']]), reverse=True)
        final_roles[sorted_numbers[0][0]] = item

        if item == 'OH' or item == 'MB':
            final_roles[sorted_numbers[1][0]] = item

    liberos = sorted([player for player in team if player[0] not in final_roles and intOrzero(player[mapping["serve_total"]]) <= 1], key=lambda p:intOrzero(p[mapping['reception_total']]), reverse=True)
    libero = liberos[0][0]
    final_roles[libero] = 'L'
    
    for player in team:
        if LEAGUE != 'vnl':
            name = player[1]
            if name not in PLAYER_MAPPING:
                name = name.lower()

            
            a = PLAYER_MAPPING[name]
            b = PLAYER_REFERENCE[a][3]
            c = ROLE_MAPPING[b]
            vbox_role = ROLE_MAPPING[PLAYER_REFERENCE[PLAYER_MAPPING[name]][3]]
            player.insert(2, vbox_role)
            
        if player[0] in final_roles:
            player.insert(3, final_roles[player[0]])
        else:
            player.insert(3, 'U')
    
    return team, modified_sets

YEARS = [2021, 2022, 2023, 2024]
LEAGUES = ['vnl', 'poland', 'italy', 'france', 'japan']

columns_mapping = {
    'vnl': vnl_cols, 
    'poland': poland_cols, 
    'italy': italy_cols, 
    'france': france_cols, 
    'japan': japan_cols
}


for LEAGUE in LEAGUES:
    mapping = {}
    exact_cols = columns_mapping[LEAGUE]

    for i in range(len(exact_cols)):
        col = exact_cols[i]
        mapping[col] = i
    
    debug_log = f'processor/{LEAGUE}_debug.log'
    debug_file = open(debug_log, 'w', encoding='utf-8')

    debug_log_2 = f'processor/{LEAGUE}_debug_2.log'
    debug_file_2 = open(debug_log_2, 'w', encoding='utf-8')
    
    for year in YEARS:
        file = f'{LEAGUE}/{year}-{LEAGUE}-data.json'
        with open(file) as f:
            matches = json.load(f)

        new_final_json = []
        for match in matches:
            match_id = match["match_id"]

            curr_match = {}

            curr_match["match_id"] = match["match_id"]
            curr_match["match_date"] = match["match_date"]
            curr_match["teamA"] = match["teamA"]
            curr_match["teamB"] = match["teamB"]
            curr_match["teamA_score"] = match["teamA_score"]
            curr_match["teamB_score"] = match["teamB_score"]
            curr_match["teamA_sets"] = match["teamA_sets"]
            curr_match["teamB_sets"] = match["teamB_sets"]

            team_A = match["teama-players"]
            team_B = match["teamb-players"]
            
            num_sets = int(match["teamA_score"]) + int(match["teamB_score"])
            
            team_A_starting = match["teama-starting"]
            team_B_starting = match["teamb-starting"]
            
            new_teamA, new_teamA_start = handle_team(team_A, team_A_starting, num_sets, match_id, match["teamA"])
            new_teamB, new_teamB_start = handle_team(team_B, team_B_starting, num_sets, match_id, match["teamB"])
            
            curr_match["teamA-players"] = new_teamA
            curr_match["teamB-players"] = new_teamB
            curr_match["teamA-starting"] = new_teamA_start
            curr_match["teamB-starting"] = new_teamB_start
            
            new_final_json.append(curr_match)

        with open(f'{LEAGUE}/{year}-{LEAGUE}-data-processed.json', 'w') as f:
            json.dump(new_final_json, f)
    

    debug_file.close()
    debug_file_2.close()