import re
import unicodedata

def remove_accents(text):
    normalized = unicodedata.normalize('NFD', text)
    return ''.join(c for c in normalized if not unicodedata.combining(c))

def is_float(element):
    try:
        int(element)
        return False
    except ValueError:
        try:
            float(element)
            return True
        
        except ValueError:
            return False

def parse_odds(text):
    # Split text into lines
    lines = text.split('\n')
    
    results = []
    current_teams = []
    current_odds = []
    
    for line in lines:
        # # Skip empty lines and headers
        # if not line.strip() or 'Play Offs' in line or line.startswith('1') or line.startswith('2'):
        #     continue
        
        if line == 'award.' or line == 'canc.':
            continue
        
        # line = remove_accents(line)
        if line == '21 Apr 2024 - Placement Play Offs':
            i = 0
        
        # If line contains only a team name (no score)
        if re.match(r'^[A-Za-z-.\s]+$', line.strip()):
            current_teams.append(line.strip())

        # If line contains a floating point number (odds)
        if is_float(line.strip()):
            current_odds.append(line.strip())
            
        # print(line.strip(), current_odds)
        # When we have 2 teams and 2 odds, add them to results
        if len(current_teams) == 4 and len(current_odds) == 2:
            results.append({
                'team_a': current_teams[0],
                'team_b': current_teams[2],
                'odds_a': current_odds[0],
                'odds_b': current_odds[1]
            })
            current_teams = []
            current_odds = []
    
    return results

# Example usage
with open('parse_odds.txt', 'r') as file:
    text = file.read()

matches = parse_odds(text)

# Print results in requested format
for match in matches:
    print(f"{match['team_a']}, {match['team_b']}, {match['odds_a']}, {match['odds_b']}")

print(len(matches))