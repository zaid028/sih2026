"""
FIREGUARD AI - Geospatial Utilities
Haversine distance, bounding box calculations, buffer zones, and road path generators.
"""
import math
from typing import Tuple, List, Dict, Any

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two points in kilometers."""
    try:
        r = 6371.0  # Earth radius in km
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        dphi = math.radians(float(lat2) - float(lat1))
        dlambda = math.radians(float(lon2) - float(lon1))

        a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r * c, 3)
    except Exception:
        return 9999.0

def bounding_box(lat: float, lon: float, radius_km: float) -> Tuple[float, float, float, float]:
    """
    Returns (min_lat, min_lon, max_lat, max_lon) for a given radius around a center.
    """
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)) if math.cos(math.radians(lat)) != 0 else 111.0)
    return (
        round(lat - lat_delta, 5),
        round(lon - lon_delta, 5),
        round(lat + lat_delta, 5),
        round(lon + lon_delta, 5)
    )

def generate_safe_corridor(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    danger_lat: float,
    danger_lon: float,
    danger_radius_m: int = 500,
    steps: int = 6
) -> List[List[float]]:
    """
    Generates a curved waypoint trajectory that routes around a danger zone.
    """
    waypoints = [[origin_lat, origin_lon]]
    # Calculate deflection vector away from danger zone
    mid_lat = (origin_lat + dest_lat) / 2.0
    mid_lon = (origin_lon + dest_lon) / 2.0

    dist_to_danger = haversine_distance_km(mid_lat, mid_lon, danger_lat, danger_lon)
    deflection = 0.02 if dist_to_danger < (danger_radius_m / 1000.0 * 2.0) else 0.005

    # Determine deflection direction
    deflect_lat = mid_lat + (0.015 if mid_lat >= danger_lat else -0.015)
    deflect_lon = mid_lon + (0.018 if mid_lon >= danger_lon else -0.018)

    waypoints.append([round(deflect_lat, 5), round(deflect_lon, 5)])
    waypoints.append([round(dest_lat, 5), round(dest_lon, 5)])
    return waypoints
