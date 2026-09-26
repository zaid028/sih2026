"""
FIREGUARD AI - OpenStreetMap (OSM) & Overpass API Service
Queries OSM for industrial facilities, refineries, factories, chemical plants,
fire stations, and hospitals, enriched with spatial metadata.
"""
import math
import requests
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class OSMService:
    @staticmethod
    def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two points in meters."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @classmethod
    def query_overpass_bbox(cls, south: float, west: float, north: float, east: float) -> list:
        """
        Query OSM Overpass API for industrial tags within bounding box:
        [out:json][timeout:25];
        (
          node["industrial"](south, west, north, east);
          way["industrial"](south, west, north, east);
          node["man_made"="works"](south, west, north, east);
        );
        out center;
        """
        query = f"""
        [out:json][timeout:15];
        (
          node["industrial"]({south},{west},{north},{east});
          way["industrial"]({south},{west},{north},{east});
          node["man_made"="works"]({south},{west},{north},{east});
          node["amenity"="fire_station"]({south},{west},{north},{east});
          node["amenity"="hospital"]({south},{west},{north},{east});
        );
        out center;
        """
        try:
            resp = requests.post(Config.OVERPASS_ENDPOINT, data={"data": query}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("elements", [])
        except Exception as e:
            logger.warning(f"Overpass query failed: {e}. Using local cached OSM catalog.")
        return []

    @classmethod
    def find_nearest_facility(cls, lat: float, lon: float, facilities: list) -> tuple:
        """
        Find closest industrial facility from a list of facility dicts/models.
        Returns: (nearest_facility, distance_meters)
        """
        if not facilities:
            return None, None

        best_facility = None
        min_dist = float("inf")

        for f in facilities:
            f_lat = f.get("latitude") if isinstance(f, dict) else f.latitude
            f_lon = f.get("longitude") if isinstance(f, dict) else f.longitude
            dist = cls.haversine_distance_m(lat, lon, f_lat, f_lon)
            if dist < min_dist:
                min_dist = dist
                best_facility = f

        return best_facility, min_dist
