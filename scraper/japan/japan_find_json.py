import requests
import json

YEARS = ['2021', '2022', '2023', '2024']

match_numbers = {
   '2021': [1, 300 + 1],
   '2022': [101, 285 + 1],
   '2023': [101, 287 + 1],
   '2024': [101, 287 + 1],
}

for YEAR in YEARS:
    for match_id in range(match_numbers[YEAR][0], match_numbers[YEAR][1]):

        url = f"https://www.svleague.jp/api/livescore/data/{match_id}?year={YEAR}&lang=en"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            with open(f'japan/match_{match_id}.json', 'w') as f:
                json.dump(data, f)

        else:
            print(f"Error: {response.status_code}")

