import json

LEAGUES = ['france']
YEARS = ['2021', '2022', '2023', '2024']

poland_mapping = {
    "Enea Czarni Radom": "Cerrad Enea Czarni Radom",
    "BOGDANKA LUK Lublin": "LUK Lublin",
    "LUK  Lublin": "LUK Lublin",
    "VERVA Warszawa ORLEN Paliwa": "Projekt Warszawa",
    "Stal Nysa": "PSG Stal Nysa",
    "KGHM Cuprum Lubin": "Cuprum Lubin"
}

italy_mapping = {
    "Consar RCM Ravenna": "Consar Ravenna",
    "Kioene Padova": "Pallavolo Padova",
    "Leo Shoes PerkinElmer Modena": "Valsa Group Modena",
    "Leo Shoes Modena": "Valsa Group Modena",
    "WithU Verona": "Rana Verona",
    "Verona Volley": "Rana Verona",
    "NBV Verona": "Rana Verona",
    "Sir Safety Susa Perugia": "Sir Susa Vim Perugia",
    "Sir Safety Conad Perugia": "Sir Susa Vim Perugia",
    "Mint Vero Volley Monza": "Vero Volley Monza"
}

japan_mapping = {
    "F.C.TOKYO": "Tokyo Great Bears",
    "NIPPON STEEL SAKAI BLAZERS": "SAKAI Blazers"
}

mapping = {
    'sÃ¨te': 'sete',
    'nantes rezÃ©': 'nantes reze'
}


for league in LEAGUES:
    for year_index in range(len(YEARS)):
        
        training_year = YEARS[year_index]

        with open(f'data/{league}/{training_year}-{league}-data-final-v3.json') as f:
            matches = json.load(f)

        allmatch = []
        
        for match in matches:
            new_match = match
            
            new_match['teamA'] = mapping[new_match['teamA']] if new_match['teamA'] in mapping else new_match['teamA']
            new_match['teamB'] = mapping[new_match['teamB']] if new_match['teamB'] in mapping else new_match['teamB']
                
            allmatch.append(new_match)
        
        with open(f'data/{league}/{training_year}-{league}-data-final-v3-draft.json', 'w') as f:
            json.dump(allmatch, f)
            
