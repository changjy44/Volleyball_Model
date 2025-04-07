import json
import random

class Player:
  def __init__(self, player_data, verbose):
    self.verbose = verbose

    self.name = player_data[0]
    self.team = player_data[1]
    self.role = player_data[2]

    # 4, 5, 6 for att
    # 16, 17, 18 for svc
    
    kill = player_data[4]
    spike_err =  player_data[5]
    spike_att = player_data[6]
    spike_total = kill + spike_err + spike_att
    
    if spike_total == 0:
        spike_total = 1

    self.att_err_perc = spike_err / spike_total
    self.att_kill_perc =  kill / spike_total
    self.att_perc =  spike_att / spike_total
    
    ace = player_data[16]
    serve_err = player_data[17]
    serve_att = player_data[18]
    serve_total = ace + serve_err + serve_att
    
    if serve_total == 0:
        serve_total = 1
    
    self.svc_err_perc = serve_err / serve_total
    self.svc_ace_perc = ace / serve_total
    self.svc_perc = serve_att / serve_total

  def validate_player(self):
    pass

  def play_service(self):
    rnd = random.random()
    if rnd < self.svc_err_perc: # Error

      print(f"Player {self.name} ({self.team}, {self.role}) service error") if self.verbose else ""
      return 2
    elif rnd < self.svc_err_perc + self.svc_ace_perc: # Ace

      print(f"Player {self.name} ({self.team}, {self.role}) service ace") if self.verbose else ""
      return 1
    else:

      print(f"Player {self.name} ({self.team}, {self.role}) service attempt") if self.verbose else ""
      return 0

  def play_spike(self):
    rnd = random.random()
    if rnd < self.att_err_perc: # Error

      print(f"Player {self.name} ({self.team}, {self.role}) spike error") if self.verbose else ""

      return 2 
    elif rnd < self.att_err_perc + self.att_kill_perc: # Kill

      print(f"Player {self.name} ({self.team}, {self.role}) spike kill") if self.verbose else ""
      return 1
    else:

      print(f"Player {self.name} ({self.team}, {self.role}) spike attempt") if self.verbose else ""
      return 0

class Team:
  def __init__(self, team_name, team_data, verbose, team_number):
    self.verbose = verbose

    self.team_name = team_name
    self.team_number = team_number
    
    self.OH_perc = team_data["OH_hits"]
    self.MB_perc = team_data["MB_hits"]
    self.O_perc = team_data["O_hits"]

    self.oh1_player = Player(team_data["OH"][0], verbose)
    self.oh2_player = Player(team_data["OH"][1], verbose)
    self.mb1_player = Player(team_data["MB"][0], verbose)
    self.mb2_player = Player(team_data["MB"][1], verbose)
    self.o_player = Player(team_data["O"][0], verbose)    
    self.s_player = Player(team_data["S"][0], verbose)    
    self.l_player = Player(team_data["L"][0], verbose)



  def play_service(self):
    return self.players[3].play_service()

  def play_spike(self):
    rnd = random.random()
    if rnd < self.OH_perc:

      print(f"Team {self.team_name} set to OH") if self.verbose else ""
      return self.curr_oh.play_spike()
    elif rnd < self.OH_perc + self.MB_perc:

      print(f"Team {self.team_name} set to MB") if self.verbose else ""
      return self.curr_mb.play_spike()
    else:

      print(f"Team {self.team_name} set to O") if self.verbose else ""
      return self.curr_o.play_spike()
    
  def rotate(self):
    temp = self.players[0]
    self.players[0] = self.players[5]
    self.players[5] = self.players[4]
    self.players[4] = self.players[3]
    self.players[3] = self.players[2]
    self.players[2] = self.players[1]
    self.players[1] = temp
    
    if self.players[0].role == 'L':
      print(f"Team {self.team_name} sub Libero out") if self.verbose else ""

      lib_player = self.players[0]
      mb_player = self.out_player
      self.players[0] = mb_player # sub MB in
      self.curr_mb = mb_player
      self.out_player = lib_player
    elif self.players[0].role == 'OH':
      self.curr_oh = self.players[0]

  def check_libero(self):
    if self.players[3].role == 'MB':

      print(f"Team {self.team_name} sub MB out") if self.verbose else ""
      mb_player = self.players[3]
      self.players[3] = self.out_player
      self.out_player = mb_player
      
  def circular_shift(self, lst, i):
      n = len(lst)
      i %= n
      return lst[i:] + lst[:i]

  def initialize_rotation(self, rotation, service_team):
    # print(rotation)
    
    players = [
      self.oh1_player,
      self.mb1_player,
      self.s_player,
      self.oh2_player,
      self.mb2_player,
      self.o_player
    ]
    
    rotated_players = self.circular_shift(players, rotation)

    self.curr_o = self.o_player
    for i in range(3):
      p = rotated_players[i]
      if p.role == 'OH':
        self.curr_oh = p
      elif p.role == 'MB':
        self.curr_mb = p
        back_middle = rotated_players[i + 3]
        if i == 0 and self.team_number == service_team: # MB serve first
          self.out_player = self.l_player
        else:
          rotated_players[i + 3] = self.l_player
          self.out_player = back_middle

    self.players = rotated_players
    

class Simulator:
  def __init__(self, teamA, teamB, match_data, verbose, rotation, service_team):
    self.verbose = verbose
    self.set_number = 1
    self.rotation = rotation

    self.sets = [0, 0]
    self.scores = [0, 0]
    self.turn = service_team

    teamA_data = match_data[teamA]
    teamB_data = match_data[teamB]
    teamA = Team(teamA, teamA_data, verbose, 0)
    teamB = Team(teamB, teamB_data, verbose, 1)

    teamA.initialize_rotation(rotation, self.turn)
    teamB.initialize_rotation(rotation, self.turn)
    
    self.teams = [teamA, teamB]
    self.score_log = []

  def simulate(self):
    while self.sets[0] < 3 and self.sets[1] < 3:
      self.simulate_set()

  def simulate_set(self):
    rotation = self.rotation
    if self.set_number > 1:
      # Change set number if set number > 0
      self.turn = 1 - self.turn
      
    print(f"Starting set number {self.set_number}") if self.verbose else ""
    while not self.check_win():
      # Sub MB with libero
      serve_team = self.turn

      self.teams[1 - self.turn].check_libero()

      serve_outcome = self.teams[self.turn].play_service()
      if serve_outcome == 0: # Attempt
        self.turn = 1 - self.turn 

        while True:
          spike_outcome = self.teams[self.turn].play_spike()
          if spike_outcome == 0: # Attempt
            self.turn = 1 - self.turn 

          elif spike_outcome == 1: # Kill
            self.win_rally(self.turn, serve_team)
            break

          elif spike_outcome == 2: # Error
            self.win_rally(1 - self.turn, serve_team)
            break

          else:
            raise Exception("undefined case")

      elif serve_outcome == 1: # Ace
        self.win_rally(self.turn, serve_team)

      elif serve_outcome == 2: # Error
        self.win_rally(1 - self.turn, serve_team)

      else:
        raise Exception("undefined case")
    
    self.set_number += 1
    self.score_log.append(self.scores)
    self.scores = [0, 0]
    self.teams[0].initialize_rotation(rotation, 1 - self.turn)
    self.teams[1].initialize_rotation(rotation, 1 - self.turn)

  def win_rally(self, team, serve_team):
    self.scores[team] += 1
    self.turn = team
    if team != serve_team:
      self.teams[team].rotate()

  def check_win(self):
    if (self.set_number == 5):
      if self.scores[0] == 15:
        self.sets[0] += 1
        return True
      elif self.scores[1] == 15:
        self.sets[1] += 1
        return True
      else:
        return False
      
    elif (self.set_number >= 1 and self.set_number <= 4):
      if self.scores[0] == 25:
        self.sets[0] += 1
        return True
      elif self.scores[1] == 25:
        self.sets[1] += 1
        return True
      else:
        return False
    else:
      raise Exception("exceed set_number case")
    
  def get_winner(self):
    if self.sets[0] == 3:
      return self.teams[0].team_name
    else:
      return self.teams[1].team_name

  def print_result(self):
    print(f"Result ({self.teams[0].team_name} vs {self.teams[1].team_name})")
    print(f"Sets {self.sets}")
    print(f"Score {self.score_log}")

LEAGUE = 'vnl'
YEAR = 2024

if __name__ == "__main__":
    with open(f'base/{LEAGUE}/{YEAR}/{YEAR}-train-matches.json') as f:
        train_matches = json.load(f)

    with open(f'data/{LEAGUE}/{YEAR}-{LEAGUE}-data-final-v3.json') as f:
        predict_matches = json.load(f)

    prediction_rate_array = []

    for count in range(3):
        games = []
        matches_predicted_correctly = 0
        total_matches = 0

        for match in predict_matches:
            teamA = match['teamA']
            teamB = match['teamB']
            teamA_score = match['teamA_score']
            teamB_score = match['teamB_score']
            teamA_wins_result = teamA_score > teamB_score

            if teamA not in train_matches or teamB not in train_matches:
                continue

            teamA_wins = 0
            teamB_wins = 0
            teamA_wins_predicted = True
            for i in range(3000):
                for rotation in range(6):
                    for service_team in range(2):
                        simulator = Simulator(teamA, teamB, train_matches, False, rotation, service_team)
                        simulator.simulate()
                        if simulator.get_winner() == teamA:
                            teamA_wins += 1
                        else:
                            teamB_wins += 1


            if teamA_wins > teamB_wins:
                teamA_wins_predicted = True
            else:
                teamA_wins_predicted = False
        
            total_matches += 1
            if teamA_wins_result == teamA_wins_predicted:
                matches_predicted_correctly += 1

            data = [teamA, teamB, teamA_score, teamB_score, teamA_wins, teamB_wins]
            # print(data)
            games.append(data)

        print(f"Prediction result: {matches_predicted_correctly}/{total_matches}")
        print(f"Prediction rate: {matches_predicted_correctly/total_matches}")
        prediction_rate_array.append(matches_predicted_correctly/total_matches)
    
    print(f"Final prediction rate across 3 runs {sum(prediction_rate_array)/len(prediction_rate_array)}")