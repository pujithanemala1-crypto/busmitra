"""
BUSMITRA - Calculation Utilities
Centralizes calculation logic for passenger counts, seat availability,
crowd density thresholds, geographic distance (Haversine), and ETA.
"""
import math
from typing import Dict, Any, Tuple
from app.config import settings

def calculate_occupancy_metrics(
    capacity: int,
    in_count: int,
    out_count: int
) -> Dict[str, Any]:
    """
    Core occupancy formula:
    Current Passengers = Max(0, in_count - out_count)
    Available Seats = Max(0, capacity - current_passengers)
    Occupancy % = (current_passengers / capacity) * 100
    """
    safe_capacity = max(1, capacity)
    # Never allow negative passengers
    current_passengers = max(0, in_count - out_count)
    available_seats = max(0, safe_capacity - current_passengers)
    occupancy_pct = round((current_passengers / safe_capacity) * 100.0, 1)

    # Threshold evaluation
    if occupancy_pct <= settings.CROWD_LOW_THRESHOLD:
        crowd_level = "LOW"
    elif occupancy_pct <= settings.CROWD_MOD_THRESHOLD:
        crowd_level = "MODERATE"
    elif occupancy_pct <= settings.CROWD_HIGH_THRESHOLD:
        crowd_level = "HIGH"
    else:
        crowd_level = "OVERCROWDED"

    return {
        "capacity": safe_capacity,
        "total_in": in_count,
        "total_out": out_count,
        "current_passengers": current_passengers,
        "available_seats": available_seats,
        "occupancy_percentage": occupancy_pct,
        "crowd_level": crowd_level
    }

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two GPS coordinates in kilometers.
    """
    R = 6371.0 # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def calculate_eta_minutes(distance_km: float, speed_kmh: float, fallback_avg_speed: float = 40.0) -> int:
    """
    Estimates travel time in minutes based on distance and speed.
    """
    effective_speed = speed_kmh if speed_kmh > 10.0 else fallback_avg_speed
    hours = distance_km / effective_speed
    return max(1, int(round(hours * 60.0)))
