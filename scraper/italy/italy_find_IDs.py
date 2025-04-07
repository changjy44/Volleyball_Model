from bs4 import BeautifulSoup
import re

from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

PATTERN = r'^https://www.legavolley.it/match/(\d+)$'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

YEARS = ['2021', '2022', '2023', '2024']

for YEAR in YEARS:
    source_file = f'italy/{YEAR}_src.txt'
    final_file = f'italy/{YEAR}_match_ids.txt'

    match_ids = []

    all_urls = []

    with open(source_file, "r") as f:
        for line in f:
            all_urls.append(line.strip())

    print(all_urls)

    for URL in all_urls:
        driver.get(URL)

        driver.implicitly_wait(30)

        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        for link in soup.find_all('a'):
            curr = str(link.get('href'))
            match = re.match(PATTERN, curr)

            if match:
                match_id = match.group(1) 
                match_ids.append(match_id)

    # Close the browser
    unique_links = list(set(sorted(match_ids)))
    print(len(unique_links))

    with open(final_file, 'a') as f:
        for i in unique_links:
            f.write(i)
            f.write("\n")
            
driver.quit()