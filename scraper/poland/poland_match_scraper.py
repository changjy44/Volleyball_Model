from bs4 import BeautifulSoup

from selenium import webdriver
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import random

from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

YEARS = ['2021', '2022', '2023', '2024']

for YEAR in YEARS:
    match_ids = []
    src_file = f'poland/{YEAR}_match_ids.txt'
    final_dump_name = f'poland/{YEAR}-poland-data.json'

    with open(src_file, 'r') as f:
        for line in f:
            match_ids.append(line.strip())

    all_match_data = []

    for match_id in match_ids:
        final_data = {}
        
        table_index = 0
        big_ids = ['1101307', '1101317', '1102011', '1102700', '1103391']
        if str(match_id) in big_ids:
            table_index = 1
        
        # the data is unclean, we skip
        unknown_ids = ['1101546', '1102700', '1101546', '1102313', '1102919', '1103377', '1103385']
        if str(match_id) in unknown_ids:
            continue

        url = f"https://www.plusliga.pl/games/action/show/id/{match_id}"

        driver.get(url)

        driver.implicitly_wait(30)

        driver.execute_script("window.scrollBy(0, 500)")  # Scroll down by 500 pixels

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        teamA = soup.select('.notranslate.game-team.left.gs')[0]
        teamB = soup.select('.notranslate.game-team.right.gs')[0]
        test = soup.find(class_='points')
        box = soup.find(class_='game-result-box')
        result = box.find(class_='game-result')
        sets = box.find(class_='score')
        detailed_sets = sets.find_all('span')
        
        date = soup.find('div', class_='game-date').text.split(",")[0].strip()
        date_obj = datetime.strptime(date, "%d.%m.%Y")
        formatted_date = str(date_obj.date())
    
        teamA_name = teamA.text.strip()
        teamB_name = teamB.text.strip()
        teamA_score = result.text.strip().split(":")[0]
        teamB_score = result.text.strip().split(":")[1]
        teamA_sets = [detailed_sets[i].text.strip() for i in range(len(detailed_sets)) if i % 2 == 0]
        teamB_sets = [detailed_sets[i].text.strip() for i in range(len(detailed_sets)) if i % 2 == 1]
        
        number_of_sets = int(teamA_score) + int(teamB_score)


        final_data['match_id'] = match_id
        final_data["teamA"] = teamA_name
        final_data["teamB"] = teamB_name
        final_data["teamA_score"] = teamA_score
        final_data["teamB_score"] = teamB_score
        final_data["match_date"] = formatted_date
        final_data["teamA_sets"] = teamA_sets
        final_data["teamB_sets"] = teamB_sets
        
        letters = ['a', 'b']
        
        for team_letter in letters:
            iframe = driver.find_elements(By.CLASS_NAME, f'widget-team-{team_letter}')[table_index]
            driver.switch_to.frame(iframe)

            test_table = driver.find_element(By.CLASS_NAME, 'team-stats-widget')

            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')

            rows = soup.find_all('div', class_='table-row')

            players = []

            for row in rows[1:-1]: # Skip header and tail
                player_data = []

                items = row.find_all(class_='table-row-item')
                for item in items[:2]: # No and Player name
                    col_text = item.text.strip()

                    libero = item.find(class_='libero')
                    if libero:
                        col_text = col_text[:-1]

                    player_data.append(col_text)

                for item in items[3:]: # Rest of data
                    col_text = item.text
                    split_text = col_text.strip().split()
                    for col in split_text:
                        player_data.append(col.strip())
                        
                if len(player_data) < 23:
                    player_data.append('0') # Add Dig
                    player_data.append('0') # Add Assist

                assert len(player_data) == 23

                players.append(player_data)

            starters = []

            for row in rows[1:-1]: # Skip header and tail
                player_data = []

                items = row.find_all(class_='table-row-item')
                sets_div = items[2]
                sets = sets_div.find_all('div', class_='columns-item')
                text_arr = [ll.text.strip() for ll in sets]

                for item in items[:2]: # No and Player name
                    col_text = item.text.strip()

                    libero = item.find(class_='libero')
                    if libero:
                        col_text = col_text[:-1]

                    player_data.append(col_text)

                for i in range(number_of_sets):
                    item = text_arr[i] if i < len(text_arr) else '*'
                    if item.isnumeric():
                        player_data.append(item)
                    else:
                        player_data.append('0')
                    
                starters.append(player_data)


            sorted_players= list(sorted(players, key=lambda x: int(x[0])))
            sorted_starters = list(sorted(starters, key=lambda x: int(x[0])))

            final_data[f'team{team_letter}-players'] = sorted_players
            final_data[f'team{team_letter}-starting'] = sorted_starters
            
            driver.switch_to.default_content()

        all_match_data.append(final_data)
        time.sleep(random.randint(2, 3))


    with open(final_dump_name, 'w') as f:
        json.dump(all_match_data, f)

# Close the browser
driver.quit()



