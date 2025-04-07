from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import requests
import os
import pdfplumber
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path

poppler = 'C:\\Users\\Jingyan\\Desktop\\poppler-24.08.0\\Library\\bin'

driver = webdriver.Chrome()

LEAGUE = 'vnl'
YEARS = ['2021', '2022', '2023', '2024']
# YEARS = ['2022', '2023', '2024']


match_numbers = {
   '2021': [11700, 11824],
   '2022': [13650, 13754],
   '2023': [16128, 16232],
   '2024': [18853, 18957],
}

def sort_table(table):
    return sorted(table, key=lambda row: int(row[0]))
 
def save_to_local_link(link, output_filename):
   try:
      response = requests.get(link, stream=True)
      response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
      
      with open(output_filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
               if chunk:
                  file.write(chunk)
      
      print(f"Download completed: {output_filename}")
   except requests.exceptions.RequestException as e:
      print(f"Error downloading the file: {e}")


def extract_subimages(input_image_path, output_image_path_1, output_image_path_2,
    coords_1,coords_2):

    with Image.open(input_image_path) as img:
        subimage_1 = img.crop(coords_1)
        subimage_1.save(output_image_path_1)
        
    with Image.open(input_image_path) as img:
        subimage_2 = img.crop(coords_2)
        subimage_2.save(output_image_path_2)
        
def detect_black_squares(image_path, num_rows=14, max_squares=5):
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Could not load the image")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Get image dimensions
    height, width = gray.shape
    
    # Estimate the height of each row
    row_height = height // num_rows
    
    # Estimate the width of each square
    # Assuming squares are at the right side of the image and are approximately square
    square_width = row_height
    
    # Calculate the starting x-coordinate for the squares region
    # Assuming the squares start at approximately 70% of the image width
    squares_start_x = int(width * 0.655)
    
    y_offset = 10
    
    # Initialize results array with False values
    results = [[False for _ in range(max_squares)] for _ in range(num_rows)]
    
    # Process each row
    for row_idx in range(num_rows):
        # Calculate the y-coordinate for the current row
        row_y = row_idx * row_height + y_offset
        
        # Process each potential square in the row
        for square_idx in range(max_squares):
            # Calculate the x-coordinate for the current square
            # Distribute evenly across the remaining width
            remaining_width = width - squares_start_x
            square_spacing = remaining_width / max_squares
            square_x = squares_start_x + int(square_idx * square_spacing)
            
            # Define the region of interest (ROI) for the current square
            roi = gray[row_y:row_y+row_height, square_x:square_x+int(square_spacing)]
            
            # Skip if ROI is empty
            if roi.size == 0:
                continue
            
            # Calculate average pixel value in the ROI
            avg_pixel_value = np.mean(roi)
            
            # If average pixel value is below threshold, consider it a black square
            # Lower values are darker in grayscale
            if avg_pixel_value < 125:  # Threshold value can be adjusted
                results[row_idx][square_idx] = True
    
    return results
 
def extract_pdf_tables(pdf_path, match_id, year):
    images = convert_from_path(pdf_path, dpi=400, first_page=1, last_page=1, poppler_path=poppler)

    first_page_image = images[0]
    image_name = f'vnl/{year}/{match_id}.png'
    first_page_image.save(image_name, 'PNG')

    output_subimage_1 = f'vnl/{year}/{match_id}_1.jpg'
    output_subimage_2 = f'vnl/{year}/{match_id}_2.jpg'

    coords_for_subimage_1 = (150, 1317, 1210, 2210)
    coords_for_subimage_2 = (1660, 1317, 2725, 2210)
        
    extract_subimages(image_name, output_subimage_1, output_subimage_2, 
                      coords_for_subimage_1, coords_for_subimage_2)
    
    A_image = detect_black_squares(output_subimage_1)
    B_image = detect_black_squares(output_subimage_2)
    
    return A_image, B_image
 
   
def scrape_sets(match_id, pdf_path, num_sets, year, A_team_unsorted, B_team_unsorted):
   A_team = sorted(A_team_unsorted, key=lambda x: int(x[0]))
   B_team = sorted(B_team_unsorted, key=lambda x: int(x[0]))
   
   if match_id == 16189 or match_id == 16191:
      return [], []

   A_B_images = extract_pdf_tables(pdf_path, match_id, year)

   with pdfplumber.open(pdf_path) as pdf:
      page_tables = pdf.pages[0].extract_tables()

   teamA_slice = [player[:2] for player in A_team]
   teamB_slice = [player[:2] for player in B_team]

   A_B_table = page_tables[2:4]
   A_B_team = [teamA_slice, teamB_slice]
   A_B_letters = ['a', 'b']

   for i in range(2):
      letter = A_B_letters[i]
      print(match_id, letter)
      
      table = A_B_table[i]
      team = A_B_team[i]
      image = A_B_images[i]
      team_numbers = [player[0] for player in team]
      
      rows = table[3:-1]
      
      names = rows[0][0].split('\n')
      
      # assert len(names) == len(rows)

      for index in range(len(names)):
         name = names[index]
         cha = ''
         digit_index = 0
         while name[digit_index].isdigit():
               cha += name[digit_index]
               digit_index += 1
               
         rows[index][0] = cha
      
      if match_id == 11772 and i == 1:
         rows[3][0] = '20'
         rows[10][0] = '23'

      processed_rows_presort = [row[:6] for row in rows if row[0] in team_numbers]
      

      for set in range(num_sets):
         column = [row[set + 1] for row in processed_rows_presort]
         for player_index in range(len(column)):
               if not image[player_index][set]:
                  column[player_index] = '0'

               col = column[player_index]
               team[player_index].append(col)

                  
      true_counter = 0
      for b1 in range(14):
         for b2 in range(5):
               if image[b1][b2]:
                  true_counter += 1
                  
      assert true_counter == (num_sets) * 6
      
      # Sort after erasing the stuff
      sorted_rows_presort = sorted(processed_rows_presort, key=lambda p:int(p[0]))
      processed_rows = [row[1:6] for row in sorted_rows_presort]
      
      assert len(team) == len(processed_rows)

               
   return A_B_team
 
 
 ## MAIN FUNCTIONS

for YEAR in YEARS:
   all_match_data = []
   for match_id in range(match_numbers[YEAR][0], match_numbers[YEAR][1]):
      # We skip these match ids as their reports do not exist
      if str(match_id) == '13686' or str(match_id) == '13691' or str(match_id) == '16189' or str(match_id) == '16191':
         continue
      
      # We skip these match ids as their reports do not tally with the scraped data
      if str(match_id) == '16216':
         continue
   
      url = f'https://en.volleyballworld.com/volleyball/competitions/volleyball-nations-league/schedule/{match_id}/#boxscore'
      driver.get(url)

      driver.implicitly_wait(30)

      html = driver.page_source

      soup = BeautifulSoup(html, 'html.parser')

      match = {}
      tmp_json = {}

      AB_map = {
         0: 'a',
         1: 'b'
      }
      
      for i in range(2):
         search_team = f'team{AB_map[i]}'
         scoring = soup.find('table', {'data-team':search_team, 'data-stattype':'scoring', "data-set":"all"})

         while scoring is None:
            # Retries for the first table, assume all other tables loaded if this is loaded
            driver.refresh()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            time.sleep(3)
            scoring = soup.find('table', {'data-team':search_team, 'data-stattype':'scoring', "data-set":"all"})

         attack = soup.find('table', {'data-team':search_team, 'data-stattype':'attack', "data-set":"all"})
         block = soup.find('table', {'data-team':search_team, 'data-stattype':'block', "data-set":"all"})
         serve = soup.find('table', {'data-team':search_team, 'data-stattype':'serve', "data-set":"all"})
         reception = soup.find('table', {'data-team':search_team, 'data-stattype':'reception', "data-set":"all"})
         dig = soup.find('table', {'data-team':search_team, 'data-stattype':'dig', "data-set":"all"})
         set = soup.find('table', {'data-team':search_team, 'data-stattype':'set', "data-set":"all"})

         all_tables = {
            'scoring': scoring, 
            'attack': attack, 
            'block': block, 
            'serve': serve, 
            'reception': reception, 
            'dig': dig, 
            'set':set
         }

         for key in all_tables:
            table = all_tables[key]
            rows = table.find_all('tr') if table else []

            if len(rows) == 0:
               print(f'{match_id} {key}')
            
            data_list = []

            for row in rows[1:]:  # Skip header row
               cols = row.find_all('td')
               if cols:
                  data = [col.text.strip() for col in cols]
                  if data[1].endswith("(C)") or data[1].endswith("(c)"):
                        data[1] = " ".join(data[1].split(" ")[:-1])
                  data_list.append(data)

            tmp_json[key + AB_map[i]] = data_list
      
      
      team_names = soup.find_all('div', class_='vbw-mu__team__name--abbr')
      team1_name = team_names[0].getText().strip()
      team2_name = team_names[1].getText().strip()

      score_home = soup.find_all('div', class_='vbw-mu__score--home')[0].getText()
      score_away = soup.find_all('div', class_='vbw-mu__score--away')[0].getText()
      sum_of_sets = int(score_away) + int(score_home)

      sets_A = list(map(lambda x: x.getText(), filter(lambda x: x.getText(), soup.find_all('span', class_='vbw-mu__pointA'))))[:sum_of_sets]
      sets_B = list(map(lambda x: x.getText(), filter(lambda x: x.getText(), soup.find_all('span', class_='vbw-mu__pointB'))))[:sum_of_sets]


      ## Block
      
      time_div = soup.find('div', class_='vbw-mu__time-wrapper')
      attrs = time_div.attrs
      date = attrs['data-utc-datetime']
      date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
      formatted_date = str(date_obj.date())
      
      button_tag = soup.find('a', class_='fa-button')
      link = button_tag.get('href')
      output_directory = f'vnl/{YEAR}'
      output_filename = f"vnl/{YEAR}/{match_id}.pdf"
      if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
      num_sets = int(score_home) + int(score_away)
      save_to_local_link(link, output_filename)
      A_starters, B_starters = scrape_sets(match_id, output_filename, num_sets, YEAR, tmp_json["scoringa"], tmp_json["scoringb"])

      match["match_id"] = match_id
      match["teamA"] = team1_name
      match["teamB"] = team2_name
      match["teamA_score"] = score_home
      match["teamB_score"] = score_away
      match["match_date"] = formatted_date
      match["teamA_sets"] = sets_A
      match["teamB_sets"] = sets_B
      match["teama-starting"] = A_starters
      match["teamb-starting"] = B_starters
      
      categories = ['attack', 'block', 'serve', 'reception', 'dig', 'set']
      AB_mapping = ['a', 'b']
      for letter in AB_mapping:
         first_player_numbers = None
         global_table = None

         for category in categories:
               table_name = category + letter
               table = tmp_json[table_name]
               sorted_table = sort_table(table)
               player_numbers = list(map(lambda row: int(row[0]), sorted_table))
               if first_player_numbers:
                  assert first_player_numbers == first_player_numbers
                  global_table = [a + b[3:] for a, b in zip(global_table, sorted_table)]
                  
               else:
                  first_player_numbers = player_numbers
                  global_table = sorted_table
         
         match[f"team{letter}-players"] = global_table
      ## Block

      all_match_data.append(match)
      
      # break
      
   with open(f'{LEAGUE}/{YEAR}-vnl-data.json', 'w') as f:
      json.dump(all_match_data, f)

driver.quit()

