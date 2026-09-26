"""
FIREGUARD AI - OpenStreetMap / Overpass API Client
Queries real OpenStreetMap Overpass servers for industrial facilities, emergency services, and roads around coordinates, with intelligent fallback.
"""
from typing import List, Dict, Any, Optional
import requests
from backend.config.settings import settings
from backend.utils.geo import haversine_distance_km

class OSMClient:
    """Client for querying OpenStreetMap Overpass API."""

    def __init__(self):
        self._timeout = 10

    def query_overpass(self, ql_query: str) -> Optional[Dict[str, Any]]:
        """Execute raw Overpass QL query."""
        endpoint = settings.effective_osm_url
        try:
            resp = requests.post(endpoint, data={"data": ql_query}, timeout=self._timeout)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def find_facilities(self, lat: float, lon: float, radius_m: int = 5000) -> List[Dict[str, Any]]:
        """Query OSM for industrial facilities around lat, lon."""
        query = f"""
        [out:json][timeout:10];
        (
          node["landuse"="industrial"](around:{radius_m},{lat},{lon});
          way["landuse"="industrial"](around:{radius_m},{lat},{lon});
          node["man_made"="works"](around:{radius_m},{lat},{lon});
          way["man_made"="works"](around:{radius_m},{lat},{lon});
          node["industrial"](around:{radius_m},{lat},{lon});
        );
        out center 25;
        """
        data = self.query_overpass(query)
        facilities = []
        if data and "elements" in data:
            for el in data["elements"]:
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("operator") or "Industrial Site"
                el_lat = el.get("lat") or el.get("center", {}).get("lat", lat)
                el_lon = el.get("lon") or el.get("center", {}).get("lon", lon)
                dist = haversine_distance_km(lat, lon, el_lat, el_lon)
                facilities.append({
                    "osm_id": str(el.get("id")),
                    "name": name,
                    "facility_type": tags.get("industrial") or tags.get("man_made") or "Industrial Area",
                    "latitude": el_lat,
                    "longitude": el_lon,
                    "distance_km": dist,
                    "tags": tags
                })
        return facilities

    def find_emergency_services(self, lat: float, lon: float, radius_m: int = 15000) -> Dict[str, List[Dict[str, Any]]]:
        """Query OSM for hospitals, fire stations, and police stations."""
        query = f"""
        [out:json][timeout:10];
        (
          node["amenity"="hospital"](around:{radius_m},{lat},{lon});
          node["amenity"="fire_station"](around:{radius_m},{lat},{lon});
          node["amenity"="police"](around:{radius_m},{lat},{lon});
        );
        out center 30;
        """
        data = self.query_overpass(query)
        result = {"hospitals": [], "fire_stations": [], "police": []}
        if data and "elements" in data:
            for el in data["elements"]:
                tags = el.get("tags", {})
                amenity = tags.get("amenity")
                el_lat = el.get("lat") or el.get("center", {}).get("lat", lat)
                el_lon = el.get("lon") or el.get("center", {}).get("lon", lon)
                item = {
                    "osm_id": str(el.get("id")),
                    "name": tags.get("name") or f"Emergency Unit ({amenity})",
                    "latitude": el_lat,
                    "longitude": el_lon,
                    "distance_km": haversine_distance_km(lat, lon, el_lat, el_lon),
                    "phone": tags.get("phone") or tags.get("contact:phone") or "112",
                    "service_type": amenity
                }
                if amenity == "hospital":
                    result["hospitals"].append(item)
                elif amenity == "fire_station":
                    result["fire_stations"].append(item)
                elif amenity == "police":
                    result["police"].append(item)
        return result

    def find_nearby_roads(self, lat: float, lon: float, radius_m: int = 3000) -> List[Dict[str, Any]]:
        """Query OSM for primary and secondary highway links."""
        query = f"""
        [out:json][timeout:10];
        (
          way["highway"~"motorway|trunk|primary|secondary"](around:{radius_m},{lat},{lon});
        );
        out tags 20;
        """
        data = self.query_overpass(query)
        roads = []
        if data and "elements" in data:
            for el in data["elements"]:
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("ref") or "Major Arterial Road"
                roads.append({
                    "osm_id": str(el.get("id")),
                    "name": name,
                    "highway_type": tags.get("highway"),
                    "maxspeed": tags.get("maxspeed", "60 km/h")
                })
        return roads

osm_client = OSMClient()
