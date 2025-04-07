import os
import pandas

LEAGUE = "lnv"

link_map = {
    '2021': "lnv-74-97-competition_matches.csv",
    '2022': "lnv-81-111-competition_matches.csv",
    '2023': "lnv-89-124-competition_matches.csv",
    '2024': "lnv-105-142-competition_matches.csv",
}

YEARS = ['2021', '2022', '2023', '2024']

for YEAR in YEARS:
    LINK = link_map[YEAR]

    csvFile = pandas.read_csv(f'france/{LINK}')
    incomplete = []
    for index, row in csvFile.iterrows():
        match_id = row['Match ID']
        os.system(f'volleystats --fed {LEAGUE} --match {match_id}')

        guest_file = f"data/{LEAGUE}-{match_id}-guest_stats.csv"
        home_file = f"data/{LEAGUE}-{match_id}-home_stats.csv"

        if os.path.getsize(guest_file) == 0 or os.path.getsize(home_file) == 0:
            print(match_id)
            incomplete.append(match_id)
            os.remove(guest_file)
            os.remove(home_file)
    