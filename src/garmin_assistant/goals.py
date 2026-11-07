"""Shared sport and distance conventions for setup and planning."""
from .readiness import number

SPORTS = {'swimming': ('游泳', 'Swimming'), 'cycling': ('自行车', 'Cycling'), 'running': ('跑步', 'Running')}
DISTANCE_LIMITS = {'swimming': 100, 'cycling': 1000, 'running': 200}


def validate_goal(sport, distance_km, minutes):
    if not isinstance(sport, str) or sport not in DISTANCE_LIMITS or not number(distance_km) or not 0 < distance_km <= DISTANCE_LIMITS[sport]:
        raise ValueError('Choose a supported sport and a positive target distance in km')
    if not number(minutes) or not 0 < minutes <= 1440:
        raise ValueError('Target time must be positive and at most 1440 minutes')
