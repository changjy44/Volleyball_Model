import random

print_var = False

def random_betting(league, year, matches, train_matches, odds_all, probability_arr, wager=100, rounds=1000):
    init_capital = 10000 * rounds
    capital = init_capital
    id = 0
    correctly_predicted = 0

    badBets = 0
    lostBets = 0
    wonBets = 0

    for round in range(rounds):
        for match, odds in zip(matches, odds_all):
            teamA = match['teamA']
            teamB = match['teamB']

            teamA_score = match['teamA_score']
            teamB_score = match['teamB_score']
            teamA_wins_result = teamA_score > teamB_score
            
            oddsA = float(odds[2])
            oddsB = float(odds[3])
            
            if teamA not in train_matches or teamB not in train_matches:
                continue
            
            if oddsA == 0:
                id += 1
                continue

            probability = random.random()
            teamA_wins_predicted = probability > 0.5

            if teamA_wins_predicted == teamA_wins_result:
                correctly_predicted += 1

            id += 1

            betOdds = oddsA if teamA_wins_predicted else oddsB
            
            if teamA_wins_predicted == teamA_wins_result:
                capital -= wager

                gain = betOdds * wager
                capital += gain
                wonBets += 1
                
            else:
                capital -= wager
                lostBets += 1
                
    if print_var:
        print(f"================={league}/{year}/random===============")
        print(f"new capital: {capital}")
        print(f"% difference: {(100 * capital/init_capital) - 100}")
        print(f"bad bets: {badBets}")
        print(f"lost bets: {lostBets}")
        print(f"won bets: {wonBets}")
        print(f"% of bets won: {100 * wonBets/id}")
    
    return (100 * capital/init_capital) - 100

def favourite_betting(league, year, matches, train_matches, odds_all, probability_arr, wager=100):
    init_capital = 10000
    capital = init_capital
    id = 0
    correctly_predicted = 0

    badBets = 0
    lostBets = 0
    wonBets = 0

    for match, odds in zip(matches, odds_all):
        teamA = match['teamA']
        teamB = match['teamB']

        teamA_score = match['teamA_score']
        teamB_score = match['teamB_score']
        teamA_wins_result = teamA_score > teamB_score
        
        oddsA = float(odds[2])
        oddsB = float(odds[3])
        
        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        if oddsA == 0:
            id += 1
            continue


        teamA_wins_predicted = oddsA < oddsB

        if teamA_wins_predicted == teamA_wins_result:
            correctly_predicted += 1

        id += 1

        betOdds = oddsA if teamA_wins_predicted else oddsB
                
        if teamA_wins_predicted == teamA_wins_result:
            capital -= wager

            gain = betOdds * wager
            capital += gain
            wonBets += 1
            
        else:
            capital -= wager
            lostBets += 1

    if print_var:
        print(f"================={league}/{year}/favourites===============")
        print(f"new capital: {capital}")
        print(f"% difference: {(100 * capital/init_capital) - 100}")
        print(f"bad bets: {badBets}")
        print(f"lost bets: {lostBets}")
        print(f"won bets: {wonBets}")
        print(f"% of bets won: {100 * wonBets/id}")
        
    return (100 * capital/init_capital) - 100

def against_betting(league, year, matches, train_matches, odds_all, probability_arr, wager=100):
    init_capital = 10000
    capital = init_capital
    id = 0
    correctly_predicted = 0

    badBets = 0
    lostBets = 0
    wonBets = 0

    for match, odds in zip(matches, odds_all):
        teamA = match['teamA']
        teamB = match['teamB']

        teamA_score = match['teamA_score']
        teamB_score = match['teamB_score']
        teamA_wins_result = teamA_score > teamB_score
        
        oddsA = float(odds[2])
        oddsB = float(odds[3])
        
        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        if oddsA == 0:
            id += 1
            continue


        teamA_wins_predicted = oddsA > oddsB

        if teamA_wins_predicted == teamA_wins_result:
            correctly_predicted += 1

        id += 1

        betOdds = oddsA if teamA_wins_predicted else oddsB
        
        if teamA_wins_predicted == teamA_wins_result:
            capital -= wager

            gain = betOdds * wager
            capital += gain
            wonBets += 1
        else:
            capital -= wager
            lostBets += 1
            
    if print_var:
        print(f"================={league}/{year}/against===============")
        print(f"new capital: {capital}")
        print(f"% difference: {(100 * capital/init_capital) - 100}")
        print(f"bad bets: {badBets}")
        print(f"lost bets: {lostBets}")
        print(f"won bets: {wonBets}")
        print(f"% of bets won: {100 * wonBets/id}")
    
    return (100 * capital/init_capital) - 100


def model_betting(league, year, matches, train_matches, odds_all, probability_arr, wager=100):
    init_capital = 10000
    capital = init_capital
    id = 0
    correctly_predicted = 0

    badBets = 0
    lostBets = 0
    wonBets = 0

    for match, odds in zip(matches, odds_all):
        teamA = match['teamA']
        teamB = match['teamB']

        teamA_score = match['teamA_score']
        teamB_score = match['teamB_score']
        teamA_wins_result = teamA_score > teamB_score
        
        oddsA = float(odds[2])
        oddsB = float(odds[3])
        
        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        if oddsA == 0:
            id += 1
            continue

        probability = float(probability_arr[id])
        teamA_wins_predicted = probability > 0.5

        if teamA_wins_predicted == teamA_wins_result:
            correctly_predicted += 1

        id += 1

        betOdds = oddsA if teamA_wins_predicted else oddsB
        
        if teamA_wins_predicted == teamA_wins_result:
            capital -= wager

            gain = betOdds * wager
            capital += gain
            wonBets += 1
        else:
            capital -= wager
            lostBets += 1
            
    if print_var:
        print(f"================={league}/{year}/model===============")
        print(f"new capital: {capital}")
        print(f"% difference: {(100 * capital/init_capital) - 100}")
        print(f"bad bets: {badBets}")
        print(f"lost bets: {lostBets}")
        print(f"won bets: {wonBets}")
        print(f"% of bets won: {100 * wonBets/id}")
    
    return (100 * capital/init_capital) - 100

def kellybet(league, year, matches, train_matches, odds_all, probability_arr, limit=1):
    init_capital = 10000
    capital = init_capital
    id = 0
    correctly_predicted = 0

    badBets = 0
    lostBets = 0
    wonBets = 0

    for match, odds in zip(matches, odds_all):
        teamA = match['teamA']
        teamB = match['teamB']

        teamA_score = match['teamA_score']
        teamB_score = match['teamB_score']
        teamA_wins_result = teamA_score > teamB_score
        
        oddsA = float(odds[2])
        oddsB = float(odds[3])
        
        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        if oddsA == 0:
            id += 1
            continue

        probability = float(probability_arr[id])
        teamA_wins_predicted = probability > 0.5

        if teamA_wins_predicted == teamA_wins_result:
            correctly_predicted += 1

        id += 1
        
        betOdds = oddsA if teamA_wins_predicted else oddsB
        betProb = probability if teamA_wins_predicted else (1 - probability)
        
        potential_profit = betOdds - 1
        fraction = (betProb * potential_profit - (1 - betProb)) / potential_profit
        if fraction > limit:
            fraction = limit

        if fraction < 0:
            badBets += 1 

        elif teamA_wins_predicted == teamA_wins_result:
            wager = fraction * capital
            capital -= wager

            gain = betOdds * wager
            capital += gain
            wonBets += 1

        else:
            wager = fraction * capital
            capital -= wager
            lostBets += 1
            
    if print_var:
        print(f"================={league}/{year}/kellybet_{limit * 100}%===============")
        print(f"new capital: {capital}")
        print(f"% difference: {(100 * capital/init_capital) - 100}")
        print(f"bad bets: {badBets}")
        print(f"lost bets: {lostBets}")
        print(f"won bets: {wonBets}")
        print(f"% of bets won: {100 * wonBets/(lostBets + wonBets)}")
    
    return (100 * capital/init_capital) - 100


def difference_betting(league, year, matches, train_matches, odds_all, probability_arr, wager=100, margin=0.1):
    init_capital = 10000
    capital = init_capital
    id = 0
    correctly_predicted = 0

    badBets = 0
    lostBets = 0
    wonBets = 0
    
    for match, odds in zip(matches, odds_all):
        teamA = match['teamA']
        teamB = match['teamB']

        teamA_score = match['teamA_score']
        teamB_score = match['teamB_score']
        teamA_wins_result = teamA_score > teamB_score
        
        oddsA = float(odds[2])
        oddsB = float(odds[3])
        
        if teamA not in train_matches or teamB not in train_matches:
            continue
        
        if oddsA == 0:
            id += 1
            continue

        impliedProbA = 1 / oddsA
        impliedProbB = 1 / oddsB

        normalisedA = impliedProbA / (impliedProbA + impliedProbB)
        normalisedB = impliedProbB / (impliedProbA + impliedProbB)

        probability = float(probability_arr[id])

        if abs(probability - normalisedA) < margin:
            badBets += 1
            continue

        teamA_wins_predicted = probability > 0.5

        if teamA_wins_predicted == teamA_wins_result:
            correctly_predicted += 1

        id += 1

        betOdds = oddsA if teamA_wins_predicted else oddsB
        
        if teamA_wins_predicted == teamA_wins_result:
            capital -= wager

            gain = betOdds * wager
            capital += gain
            wonBets += 1
        else:
            capital -= wager
            lostBets += 1
            
    if print_var:
        print(f"================={league}/{year}/difference_{100 * margin}%===============")
        print(f"new capital: {capital}")
        print(f"% difference: {(100 * capital/init_capital) - 100}")
        print(f"bad bets: {badBets}")
        print(f"lost bets: {lostBets}")
        print(f"won bets: {wonBets}")
        print(f"% of bets won: {100 * wonBets/id}")
    
    return (100 * capital/init_capital) - 100