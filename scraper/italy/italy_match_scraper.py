from bs4 import BeautifulSoup

from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
import json
import time
import random

driver = webdriver.Chrome()

YEARS = ['2021', '2022', '2023', '2024']
YEARS = ['2023', '2024']

for YEAR in YEARS:
    match_ids = []
    src_file = f'italy/{YEAR}_match_ids.txt'
    final_dump_name = f'italy/{YEAR}-italy-data.json'
    
    with open(src_file, 'r') as f:
        for line in f:
            match_ids.append(line.strip())

    all_match_data = []

    for match_id in match_ids:
        print(match_id)
        final_data = {}

        url = f"https://www.legavolley.it/match/{match_id}"

        driver.get(url)

        driver.implicitly_wait(30)

        driver.execute_script("window.scrollBy(0, 500)")  # Scroll down by 500 pixels

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        AB_map = {
            0: 'a',
            1: 'b'
        }

        tables = soup.find_all('table', id='Tabellino')

        if len(tables) != 6:
            print(match_id)
            continue

        overall_score_table = tables[0]
        overall_score_table_rows = overall_score_table.find_all('tr')

        teamA_row = overall_score_table_rows[1]
        teamA_cols = teamA_row.find_all('td')
        teamA_name = teamA_cols[0].text.strip()
        teamA_score = teamA_cols[1].text.strip()
        
        teamB_row = overall_score_table_rows[2]
        teamB_cols = teamB_row.find_all('td')
        teamB_name = teamB_cols[0].text.strip()
        teamB_score = teamB_cols[1].text.strip()

        teamA_sets = []
        teamB_sets = []
        overall_sets_table = tables[2]
        overall_sets_table_rows = overall_sets_table.find_all('tr')
        for row in overall_sets_table_rows[1:-1]: # exclude header and tail
            cols = row.find_all('td')
            scoreline = cols[-1].text.strip()
            if scoreline == "0-0":
                break

            scoreline_break = scoreline.split("-")
            teamA_sets.append(scoreline_break[0].strip())
            teamB_sets.append(scoreline_break[1].strip())

        date_table = soup.find_all('table', id='Tabellino')[1]
        date_rows = date_table.find_all('tr')
        date_row = date_rows[1]
        date = date_row.find_all('td')[0].text.strip()
        date_obj = datetime.strptime(date, "%d/%m/%Y")
        formatted_date = str(date_obj.date())
        
        final_data['match_id'] = match_id
        final_data["teamA"] = teamA_name
        final_data["teamB"] = teamB_name
        final_data["teamA_score"] = teamA_score
        final_data["teamB_score"] = teamB_score 
        final_data["match_date"] = formatted_date
        final_data["teamA_sets"] = teamA_sets
        final_data["teamB_sets"] = teamB_sets

        tables = tables[3:5]

        for i in range(2):
            team_letter = AB_map[i]
            table = tables[i]

            rows = table.find_all('tr')

            assert len(rows) > 0

            all_players = []

            for row in rows[2:]: # skip two header rows
                cols = row.find_all('td')
                cols_text = [col.text.strip() for col in cols]

                if not cols_text[0].isnumeric():
                    continue

                if cols_text[1].endswith("(C)"):
                    cols_text[1] = cols_text[1].split("(C)")[0].strip()

                if cols_text[1].endswith("(L)"):
                    cols_text[1] = cols_text[1].split("(L)")[0].strip()
                
                first_two = cols_text[:2]
                last_cols = cols_text[8:]
                filtered_cols = first_two + last_cols

                assert len(filtered_cols) == 18

                all_players.append(filtered_cols)

            all_starters = []

            for row in rows[2:]: # skip two header rows
                cols = row.find_all('td')
                cols_text = [col.text.strip() for col in cols]

                if not cols_text[0].isnumeric():
                    continue

                if cols_text[1].endswith("(C)"):
                    cols_text[1] = cols_text[1].split("(C)")[0].strip()

                if cols_text[1].endswith("(L)"):
                    cols_text[1] = cols_text[1].split("(L)")[0].strip()
                
                first_two = cols_text[:2]
                sets = cols_text[3:8]

                for set in sets:
                    if set.isnumeric():
                        first_two.append(set)
                    else:
                        first_two.append('0')

                all_starters.append(first_two)
            
            final_data[f'team{team_letter}-players'] = all_players
            final_data[f'team{team_letter}-starting'] = all_starters

        all_match_data.append(final_data)
        # break
        time.sleep(random.randint(2, 3))


    with open(final_dump_name, 'w') as f:
        json.dump(all_match_data, f)

# Close the browser
driver.quit()



