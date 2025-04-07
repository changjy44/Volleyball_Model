# scraping all links

from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
from selenium.webdriver.chrome.options import Options



chrome_options = Options()
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument('--ignore-ssl-errors=yes')
# Set up Selenium WebDriver (ensure the appropriate driver is installed and in PATH)
driver = webdriver.Chrome(options=chrome_options)


# driver = webdriver.PhantomJS("C:/Users/chang/OneDrive/Desktop/FYP/volleyball-model/phantomjs-2.1.1-windows/bin/phantomjs.exe")

# YEAR = 2021
YEARS = [2021, 2022, 2023, 2024]

for YEAR in YEARS:
    with open(f'sql/vnl/{YEAR}-vnl-data-final.json') as f:
       matches = json.load(f)
    all_match_data = []

    for match in matches:
        match_id = match["match_id"]

        # Navigate to the webpage
        url = f'https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/schedule/{match_id}/#boxscore'
        driver.get(url)
        
        
        # driver.refresh()
        # Wait for the page to load (adjust time as needed)
        # driver.implicitly_wait(30)

        # Get the page source after JavaScript has rendered the content
        html = driver.page_source

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        search_team = 'teama'
        
        scoring = soup.find('table', {'data-team':search_team, 'data-stattype':'scoring', "data-set":"all"})

        while scoring is None:
            print(match_id, 'retry')
            # Retries for the first table, assume all other tables loaded if this is loaded
            driver.refresh()
            # driver.implicitly_wait(30)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(3)
            scoring = soup.find('table', {'data-team':search_team, 'data-stattype':'scoring', "data-set":"all"})
        
        button_tag = soup.find('a', class_='fa-button')
        link = button_tag.get('href')
        
        final_json = {}

        final_json['match_id'] = match_id
        final_json['link'] = link
        # print(final_json)

        all_match_data.append(final_json)

    with open(f'vnl/{YEAR}-vnl-links.json', 'w') as f:
        json.dump(all_match_data, f)

# Close the browser
driver.quit()

