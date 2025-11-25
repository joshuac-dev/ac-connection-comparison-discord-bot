"""Scoring calculations for Base Opportunity Score."""

import math
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not available, environment variables will be read directly
    pass


# BOS Profile Configuration
# Load profile from environment with default to 'balanced'
BOS_PROFILE = os.environ.get("BOS_PROFILE", "balanced").lower()

# Profile parameter definitions
PROFILES = {
    "balanced": {
        "POP_EXP": 0.85,
        "INCOME_EXP": 1.25,
        "COMP_SCALE": 25000,
        "COMP_EXP": 1.2,
        "DIST_MU": 1500,
        "DIST_SIGMA": 1200,
        "DIST_FLOOR": 0.25,
        "DIST_PEAK": 1.8,
    },
    "growth": {
        "POP_EXP": 0.9,
        "INCOME_EXP": 1.3,
        "COMP_SCALE": 25000,
        "COMP_EXP": 1.0,
        "DIST_MU": 1400,
        "DIST_SIGMA": 1200,
        "DIST_FLOOR": 0.3,
        "DIST_PEAK": 2.0,
    },
    "conservative": {
        "POP_EXP": 0.8,
        "INCOME_EXP": 1.2,
        "COMP_SCALE": 25000,
        "COMP_EXP": 1.4,
        "DIST_MU": 1600,
        "DIST_SIGMA": 1200,
        "DIST_FLOOR": 0.25,
        "DIST_PEAK": 1.6,
    },
}

# Select active profile
if BOS_PROFILE not in PROFILES:
    print(f"Warning: Unknown BOS_PROFILE '{BOS_PROFILE}', defaulting to 'balanced'")
    BOS_PROFILE = "balanced"

ACTIVE_PROFILE = PROFILES[BOS_PROFILE]

# Extract parameters from active profile
POP_EXP = ACTIVE_PROFILE["POP_EXP"]
INCOME_EXP = ACTIVE_PROFILE["INCOME_EXP"]
COMP_SCALE = ACTIVE_PROFILE["COMP_SCALE"]
COMP_EXP = ACTIVE_PROFILE["COMP_EXP"]
DIST_MU = ACTIVE_PROFILE["DIST_MU"]
DIST_SIGMA = ACTIVE_PROFILE["DIST_SIGMA"]
DIST_FLOOR = ACTIVE_PROFILE["DIST_FLOOR"]
DIST_PEAK = ACTIVE_PROFILE["DIST_PEAK"]


def calculate_bos(
    population: float,
    income_level: float,
    competition: float,
    distance: float,
    openness: float = 5.0,
) -> Optional[float]:
    """
    Calculate Base Opportunity Score (BOS) for an airport.
    
    The BOS formula uses a smooth, tunable approach that considers:
    - Economic potential: population and income with configurable exponents
    - Competition dampening: log-based penalty with diminishing returns
    - Distance preference: Gaussian-shaped weighting around optimal stage length
    - Country openness: multiplier that rewards higher openness levels
    
    Args:
        population: Airport population (passenger demand indicator)
        income_level: Income level at airport (affects ticket prices)
        competition: Total competition seats from existing airlines
        distance: Distance from HQ in kilometers
        openness: Country openness level (0-10, default: 5.0)
    
    Returns:
        Float BOS score, or None if inputs are invalid (zero/negative population or income)
    """
    # Validate inputs - return None for invalid data
    if population <= 0 or income_level <= 0:
        return None
    
    # 1. Economic Term: population^POP_EXP * income^INCOME_EXP
    # This reduces overweighting of tiny but wealthy cities
    economics = (population ** POP_EXP) * (income_level ** INCOME_EXP)
    
    # 2. Competition Dampening: log-based penalty
    # comp_pen = (1 + ln(1 + seats/COMP_SCALE))^COMP_EXP
    # Provides diminishing marginal penalty in very crowded hubs
    if competition < 0:
        competition = 0
    comp_ratio = competition / COMP_SCALE
    comp_pen = (1 + math.log(1 + comp_ratio)) ** COMP_EXP
    
    # 3. Distance Weighting: Gaussian-shaped preference
    # Centered around DIST_MU (1500 km) with sigma ~DIST_SIGMA (1200 km)
    # Multiplier constrained to [DIST_FLOOR, DIST_PEAK]
    # This avoids sharp steps while preferring realistic stage lengths
    distance_variance = DIST_SIGMA ** 2
    gaussian = math.exp(-((distance - DIST_MU) ** 2) / (2 * distance_variance))
    # Scale and constrain to [DIST_FLOOR, DIST_PEAK]
    dist_weight = DIST_FLOOR + (DIST_PEAK - DIST_FLOOR) * gaussian
    
    # 4. Openness Weighting
    # openness in [0..10] -> multiplier in [0.9..1.1]
    # openness_weight = 0.9 + 0.02 * openness
    # Clamp openness to valid range
    openness_clamped = max(0, min(10, openness))
    openness_weight = 0.9 + 0.02 * openness_clamped
    
    # 5. Final BOS Calculation
    bos = (economics / comp_pen) * dist_weight * openness_weight
    
    return bos
