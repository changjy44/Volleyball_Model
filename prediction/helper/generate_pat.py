import sys
from string import Template
import os

pat_template = Template("""
#define WIN_POINTS 25;
#define WIN_POINTS_5 15;

#define SERVE_INDEX 1;
#define ATTACK_INDEX 0;

#define OH1 0;
#define OH2 1;
#define MB1 2;
#define MB2 3;
#define SETTER 4;
#define OPPOSITE 5;

#define SCORE 0;
#define ERROR 1;
#define RALLY 2;

var DEFAULT_POSITION[6][6] = [
0, 2, 4, 1, 3, 5,
5, 0, 2, 4, 1, 3,
3, 5, 0, 2, 4, 1,
1, 3, 5, 0, 2, 4,
4, 1, 3, 5, 0, 2,
2, 4, 1, 3, 5, 0
];
var WINNING_SCORE = [$Points, 25, 25, 25, 15];

// OH1, OH2, MB1, MB2, S, O
// AK, AE, AS, SA, SE, SS
var ratesAll[2][6][2][3] = [
$Hit_rates
];

var setterRates[2][3] = [
$Set_rates
];

var positionsAll[2][6] = [
0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0
];

var currentOH = [
0, 0
];

var currentMB = [
1, 1
];

var scoreAll = [0, 0];
var setAll = [0, 0];

var service_team = 0;

// Utility Functions
IncrementScore(team) = Increase{
	scoreAll[team] = scoreAll[team] + 1
} -> Skip;

IncrementSet(team) = IncreaseSet {
	setAll[team] = setAll[team] + 1
} -> Skip;

SetPlayerPositions(team, rotation) = SetPosition{
	var i = 0;
    while (i < 6) {
		positionsAll[team][i] = DEFAULT_POSITION[rotation][i];
		i = i + 1;
	}
} -> Skip;

ResetScore = SetScore {
	scoreAll[0] = 0;
	scoreAll[1] = 0;
} -> Skip;

Rotate(team) = rotate{
	var i = 0;
	var prev = positionsAll[team][5];
	
	while (i < 6) {
		var temp = positionsAll[team][i];
		positionsAll[team][i] = prev;
		prev = temp;
    	i = i + 1;
  }
} -> Skip;

CheckWin(set, team) = ifa (scoreAll[team] == WINNING_SCORE[set]) { 
	IncrementSet(team); 
	ifa (setAll[team] == 1) {
		Skip
	}
	else {
		Game(set + 1, 0, 0); Skip
	}
} 
// Game does not score, next point
else {
	ifa (team == service_team) { 
		Serve(set, team); Skip 
	}
	else {
		Rotate(team); Serve(set, team); Skip
	}
};

// Play Functions
SpikePlayer(set, team, player) = pcase {
	ratesAll[team][player][ATTACK_INDEX][SCORE]: IncrementScore(team); CheckWin(set, team)
	ratesAll[team][player][ATTACK_INDEX][ERROR]: IncrementScore(1 - team); CheckWin(set, 1 - team)
	ratesAll[team][player][ATTACK_INDEX][RALLY]: Setter(set, 1 - team)
};

OutsideSpike(set, team) = SetOH {
	var i = 0;
    while (i < 3) {
    	var player = positionsAll[team][i];
    	if ((player == OH1) || (player == OH2)) {
    		currentOH[team] = player;
    	}
		i = i + 1;
	}
} -> SpikePlayer(set, team, currentOH[team]);

MiddleSpike(set, team) = SetMB {
	var i = 0;
    while (i < 3) {
    	var player = positionsAll[team][i];
    	if ((player == MB1) || (player == MB2)) {
    		currentMB[team] = player;
    	}
		i = i + 1;
	}
} -> SpikePlayer(set, team, currentMB[team]);

OppositeSpike(set, team) = SpikePlayer(set, team, OPPOSITE);


Setter(set, team) = pcase {
	setterRates[team][0]: OutsideSpike(set, team)
	setterRates[team][1]: MiddleSpike(set, team)
	setterRates[team][2]: OppositeSpike(set, team)
};

ServicePlayer(set, team, player) = pcase {
	ratesAll[team][player][SERVE_INDEX][SCORE]: IncrementScore(team); CheckWin(set, team)
	ratesAll[team][player][SERVE_INDEX][ERROR]: IncrementScore(1 - team); CheckWin(set, 1 - team)
	ratesAll[team][player][SERVE_INDEX][RALLY]: Setter(set, 1 - team)
};

Serve(set, team) = SetServiceTeam {service_team = team;} -> ServicePlayer(set, team, positionsAll[team][3]);


Game(set, rotation, service) = SetPlayerPositions(0, rotation); SetPlayerPositions(1, rotation); ResetScore; Serve(set, (set % 2) + service);

BeginMatch = Game(0, 0, 0);

AllRotations = pcase {
1: Game(0, 0, 0)
1: Game(0, 0, 1)
1: Game(0, 1, 0)
1: Game(0, 1, 1)
1: Game(0, 2, 0)
1: Game(0, 2, 1)
1: Game(0, 3, 0)
1: Game(0, 3, 1)
1: Game(0, 4, 0)
1: Game(0, 4, 1)
1: Game(0, 5, 0)
1: Game(0, 5, 1)
};

#define goal setAll[0] == 1;
#assert AllRotations reaches goal with prob;
""")

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from helper.columns_starters import ALL_COLS

   
cols = ALL_COLS
mapping = {}
for i in range(len(cols)):
    col = cols[i]
    mapping[col] = i

def generate_set_rates(teamA, teamB, matches_2023, league):
   output_str_arr = ""
   output_str_arr += str(matches_2023[teamA]['OH_hits'])
   output_str_arr += ","
   output_str_arr += str(matches_2023[teamA]['MB_hits'])
   output_str_arr += ","
   output_str_arr += str(matches_2023[teamA]['O_hits'])
   output_str_arr += ","
   
   output_str_arr += str(matches_2023[teamB]['OH_hits'])
   output_str_arr += ","
   output_str_arr += str(matches_2023[teamB]['MB_hits'])
   output_str_arr += ","
   output_str_arr += str(matches_2023[teamB]['O_hits'])
   return output_str_arr

def generate_spike_serve_rates(teamA, teamB, matches_2023, league):
   global output_str_arr
   global counter


   def add(new_str):
    global counter
    global output_str_arr
    counter += 1
    output_str_arr += new_str
    
    if counter != 72:
       output_str_arr += ","
    
    if counter % 6 == 0:
       output_str_arr += "\n"


   
   output_str_arr = ""
   counter = 0
   
   players_per_role = {
    'OH': 2,
    'MB': 2,
    'S' : 1,
    'O' : 1
    }
   for team in [teamA, teamB]:
      for role in players_per_role:
         for i in range(players_per_role[role]):
            # att kill
            add(str(matches_2023[team][role][i][mapping['attack_points']]))
            # att err
            add(str(matches_2023[team][role][i][mapping['attack_errors']]))
            # att succ
            add(str(matches_2023[team][role][i][mapping['attack_attempts']]))

            # svc ace
            add(str(matches_2023[team][role][i][mapping['serve_points']]))
            # svc err
            add(str(matches_2023[team][role][i][mapping['serve_errors']]))
            # svc succ
            add(str(matches_2023[team][role][i][mapping['serve_attempts']]))

   return output_str_arr

def generate_spike_serve_rates_v2(teamA, teamB):
    combined = teamA + teamB
    output_arr = []
    for player in combined:
        # att kill
        output_arr.append(str(player[mapping['attack_points']]))
        # att err
        output_arr.append(str(player[mapping['attack_errors']]))
        # att succ
        output_arr.append(str(player[mapping['attack_attempts']]))
        
        if int(player[mapping['attack_points']]) + int(player[mapping['attack_errors']]) + int(player[mapping['attack_attempts']]) == 0:
            assert False

        # svc ace
        output_arr.append(str(player[mapping['serve_points']]))
        # svc err
        output_arr.append(str(player[mapping['serve_errors']]))
        # svc succ
        output_arr.append(str(player[mapping['serve_attempts']]))
        
        if int(player[mapping['serve_points']]) + int(player[mapping['serve_errors']]) + int(player[mapping['serve_attempts']]) == 0:
            assert False
        
    output_str_arr = ""
    for i in range(len(output_arr)):
        counter = i + 1
        output_str_arr += output_arr[i]
        if counter != 72:
            output_str_arr += ","
        if counter % 6 == 0:
            output_str_arr += "\n"
            
    return output_str_arr


def generate_pat_model(id, teamA, teamB, matches_2023, points_to_win, path, league):
    keys = {}

    keys["Hit_rates"] = generate_spike_serve_rates(teamA, teamB, matches_2023, league)
    keys["Set_rates"] = generate_set_rates(teamA, teamB, matches_2023, league)
    keys["Points"] = points_to_win

    id_string = str(id)
    while len(id_string) != 3:
        id_string = '0' + id_string

    pat_filled = pat_template.substitute(keys)

    with open(path, "w") as outfile:
        outfile.write(pat_filled)


# Take in an array of players in TeamA and in TeamB
def generate_pat_model_custom(id, teamA, teamB, teamA_players, teamB_players, 
                              train_matches, points_to_win, path, league):
    keys = {}

    
    keys["Hit_rates"] = generate_spike_serve_rates_v2(teamA_players, teamB_players)
    keys["Set_rates"] = generate_set_rates(teamA, teamB, train_matches, league)
    keys["Points"] = points_to_win

    id_string = str(id)
    while len(id_string) != 3:
        id_string = '0' + id_string

    pat_filled = pat_template.substitute(keys)

    with open(path, "w") as outfile:
        outfile.write(pat_filled)
        
