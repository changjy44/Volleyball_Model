import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from helper.columns_starters import ALL_COLS

mapping = {}
for i in range(len(ALL_COLS)):
    col = ALL_COLS[i]
    mapping[col] = i

def compute_spike(player, match_id, intended_role, year, league):
    name = player[1]
    points = int(player[mapping['attack_points']])
    error = int(player[mapping['attack_errors']])
    total = int(player[mapping['attack_points']]) + int(player[mapping['attack_errors']]) + int(player[mapping['attack_attempts']])
    if total == 0:
        return [match_id, league, year, name, intended_role, 0, 0]
    else:
        return [match_id, league, year, name, intended_role, round((points / total), 6), round((error / total), 6)]

def compute_serve(player, match_id, intended_role, year, league):
    name = player[1]
    points = int(player[mapping['serve_points']])
    error = int(player[mapping['serve_errors']])
    total = int(player[mapping['serve_points']]) + int(player[mapping['serve_errors']]) + int(player[mapping['serve_attempts']])
    if total == 0:
        return [match_id, league, year, name, intended_role, 0, 0]
    else:        
        return [match_id, league, year, name, intended_role, round((points / total), 6), round((error / total), 6)]
