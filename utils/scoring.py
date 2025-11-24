"""Scoring calculations for Base Opportunity Score."""

from typing import Optional


import math

def calculate_bos(population, income_level, competition, distance):
    # 1. Distance Factor (Synergy)
    # Using the provided Haversine utility from your geo.py
    # (Assuming simple distance calc here for the formula)
    
    dist = distance
    
    if dist < 200:
        d_factor = 0.1 # Cannibalization penalty
    elif 200 <= dist <= 3000:
        d_factor = 1.5 # Sweet spot for narrowbody connections
    else:
        d_factor = 1.0 # Long haul
        
    # 2. Core Economics (Pop * Income)
    # We increase the weight of Income significantly (power of 2)
    # We make population linear (power of 1)
    # We divide population by 1,000,000 just to keep the final score numbers readable
    pop_millions = population / 1000000
    
    # Example: 50 income becomes 2500 multiplier. 
    # This ensures rich cities dominate poor mega-cities.
    economics = (pop_millions) * (income_level ** 2)

    # 3. Competition Dampener
    # Instead of exponential punishment, we treat competition as "Noise"
    # We add a 50,000 seat "Buffer". 
    # If competition is < 50k, the denominator is basically constant.
    # If competition is 2M (Heathrow), the denominator scales linearly to suppress it slightly.
    competition_penalty = competition + 50000
    
    # 4. Final Calculation
    # We multiply by 1,000,000,000 just to get a nice integer score at the end
    bos = (economics / competition_penalty) * d_factor * 1000000000
    
    return int(bos)
