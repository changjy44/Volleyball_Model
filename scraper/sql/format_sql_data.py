import json
import csv
import os
import sys

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory by going one level up
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)


from processor.columns_final import vnl_cols
from processor.columns_final import poland_cols
from processor.columns_final import italy_cols
from processor.columns_final import france_cols
from processor.columns_final import japan_cols

from processor.columns_final import match_cols
from processor.columns_final import statistics_cols

statistics = []
all_matches = []

PLAYER_MAPPING = {}
PLAYER_REFERENCE = {}

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

debug_log = 'sql/debug.log'
debug_file = open(debug_log, 'w', encoding='utf-8')

debug_log_2 = 'sql/debug_2.log'
debug_file_2 = open(debug_log_2, 'w', encoding='utf-8')

ALL_COLS = [
    'player_number',
    'player_name',
    'role',
    'starter_role',
    'attack_points',
    'attack_errors',
    'attack_attempts',
    'attack_blocked',
    'attack_total',
    'attack_kill_efficiency',
    'attack_efficiency',
    'block_points',
    'block_errors',
    'block_touches',
    'block_total',
    'block_efficiency',
    'serve_points',
    'serve_errors',
    'serve_attempts',
    'serve_total',
    'serve_efficiency',
    'reception_perfect',
    'reception_positive',
    'reception_errors',
    'reception_attempts',
    'reception_total',
    'reception_positive_%',
    'reception_perfect_%',
    'reception_efficiency',
    'dig_sucess',
    'dig_error',
    'dig_total',
    'dig_efficiency',
    'set_success',
    'set_errors',
    'set_attempts',
    'set_total',
    'set_efficiency',
    'back_attack_points',
    'back_attack_errors',
    'back_attack_total',
    'back_attack_kill_efficiency'
]

YEARS = [2021, 2022, 2023, 2024]
LEAGUE_MAPPING = {
    'vnl': "Nation's League",
    'poland': "Plusliga",
    'italy': "Superlega",
    'france': "Ligue Nationale de Volley",
    'japan': "SV-League"
}

ROLE_MAPPING = {
    "Outside Hitter": "OH",
    "Middle-blocker": "MB",
    "Opposite": "O",
    "Setter": "S",
    "Libero": "L"
}

LEAGUE_COLUMNS = {
    'vnl': vnl_cols,
    'poland': poland_cols,
    'italy': italy_cols,
    'france': france_cols,
    'japan': japan_cols
}

EFFICIENCY_COLUMNS = [
    'attack_kill_efficiency',
    'attack_efficiency',
    'block_efficiency',
    'serve_efficiency',
    'reception_positive_%',
    'reception_perfect_%',
    'reception_efficiency',
    'dig_efficiency',
    'set_efficiency',
    'back_attack_kill_efficiency'
]

def sort_letters_alphabetically(name):
    return ''.join(sorted(name))

def calc_reception_perfect(player, recep_perf, null_marker):
    if recep_perf != null_marker:
        rate = float(recep_perf[:-1]) / 100
        return str(round(rate * int(player['reception_total'])))
    else:
        return 0

def calc_reception_positive(player, recep_pos, null_marker):
    if recep_pos != null_marker:
        rate = float(recep_pos[:-1]) / 100
        return str(round(rate * int(player['reception_total'])))
    else:
        return 0

def calc_attack_kill_efficiency(player):
    if player['attack_points'] is None or int(player['attack_total']) == 0:
        return None
    else:
        return round(100 * int(player['attack_points']) / int(player['attack_total']), 4)

def calc_attack_efficiency(player):
    if player['attack_points'] is None or player['attack_errors'] is None or int(player['attack_total']) == 0:
        return None
    else:
        return round(100 * (int(player['attack_points']) - int(player['attack_errors'])) / int(player['attack_total']), 4)

def calc_block_efficiency(player):
    if player['block_points'] is None or player['block_errors'] is None or int(player['block_total']) == 0:
        return None
    else:
        return round(100 * (int(player['block_points']) - int(player['block_errors'])) / int(player['block_total']), 4)

def calc_serve_efficiency(player):
    if player['serve_points'] is None or player['serve_errors'] is None or int(player['serve_total']) == 0:
        return None
    else:
        return round(100 * (int(player['serve_points']) - int(player['serve_errors'])) / int(player['serve_total']), 4)

def calc_reception_positive_efficiency(player):
    if player['reception_positive'] is None or int(player['reception_total']) == 0:
        return None
    else:
        return round(100 * int(player['reception_positive']) / int(player['reception_total']), 4)

def calc_reception_perfect_efficiency(player):
    if player['reception_perfect'] is None or int(player['reception_total']) == 0:
        return None
    else:
        return round(100 * int(player['reception_perfect']) / int(player['reception_total']), 4)

def calc_reception_efficiency(player):
    if player['reception_perfect'] is None or player['reception_errors'] is None or int(player['reception_total']) == 0:
        return None
    else:
        return round(100 * (int(player['reception_perfect']) - int(player['reception_errors'])) / int(player['reception_total']), 4)

def calc_dig_efficiency(player):
    if player['dig_sucess'] is None or player['dig_error'] is None or int(player['dig_total']) == 0:
        return None
    else:
        return round(100 * (int(player['dig_sucess']) - int(player['dig_error'])) / int(player['dig_total']), 4)

def calc_set_efficiency(player):
    if player['set_success'] is None or player['set_errors'] is None or int(player['set_total']) == 0:
        return None
    else:
        return round(100 * (int(player['set_success']) - int(player['set_errors'])) / int(player['set_total']), 4)

def calc_back_attack_kill_efficiency(player):
    if player['back_attack_points'] is None or int(player['back_attack_total']) == 0:
        return None
    else:
        return round(100 * int(player['back_attack_points']) / int(player['back_attack_total']), 4)
    
# Returns a match object
def handle_match(match, league, year):
    league_name = LEAGUE_MAPPING[league]
    match_id = match["match_id"]
    match_date = match["match_date"]
    teamA = match["teamA"]
    teamB = match["teamB"]
    teamA_score = match["teamA_score"]
    teamB_score = match["teamB_score"]

    A_sets = match["teamA_sets"]
    B_sets = match["teamB_sets"]

    set1_A = A_sets[0] 
    set2_A = A_sets[1] if len(A_sets) >= 2 else None 
    set3_A = A_sets[2] if len(A_sets) >= 3 else None 
    set4_A = A_sets[3] if len(A_sets) >= 4 else None 
    set5_A = A_sets[4] if len(A_sets) >= 5 else None
    set1_B = B_sets[0]
    set2_B = B_sets[1] if len(A_sets) >= 2 else None 
    set3_B = B_sets[2] if len(A_sets) >= 3 else None 
    set4_B = B_sets[3] if len(B_sets) >= 4 else None 
    set5_B = B_sets[4] if len(B_sets) >= 5 else None
    
    return [league_name, match_id, year, match_date, teamA, teamB, teamA_score, teamB_score,
            set1_A, set2_A, set3_A, set4_A, set5_A, 
            set1_B, set2_B, set3_B, set4_B, set5_B]

def create_default_player():
    player = {}
    for col in ALL_COLS:
        player[col] = None
    return player

def format_player(player):
    player_arr = []
    for col in ALL_COLS:
        player_arr.append(player[col])
    return player_arr

def handle_poland(player):
    curr_player = create_default_player()

    cols = LEAGUE_COLUMNS['poland']
    
    for i in range(len(cols)):
        col = cols[i]
        if col not in curr_player:
            continue

        field = player[i]
        value = None
        # Potentially check 0 as well

        # Store reception_positive/perfect_%
        if col == 'reception_positive_%':
            recep_pos = field
            
        if col == 'reception_perfect_%':
            recep_perf = field

        # % columns left to the end
        if col in EFFICIENCY_COLUMNS:
            continue
        else:
            value = field
        
        curr_player[col] = value

    # Calculate missing columns
    curr_player['attack_errors'] = str(int(curr_player['attack_errors']) + int(curr_player['attack_blocked']))
    curr_player['attack_attempts'] = str(int(curr_player['attack_total']) - int(curr_player['attack_points']) - int(curr_player['attack_errors']))
    curr_player['serve_attempts'] = str(int(curr_player['serve_total']) - int(curr_player['serve_points']) - int(curr_player['serve_errors']))
    curr_player['reception_perfect'] = calc_reception_perfect(curr_player, recep_perf, '-')
    curr_player['reception_positive'] = calc_reception_perfect(curr_player, recep_pos, '-')
    curr_player['reception_attempts'] = str(int(curr_player['reception_total']) - int(curr_player['reception_perfect']) - int(curr_player['reception_perfect']) - int(curr_player['reception_errors']))

    curr_player['block_total'] = calc_block_total(curr_player)
    curr_player['dig_total'] = calc_dig_total(curr_player)
    curr_player['set_total'] = calc_set_total(curr_player)
    
    # Calculate efficiencies
    curr_player['attack_kill_efficiency'] = calc_attack_kill_efficiency(curr_player)
    curr_player['attack_efficiency'] = calc_attack_efficiency(curr_player)
    curr_player['block_efficiency'] = calc_block_efficiency(curr_player)
    curr_player['serve_efficiency'] = calc_serve_efficiency(curr_player)
    curr_player['reception_positive_%'] = calc_reception_positive_efficiency(curr_player)
    curr_player['reception_perfect_%'] = calc_reception_perfect_efficiency(curr_player)
    curr_player['reception_efficiency'] = calc_reception_efficiency(curr_player)
    curr_player['dig_efficiency'] = calc_dig_efficiency(curr_player)
    curr_player['set_efficiency'] = calc_set_efficiency(curr_player)
    curr_player['back_attack_kill_efficiency'] = calc_back_attack_kill_efficiency(curr_player)

    return format_player(curr_player)

def handle_italy(player):
    curr_player = create_default_player()

    cols = LEAGUE_COLUMNS['italy']
    
    for i in range(len(cols)):
        col = cols[i]
        if col not in curr_player:
            continue

        # Potentially check 0 as well
        field = player[i] if player[i] != '.' else 0
        value = None

        # Store reception_positive/perfect_%
        if col == 'reception_positive_%':
            recep_pos = player[i]
            
        if col == 'reception_perfect_%':
            recep_perf = player[i]

        # % columns left to the end
        if col in EFFICIENCY_COLUMNS:
            continue
        else:
            value = field
        
        curr_player[col] = value

    # Calculate missing columns
    curr_player['attack_errors'] = str(int(curr_player['attack_errors']) + int(curr_player['attack_blocked']))
    curr_player['attack_attempts'] = str(int(curr_player['attack_total']) - int(curr_player['attack_points']) - int(curr_player['attack_errors']))
    curr_player['serve_attempts'] = str(int(curr_player['serve_total']) - int(curr_player['serve_points']) - int(curr_player['serve_errors']))
    curr_player['reception_perfect'] = calc_reception_perfect(curr_player, recep_perf, '.')
    curr_player['reception_positive'] = calc_reception_perfect(curr_player, recep_pos, '.')
    curr_player['reception_attempts'] = str(int(curr_player['reception_total']) - int(curr_player['reception_perfect']) - int(curr_player['reception_positive']) - int(curr_player['reception_errors']))

    curr_player['block_total'] = calc_block_total(curr_player)
    curr_player['dig_total'] = calc_dig_total(curr_player)
    curr_player['set_total'] = calc_set_total(curr_player)
    
    # Calculate efficiencies
    curr_player['attack_kill_efficiency'] = calc_attack_kill_efficiency(curr_player)
    curr_player['attack_efficiency'] = calc_attack_efficiency(curr_player)
    curr_player['block_efficiency'] = calc_block_efficiency(curr_player)
    curr_player['serve_efficiency'] = calc_serve_efficiency(curr_player)
    curr_player['reception_positive_%'] = calc_reception_positive_efficiency(curr_player)
    curr_player['reception_perfect_%'] = calc_reception_perfect_efficiency(curr_player)
    curr_player['reception_efficiency'] = calc_reception_efficiency(curr_player)
    curr_player['dig_efficiency'] = calc_dig_efficiency(curr_player)
    curr_player['set_efficiency'] = calc_set_efficiency(curr_player)
    curr_player['back_attack_kill_efficiency'] = calc_back_attack_kill_efficiency(curr_player)

    return format_player(curr_player)

def handle_france(player):
    curr_player = create_default_player()

    cols = LEAGUE_COLUMNS['france']
    
    for i in range(len(cols)):
        col = cols[i]
        if col not in curr_player:
            continue

        # Potentially check 0 as well
        field = player[i] if player[i] != '-' else 0
        value = None

        # Store reception_positive/perfect_%
        if col == 'reception_positive_%':
            recep_pos = player[i]
            
        if col == 'reception_perfect_%':
            recep_perf = player[i]

        # % columns left to the end
        if col in EFFICIENCY_COLUMNS:
            continue
        else:
            value = field
        
        curr_player[col] = value

    # Calculate missing columns
    curr_player['attack_errors'] = str(int(curr_player['attack_errors']) + int(curr_player['attack_blocked']))
    curr_player['attack_attempts'] = str(int(curr_player['attack_total']) - int(curr_player['attack_points']) - int(curr_player['attack_errors']))
    curr_player['serve_attempts'] = str(int(curr_player['serve_total']) - int(curr_player['serve_points']) - int(curr_player['serve_errors']))
    curr_player['reception_perfect'] = calc_reception_perfect(curr_player, recep_perf, '.')
    curr_player['reception_positive'] = calc_reception_perfect(curr_player, recep_pos, '.')
    curr_player['reception_attempts'] = str(int(curr_player['reception_total']) - int(curr_player['reception_perfect']) - int(curr_player['reception_positive']) - int(curr_player['reception_errors']))

    curr_player['block_total'] = calc_block_total(curr_player)
    curr_player['dig_total'] = calc_dig_total(curr_player)
    curr_player['set_total'] = calc_set_total(curr_player)

    # Calculate efficiencies
    curr_player['attack_kill_efficiency'] = calc_attack_kill_efficiency(curr_player)
    curr_player['attack_efficiency'] = calc_attack_efficiency(curr_player)
    curr_player['block_efficiency'] = calc_block_efficiency(curr_player)
    curr_player['serve_efficiency'] = calc_serve_efficiency(curr_player)
    curr_player['reception_positive_%'] = calc_reception_positive_efficiency(curr_player)
    curr_player['reception_perfect_%'] = calc_reception_perfect_efficiency(curr_player)
    curr_player['reception_efficiency'] = calc_reception_efficiency(curr_player)
    curr_player['dig_efficiency'] = calc_dig_efficiency(curr_player)
    curr_player['set_efficiency'] = calc_set_efficiency(curr_player)
    curr_player['back_attack_kill_efficiency'] = calc_back_attack_kill_efficiency(curr_player)

    return format_player(curr_player)

def handle_japan(player):
    curr_player = create_default_player()

    cols = LEAGUE_COLUMNS['japan']
    
    for i in range(len(cols)):
        col = cols[i]
        if col not in curr_player:
            continue

        # Potentially check 0 as well
        field = player[i]
        value = None

        # % columns left to the end
        if col in EFFICIENCY_COLUMNS:
            continue
        else:
            value = field
        
        curr_player[col] = value

    # Calculate missing columns
    curr_player['attack_attempts'] = str(int(curr_player['attack_total']) - int(curr_player['attack_points']) - int(curr_player['attack_errors']))
    curr_player['serve_attempts'] = str(int(curr_player['serve_total']) - int(curr_player['serve_points']) - int(curr_player['serve_errors']))
    
    curr_player['block_total'] = calc_block_total(curr_player)
    curr_player['dig_total'] = calc_dig_total(curr_player)
    curr_player['set_total'] = calc_set_total(curr_player)


    # Calculate efficiencies
    curr_player['attack_kill_efficiency'] = calc_attack_kill_efficiency(curr_player)
    curr_player['attack_efficiency'] = calc_attack_efficiency(curr_player)
    curr_player['block_efficiency'] = calc_block_efficiency(curr_player)
    curr_player['serve_efficiency'] = calc_serve_efficiency(curr_player)
    curr_player['reception_positive_%'] = calc_reception_positive_efficiency(curr_player)
    curr_player['reception_perfect_%'] = calc_reception_perfect_efficiency(curr_player)
    curr_player['reception_efficiency'] = calc_reception_efficiency(curr_player)
    curr_player['dig_efficiency'] = calc_dig_efficiency(curr_player)
    curr_player['set_efficiency'] = calc_set_efficiency(curr_player)
    curr_player['back_attack_kill_efficiency'] = calc_back_attack_kill_efficiency(curr_player)

    return format_player(curr_player)

def handle_vnl(player):
    curr_player = create_default_player()
    cols = LEAGUE_COLUMNS['vnl']
    
    for i in range(len(cols)):
        col = cols[i]
        if col not in curr_player:
            continue

        field = player[i]
        value = None
        # Potentially check 0 as well

        # % columns left to the end
        if col in EFFICIENCY_COLUMNS:
            continue
        else:
            value = field
        
        curr_player[col] = value

    # Calculate missing columns
    curr_player['block_total'] = calc_block_total(curr_player)
    curr_player['dig_total'] = calc_dig_total(curr_player)
    curr_player['set_total'] = calc_set_total(curr_player)
    
    # Calculate efficiencies
    curr_player['attack_kill_efficiency'] = calc_attack_kill_efficiency(curr_player)
    curr_player['attack_efficiency'] = calc_attack_efficiency(curr_player)
    curr_player['block_efficiency'] = calc_block_efficiency(curr_player)
    curr_player['serve_efficiency'] = calc_serve_efficiency(curr_player)
    curr_player['reception_positive_%'] = calc_reception_positive_efficiency(curr_player)
    curr_player['reception_perfect_%'] = calc_reception_perfect_efficiency(curr_player)
    curr_player['reception_efficiency'] = calc_reception_efficiency(curr_player)
    curr_player['dig_efficiency'] = calc_dig_efficiency(curr_player)
    curr_player['set_efficiency'] = calc_set_efficiency(curr_player)
    curr_player['back_attack_kill_efficiency'] = calc_back_attack_kill_efficiency(curr_player)

    pp =  format_player(curr_player)
    return pp

def get_int(field):
    if field is None:
        return 0
    else:
        return int(field)

def calc_block_total(player):
    return str(get_int(player['block_points']) + get_int(player['block_errors']) + get_int(player['block_touches']))

def calc_dig_total(player):
    return str(get_int(player['dig_sucess']) + get_int(player['dig_error']))

def calc_set_total(player):
    return str(get_int(player['set_success']) + get_int(player['set_errors']) + get_int(player['set_attempts']))

# Return a player
def handle_player(match_id, player, league):
    match_name = player[1]
        
    match_name_clean = " ".join(match_name.split())
    
    player_id = PLAYER_MAPPING[match_name_clean]
    player_name = PLAYER_REFERENCE[player_id][1]
    long_role =  PLAYER_REFERENCE[player_id][3]
    role = ROLE_MAPPING[long_role]
    arr = []

    if league == 'vnl':
        vnl_role = player[2]
        role = vnl_role # VNL role is more accurate

        arr = handle_vnl(player)

    elif league == 'poland':
        arr = handle_poland(player)

    elif league == 'italy':
        arr = handle_italy(player)

    elif league == 'france':
        arr = handle_france(player)

    elif league == 'japan':
        arr = handle_japan(player)

    jersey_number = arr[0]
    
    refined_player = [player_id, jersey_number, player_name, role, arr[3]] + arr[4:]

    if refined_player[3] != refined_player[4] and refined_player[4] != 'U':
        debug_line = f"<MATCH_ID> {match_id} <LEAGUE> {league} <NAME> {player_name} <DISPLAY_NAME> {match_name} <PLAYER_NUM> {player[0]} <VBOX_ROLE> {refined_player[3]} <STARTER_ROLE> {refined_player[4]}"
        debug_file.write(debug_line + '\n')
    
    return refined_player

# Returns a list of statistics
def handle_statistics(match, league, season):

    league_name = LEAGUE_MAPPING[league]
    match_id = match["match_id"]
    match_date = match["match_date"]
    

    teamA_name = match['teamA']
    teamB_name = match["teamB"]

    teamA_players = match['teamA-players']
    teamB_players = match['teamB-players']

    teamA_stats = []
    teamB_stats = []

    for player in teamA_players:
        partial_player = handle_player(match_id, player, league)
        temp = [league_name, match_id, season, match_date, teamA_name] + partial_player
        teamA_stats.append(temp)

    for player in teamB_players:
        partial_player = handle_player(match_id, player, league)
        temp = [league_name, match_id, season, match_date, teamB_name] + partial_player
        teamB_stats.append(temp)

    return teamA_stats, teamB_stats

for year in YEARS:
    print(f'DOING YEAR {year}')

    for league in LEAGUE_MAPPING:
        with open(f'{league}/{year}-{league}-data-processed.json', 'r', encoding='utf-8') as f:
            matches = json.load(f)

        all_matches_json = []
        
        for match in matches:
            new_match = match
            
            curr_match = handle_match(match, league, year)
            all_matches.append(curr_match)

            teamA_stats, teamB_stats = handle_statistics(match, league, year)
            curr_statistics = teamA_stats + teamB_stats
            statistics.append(curr_statistics)
            
            teamA_saved = [player[6:] for player in teamA_stats]
            teamB_saved = [player[6:] for player in teamB_stats]
            new_match['teamA-players'] = teamA_saved
            new_match['teamB-players'] = teamB_saved
            all_matches_json.append(new_match)
            
        with open(f'sql/{league}/{year}-{league}-data-final.json', 'w', encoding='utf-8') as f:
            json.dump(all_matches_json, f)
            
with open('sql/matches.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(match_cols)
    writer.writerows(all_matches)

with open('sql/statistics.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(statistics_cols)
    for stat in statistics:
        writer.writerows(stat)

debug_file.close()
debug_file_2.close()