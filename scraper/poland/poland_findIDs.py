# scarpa all match_ids
from bs4 import BeautifulSoup
import re

from selenium import webdriver
from bs4 import BeautifulSoup


driver = webdriver.Chrome()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

YEARS = ['2021', '2022', '2023', '2024']

years_mapping = {
    '2021': 35,
    '2022': 38,
    '2023': 41,
    '2024': 44,
}

for YEAR in YEARS:
    file = f'poland/{YEAR}_match_ids.txt'
    url = f"https://www.plusliga.pl/games/tour/{years_mapping[YEAR]}.html"
    pattern = fr'^/games/action/show/id/(\d+)/tour/{years_mapping[YEAR]}\.html$'
    
    match_ids = []

    driver.get(url)

    driver.implicitly_wait(30)

    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    game_links = soup.find_all('section', class_='filterable-content ajax-synced-games')

    links = []

    for link in soup.find_all('a'):
        curr = str(link.get('href'))
        match = re.match(pattern, curr)

        if match:
            match_id = match.group(1) 
            links.append(match_id)

    unique_links = list(sorted(links))
    print(len(unique_links))

    with open(file, 'a') as f:
        for i in unique_links:
            f.write(i)
            f.write("\n")

# Close the browser
driver.quit()



