"""Scoring calculations for Base Opportunity Score."""

from typing import Optional


def calculate_bos(
    population: int,
    income_level: int,
    competition_seats: int,
    distance: float,
) -> Optional[float]:
    """
    Calculate Base Opportunity Score (BOS) for an airport.
    
    Args:
        population: Airport population
        income_level: Airport income level
        competition_seats: Total competition capacity (sum of link capacities)
        distance: Distance from HQ in kilometers
    
    Returns:
        BOS value or None if calculation not possible
    """
    # Handle missing or zero population/income
    if population <= 0 or income_level <= 0:
        return None
    
    # Distance factor based on distance ranges
    if distance < 200:
        d_factor = 0.1
    elif 200 <= distance <= 2000:
        d_factor = 1.5
    else:
        d_factor = 1.0
    
    # Competition score
    c_score = competition_seats / 10000
    
    # BOS formula
    bos = (
        (population ** 0.7) * (income_level ** 1.3)
    ) / ((1 + c_score) ** 1.5) * d_factor
    
    return bos
