import json
import numpy as np
import math
import os

from bs4 import BeautifulSoup
from selenium import webdriver


YEARS = ['2021', '2022', '2023', '2024']


AB_mapping = ['a', 'b']
columns = ["atk_success",
           "atk_fail",	
           "atk_all",	
           "atk_rate",	
           "backatk_success",	
           "backatk_fail",	
           "backatk_all",	
           "backatk_rate",	
           "block_success",	
           "serve_all",	
           "serve_fail",	
           "serve_effect1",	
           "serve_point",	
           "serve_effect_rate",	
           "receive_all",	
           "receive_exellent",	
           "receive_good",	
           "receive_fail",
           "receive_rate"]

def scrape_sets(driver, match_id, total_sets, A_players, B_players):
    if match_id == '28444':
        return [], []
    
    url = f"https://www.svleague.jp/en/form/b/{match_id}"
    driver.get(url)

    # Wait for the page to load (adjust time as needed)
    driver.implicitly_wait(30)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    starter_div = soup.find('div', class_='member_area')
    big_table = starter_div.find('table')
    rows = big_table.find_all('tr')
    
    starter_row = rows[1]
    all_td = starter_row.find_all('td')
    
    teamA_td = [td for td in all_td[:5] if td.text.strip() != ""]
    teamB_td = [td for td in all_td[-5:] if td.text.strip() != ""]
    
    assert len(teamA_td) == total_sets
    assert len(teamB_td) == total_sets
    
    A_B_td = [teamA_td, teamB_td]
    
    A_players_sliced = [player[:2] for player in A_players].copy()
    B_players_sliced = [player[:2] for player in B_players].copy()
    
    A_B_players = [A_players_sliced, B_players_sliced]
    
    for i in range(2):
        table = A_B_td[i]
        team_players = A_B_players[i]
            
        for td in table:
            all_li = td.find_all('li')
            
            assert len(all_li) == 6
            
            li_text = [li.text.strip() for li in all_li]
            li_text_map = list(map(lambda x: x.split('(')[0].strip() if x.endswith(')') else x, li_text))
            li_text_map[3], li_text_map[5] = li_text_map[5], li_text_map[3]
            curr_map = {}
            for i in range(len(li_text_map)):
                curr_map[li_text_map[i]] = str(i + 1)
                
            for player in team_players:
                if player[0] in curr_map:
                    player.append(curr_map[player[0]])
                else:
                    player.append('0')

    return A_B_players

driver = webdriver.Chrome()

for YEAR in YEARS:
    file_list = os.listdir(str(f'japan/{YEAR}'))
    new_final_json = []
    
    for file in file_list:
        print(file)
        match_path = 'japan/' + str(YEAR) + "/" + file
        with open(match_path,  'r') as f:
            match = json.load(f)["message"]
        
        match_id = file[6:-5] # match_xxx.json
        skip_list = ['28444']
        
        # Form not included
        if str(match_id) in skip_list:
            continue
        
        match_info = match["match_info"]
        match_tables = match["table"]

        teamA = match_info["team1_name"]
        teamB = match_info["team2_name"]
        teamA_score = match_info["set_team1"]
        teamB_score = match_info["set_team2"]
        
        match_date = match["history"][0]["match_date"]
        true_match_id = match["member"]["team1"]["match_id"]


        setsA = []
        setsB = []

        total_score = int(teamA_score) + int(teamB_score)

        for i in range(total_score):
            setsA.append(match_info[f"point_team1_set{i + 1}"])
            setsB.append(match_info[f"point_team2_set{i + 1}"])
            
            teamA_sets = setsA
            teamB_sets = setsB
            
        curr_match = {}
        curr_match["match_id"] = true_match_id
        curr_match["teamA"] = teamA
        curr_match["teamB"] = teamB
        curr_match["teamA_score"] = teamA_score
        curr_match["teamB_score"] = teamB_score
        curr_match["match_date"] = match_date
        curr_match["teamA_sets"] = teamA_sets
        curr_match["teamB_sets"] = teamB_sets
        
        for i in range(2):
            team_index = i + 1
            letter = AB_mapping[i]
            table = match_tables[f"team{team_index}"]

            all_players = []
            for player in table:
                current_player = []
                number = player["number"]

                first_name = player["en_name_first"] if player["en_name_first"] is not None else player["sei"]  
                last_name = player["en_name_last"]  if player["en_name_last"] is not None else player["mei"]

                name = ' '.join(filter(None, (first_name, last_name)))

                current_player.append(number)
                current_player.append(name)

                for col in columns:
                    current_player.append(player[col])

                assert len(current_player) == 21

                all_players.append(current_player)
            curr_match[f"team{letter}-players"] = all_players


        total_sets = int(curr_match["teamA_score"]) + int(curr_match["teamB_score"])
        sets_played_A, sets_played_B = scrape_sets(driver, true_match_id, total_sets, curr_match["teama-players"], curr_match["teamb-players"])
        curr_match["teama-starting"] = sets_played_A.copy()
        curr_match["teamb-starting"] = sets_played_B.copy()
        
        new_final_json.append(curr_match)
    
    with open(f'japan/{YEAR}-japan-data.json', 'w') as f:
        json.dump(new_final_json, f)

driver.quit()