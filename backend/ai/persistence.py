"""
FIREGUARD AI - Spatiotemporal Persistence & Anomaly Spike Detection
Clusters thermal hotspots within 350m spatial radius and computes 2.5-sigma recurrence anomalies.
"""
import math
from typing import List, Dict, Any, Tuple
from backend.utils.geo import haversine_distance_km

CLUSTER_RADIUS_KM = 0.350  # 350 meters
Z_SCORE_ANOMALY_THRESHOLD = 2.5

def analyze_hotspot_persistence(
    current_frp: float,
    current_lat: float,
    current_lon: float,
    historical_hotspots: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyzes historical hits around current location to determine persistence score,
    recurrence frequency, and if current FRP represents a 2.5σ anomaly spike.
    """
    nearby_hits = []
    frp_values = []

    for h in historical_hotspots:
        h_lat = float(h.get("latitude", 0))
        h_lon = float(h.get("longitude", 0))
        dist = haversine_distance_km(current_lat, current_lon, h_lat, h_lon)
        if dist <= CLUSTER_RADIUS_KM:
            nearby_hits.append(h)
            frp_values.append(float(h.get("frp", 30.0)))

    detection_count = len(nearby_hits) + 1  # include current
    frp_values.append(current_frp)

    avg_frp = round(sum(frp_values) / len(frp_values), 2)
    # Variance and standard deviation
    if len(frp_values) > 1:
        variance = sum((x - avg_frp) ** 2 for x in frp_values) / (len(frp_values) - 1)
        std_dev = math.sqrt(variance)
    else:
        std_dev = 5.0

    z_score = round((current_frp - avg_frp) / (std_dev if std_dev > 0.1 else 1.0), 2)
    is_spike = bool(z_score >= Z_SCORE_ANOMALY_THRESHOLD and current_frp > 45.0)

    # Persistence score (0 - 100) based on hit count and temporal clustering
    persistence_score = min(100.0, round(detection_count * 7.5, 1))

    return {
        "detection_count": detection_count,
        "detection_frequency": round(min(1.0, detection_count / 15.0), 2),
        "average_frp": avg_frp,
        "std_dev_frp": round(std_dev, 2),
        "z_score": z_score,
        "is_anomalous_spike": is_spike,
        "persistence_score": persistence_score
    }
