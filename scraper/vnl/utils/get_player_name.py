import pandas as pd
import json
import numpy as np
import math
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time


pd.set_option('display.max_columns', None)

# YEAR = 2021
YEARS = [2021, 2022, 2023, 2024]

AB_map = {
    0: 'a',
    1: 'b'
}

players_seen = {
   
}

def add_players(driver, match_id):
    url = f'https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/schedule/{match_id}/#boxscore'
    driver.get(url)

    driver.implicitly_wait(30)

    # Get the page source after JavaScript has rendered the content
    html = driver.page_source
    
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    for i in range(2):
        search_team = f'team{AB_map[i]}'
        scoring = soup.find('table', {'data-team':search_team, 'data-stattype':'scoring', "data-set":"all"})

        while scoring is None:
            # Retries for the first table, assume all other tables loaded if this is loaded
            driver.refresh()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(3)
            scoring = soup.find('table', {'data-team':search_team, 'data-stattype':'scoring', "data-set":"all"})


        rows = scoring.find_all('tr') if scoring else []

        if len(rows) == 0:
            print(f'{match_id}')

        for row in rows[1:]:  # Skip header row
            cols = row.find_all('a')
            if cols:
                for link in cols:
                    player_short_name = link.text.strip()
                    str_link = str(link.get('href')).strip()

                    if player_short_name not in players_seen:
                       players_seen[player_short_name] = str_link

    return 0

def get_full_name(driver, player):
    with open('vnl/players_full_name.txt', 'a', encoding='utf-8') as f:
        url = "https://en.volleyballworld.com" + players_seen[player]
        driver.get(url)

        driver.implicitly_wait(30)

        # Get the page source after JavaScript has rendered the content
        html = driver.page_source
        
        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        full_name_div = soup.find('h3', class_='vbw-player-name')
        while full_name_div is None:
            # Retries for the first table, assume all other tables loaded if this is loaded
            driver.refresh()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(3)
            full_name_div = soup.find('h3', class_='vbw-player-name')
        
        full_name = full_name_div.text.strip()

        f.write(f'{player}, {full_name}, {url}\n')

driver = webdriver.Chrome()
for YEAR in YEARS:
    with open(f'vnl/{YEAR}-vnl-data-standardized.json') as f:
       matches = json.load(f)

    count = 0

    for match in matches:
        add_players(driver, match["match_id"])
        count += 1
    #     if count == 1:
    #         break
    # break
for player in players_seen:
    with open('vnl/player_link.txt', 'a', encoding='utf-8') as f:
        f.write(f'{player}, {players_seen[player]}\n')


for player in players_seen:
    get_full_name(driver, player)

driver.close()