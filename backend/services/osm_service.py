"""
FIREGUARD AI - OSMService (Requirement 4 & 5)
Provides OpenStreetMap geospatial lookups for facilities, emergency services, and road infrastructure.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.entities import IndustrialFacility, EmergencyService
from backend.integrations.osm_client import osm_client
from backend.utils.geo import haversine_distance_km

class OSMService:
    """Service handling OpenStreetMap data queries and database fallbacks."""

    @staticmethod
    def get_nearby_facilities(db: Session, lat: float, lon: float, radius_km: float = 25.0) -> List[Dict[str, Any]]:
        """Find industrial facilities near coordinates, checking database and live OSM."""
        facilities = db.query(IndustrialFacility).all()
        result = []
        for f in facilities:
            dist = haversine_distance_km(lat, lon, f.latitude, f.longitude)
            if dist <= radius_km:
                d = f.to_dict()
                d["distance_km"] = dist
                result.append(d)

        # Sort by distance
        result.sort(key=lambda x: x["distance_km"])
        if result:
            return result

        # Query live OSM Overpass
        osm_facilities = osm_client.find_facilities(lat, lon, radius_m=int(radius_km * 1000))
        return osm_facilities

    @staticmethod
    def get_nearby_emergency_services(
        db: Session,
        lat: float,
        lon: float,
        radius_km: float = 30.0,
        service_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find hospitals, fire stations, and police stations near coordinates."""
        query = db.query(EmergencyService)
        if service_type:
            query = query.filter(EmergencyService.service_type == service_type)

        all_services = query.all()
        results = []
        for s in all_services:
            dist = haversine_distance_km(lat, lon, s.latitude, s.longitude)
            if dist <= radius_km:
                d = s.to_dict()
                d["distance_km"] = dist
                d["distance"] = dist
                results.append(d)

        results.sort(key=lambda x: x["distance_km"])
        if results:
            return results

        # Live OSM query fallback
        live_data = osm_client.find_emergency_services(lat, lon, radius_m=int(radius_km * 1000))
        flat_results = []
        for cat, items in live_data.items():
            if not service_type or service_type in cat:
                flat_results.extend(items)
        flat_results.sort(key=lambda x: x.get("distance_km", 999))
        return flat_results

    @staticmethod
    def get_nearest_emergency_service(
        db: Session,
        lat: float,
        lon: float,
        service_type: str = "hospital"
    ) -> Optional[Dict[str, Any]]:
        """Get single nearest emergency service of specified type."""
        services = OSMService.get_nearby_emergency_services(db, lat, lon, radius_km=100.0, service_type=service_type)
        return services[0] if services else None

    @staticmethod
    def get_nearby_roads(lat: float, lon: float, radius_km: float = 5.0) -> List[Dict[str, Any]]:
        """Get arterial roads from OSM or fallback."""
        roads = osm_client.find_nearby_roads(lat, lon, radius_m=int(radius_km * 1000))
        if not roads:
            roads = [
                {"name": "National Highway 27 (NH-27)", "highway_type": "trunk", "maxspeed": "80 km/h"},
                {"name": "State Highway 6 (SH-6 Bypass)", "highway_type": "primary", "maxspeed": "60 km/h"},
                {"name": "Refinery Perimeter Access Road", "highway_type": "secondary", "maxspeed": "40 km/h"}
            ]
        return roads

    @staticmethod
    def analyze_location(db: Session, lat: float, lon: float, radius_km: float = 25.0) -> Dict[str, Any]:
        """Comprehensive spatial correlation around coordinate (Requirement 5)."""
        facilities = OSMService.get_nearby_facilities(db, lat, lon, radius_km=radius_km)
        nearest_fac = facilities[0] if facilities else None
        dist_to_fac = nearest_fac["distance_km"] if nearest_fac else 999.0

        hospitals = OSMService.get_nearby_emergency_services(db, lat, lon, radius_km=radius_km, service_type="hospital")
        fire_stations = OSMService.get_nearby_emergency_services(db, lat, lon, radius_km=radius_km, service_type="fire_station")
        police = OSMService.get_nearby_emergency_services(db, lat, lon, radius_km=radius_km, service_type="police")
        roads = OSMService.get_nearby_roads(lat, lon, radius_km=5.0)

        # Estimate population context based on proximity to facilities
        pop_density = "High Industrial Density" if dist_to_fac < 2.0 else "Rural / Mixed Semi-Urban"
        est_workforce = 4500 if dist_to_fac < 1.0 else 350

        return {
            "nearest_facility": nearest_fac,
            "distance_to_facility": dist_to_fac,
            "nearby_hospitals": hospitals[:5],
            "nearby_fire_stations": fire_stations[:5],
            "nearby_police": police[:5],
            "nearby_roads": roads[:5],
            "population_context": {
                "density_category": pop_density,
                "estimated_personnel_in_1km": est_workforce,
                "vulnerable_structures_nearby": 3 if dist_to_fac < 1.5 else 0
            }
        }
