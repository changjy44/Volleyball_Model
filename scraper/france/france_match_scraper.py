import json
import os

from bs4 import BeautifulSoup
from selenium import webdriver

link_map = {
    '2021': "lnv-74-97-competition_matches.csv",
    '2022': "lnv-81-111-competition_matches.csv",
    '2023': "lnv-89-124-competition_matches.csv",
    '2024': "lnv-105-142-competition_matches.csv",
}

YEARS = ['2021', '2022', '2023', '2024']

AB_mapping = ['a', 'b']

driver = webdriver.Chrome()

def scrape_sets(match_id):
    setsA = []
    setsB = []

    url = f'https://lnv-web.dataproject.com/MatchStatistics.aspx?mID={match_id}'

    driver.get(url)

    driver.implicitly_wait(30)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    sets = soup.find('span', id="Content_Main_LB_SetsPartials").text.strip()
    sets_split = sets.split()
    for set in sets_split:
        a, b = set.split("/")
        setsA.append(a.strip())
        setsB.append(b.strip())

    return setsA, setsB

for YEAR in YEARS:
    new_final_json = []
    CSV_MATCHES = 'france/' + link_map[YEAR]
    
    with open(CSV_MATCHES) as f:
        matches = f.readlines()[1:] # Skip header row

    matches = sorted(matches, key=lambda x: int(x.split(",")[0]))
    
    file_list = os.listdir(str(f'france/{YEAR}')) # Assume sorted
    file_pointer = 1
    
    for match in matches:
        match_id, date, stadium, teamA, teamA_score, teamB, teamB_score = list(map(lambda x:x.strip(), match.split(",")))
        
        # These match ids have missing starter data, and is hence manually cleaned
        unclean_ids = ['4842', '4901', '4918', '5321','5331', '5352', '5363', 
                       '5387', '5405', '5418', '5433', '5470', '5490', '5874',
                       '5876', '5877', '5884', '6379']
        if str(match_id) in unclean_ids:
            file_pointer += 2
            continue
        
        setsA = []
        setsB = []

        url = f'https://lnv-web.dataproject.com/MatchStatistics.aspx?mID={match_id}'

        driver.get(url)

        driver.implicitly_wait(30)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        sets = soup.find('span', id="Content_Main_LB_SetsPartials").text.strip()
        sets_split = sets.split()
        for set in sets_split:
            a, b = set.split("/")
            setsA.append(a.strip())
            setsB.append(b.strip())
        
        # Team A is home team
        curr_match = {}
        curr_match["match_id"] = match_id
        curr_match["teamA"] = teamA
        curr_match["teamB"] = teamB
        curr_match["teamA_score"] = teamA_score
        curr_match["teamB_score"] = teamB_score
        curr_match["match_date"] = date
        curr_match["teamA_sets"] = setsA
        curr_match["teamB_sets"] = setsB
        
        tables = soup.find_all('table', class_='rgMasterTable')[:2]

        for i in range(2):
            letter = AB_mapping[i]
            csv_file_name = str(f'france/{YEAR}') + "/" + file_list[file_pointer]
            if file_pointer % 2 == 1:
                file_pointer -= 1
            else:
                file_pointer += 3

            with open(csv_file_name) as f:
                table = f.readlines()[1:-1] # Skip header and tail
            
            players = [row.split(",")[5:] for row in table]
            clean_players = []

            for player in players:
                name = player[1]
                if name.endswith("(l)"):
                    player[1] = name.split("(l)")[0].strip()

                player = [text.strip() for text in player]

                assert len(player) == 18

                clean_players.append(player)

            table = tables[i]
            rows = table.find_all('tr')
            starter = []
            
            for row in rows[2:-1]: # Skip header and tail
                player_data = []
                items = row.find_all('td')[:7]
                for item in items[:2]:
                    col_text = item.text.strip()
                    player_data.append(col_text)

                for item in items[2:]:
                    col_text = item.text.strip()
                    if col_text.isnumeric():
                        player_data.append(col_text)
                    else:
                        player_data.append('0')
                    
                starter.append(player_data)
            
            curr_match[f'team{letter}-players'] = clean_players
            curr_match[f'team{letter}-starting'] = starter
            
        new_final_json.append(curr_match)
        
    with open(f'france/{YEAR}-france-data.json', 'w') as f:
        json.dump(new_final_json, f)

driver.quit()
    
    
