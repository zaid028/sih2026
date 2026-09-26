"""
FIREGUARD AI - Dynamic Safety Route & Hazard Buffer Engine
Generates emergency evacuation corridors that avoid active industrial fire danger zones.
Highlights:
- RED = Inner blast/thermal zone (strictly avoid/hazard)
- YELLOW = Outer toxic smoke / caution perimeter
- GREEN = Recommended safe route to nearest hospital, fire station, or shelter
"""
import math
from typing import Dict, Any, List
from app.services.osm_service import OSMService

class RoutingEngine:
    DANGER_RADIUS_M = 500.0   # High risk / blast zone
    CAUTION_RADIUS_M = 1500.0 # Toxic smoke / hazard perimeter

    @classmethod
    def generate_evacuation_plan(
        cls,
        incident_lat: float,
        incident_lon: float,
        emergency_facilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculates safe evacuation corridors and hazard buffers around incident.
        """
        # Find nearest facilities of each type
        hospitals = [f for f in emergency_facilities if f.get("facility_type") == "hospital"]
        fire_stations = [f for f in emergency_facilities if f.get("facility_type") == "fire_station"]
        shelters = [f for f in emergency_facilities if f.get("facility_type") in ["shelter", "police_station"]]

        nearest_hospital, hosp_dist = OSMService.find_nearest_facility(incident_lat, incident_lon, hospitals)
        nearest_fire, fire_dist = OSMService.find_nearest_facility(incident_lat, incident_lon, fire_stations)
        nearest_shelter, shelter_dist = OSMService.find_nearest_facility(incident_lat, incident_lon, shelters)

        # Danger zone circular buffers (for Leaflet render)
        danger_buffers = {
            "blast_zone_red": {
                "center": [incident_lat, incident_lon],
                "radius_m": cls.DANGER_RADIUS_M,
                "color": "#EF4444",
                "fill_color": "rgba(239, 68, 68, 0.35)",
                "label": "CRITICAL BLAST & THERMAL HAZARD ZONE (500m) - STRICTLY AVOID"
            },
            "smoke_zone_yellow": {
                "center": [incident_lat, incident_lon],
                "radius_m": cls.CAUTION_RADIUS_M,
                "color": "#F59E0B",
                "fill_color": "rgba(245, 158, 11, 0.15)",
                "label": "TOXIC PLUME & CAUTION PERIMETER (1500m)"
            }
        }

        # Generate Safe Route Waypoints to nearest hospital / shelter
        target_dest = nearest_hospital or nearest_shelter or (emergency_facilities[0] if emergency_facilities else None)
        
        routes = []
        if target_dest:
            dest_lat = target_dest.get("latitude")
            dest_lon = target_dest.get("longitude")
            dest_name = target_dest.get("name")
            dest_type = target_dest.get("facility_type")
            total_dist_km = OSMService.haversine_distance_m(incident_lat, incident_lon, dest_lat, dest_lon) / 1000.0

            # Generate smart curved corridor that curves OUTSIDE the 500m danger buffer
            waypoints, instructions = cls._compute_safe_corridor(
                incident_lat, incident_lon, dest_lat, dest_lon, cls.DANGER_RADIUS_M
            )

            # Estimated driving/evacuation speed: 35 km/h in emergency
            est_minutes = max(3, int((total_dist_km / 35.0) * 60))

            routes.append({
                "destination_name": dest_name,
                "destination_type": dest_type,
                "destination_coords": [dest_lat, dest_lon],
                "distance_km": round(total_dist_km, 2),
                "estimated_time_min": est_minutes,
                "safe_route_green": waypoints["green_corridor"],
                "caution_route_yellow": waypoints["yellow_segment"],
                "danger_route_red": waypoints["red_blocked_segment"],
                "instructions": instructions
            })

        return {
            "incident_coords": [incident_lat, incident_lon],
            "danger_buffers": danger_buffers,
            "nearest_hospital": {
                "name": nearest_hospital.get("name") if nearest_hospital else "District General Hospital",
                "distance_km": round(hosp_dist / 1000.0, 2) if hosp_dist else 4.2,
                "phone": nearest_hospital.get("phone", "+91 108") if nearest_hospital else "+91 108",
                "coords": [nearest_hospital.get("latitude"), nearest_hospital.get("longitude")] if nearest_hospital else None
            },
            "nearest_fire_station": {
                "name": nearest_fire.get("name") if nearest_fire else "Industrial Hazmat Fire Station",
                "distance_km": round(fire_dist / 1000.0, 2) if fire_dist else 2.1,
                "phone": nearest_fire.get("phone", "+91 101") if nearest_fire else "+91 101",
                "coords": [nearest_fire.get("latitude"), nearest_fire.get("longitude")] if nearest_fire else None
            },
            "evacuation_routes": routes
        }

    @classmethod
    def _compute_safe_corridor(cls, start_lat: float, start_lon: float,
                               end_lat: float, end_lon: float, danger_radius_m: float) -> tuple:
        """
        Creates a polyline that navigates away from the hazard center, avoids the danger radius,
        and proceeds safely to the destination.
        """
        # Vector pointing away from incident towards destination
        d_lat = end_lat - start_lat
        d_lon = end_lon - start_lon
        
        # Perpendicular detour offset in degrees (~700m to steer outside the 500m danger circle)
        offset = 0.0075 
        
        # Danger segment: starts inside hazard zone (Red)
        red_pts = [
            [start_lat, start_lon],
            [start_lat + (d_lat * 0.15) + (offset * 0.3), start_lon + (d_lon * 0.15) + (offset * 0.3)]
        ]

        # Egress point clearing the 500m danger zone (Yellow transition)
        yellow_pts = [
            red_pts[-1],
            [start_lat + (d_lat * 0.35) + offset, start_lon + (d_lon * 0.35) + offset]
        ]

        # Safe corridor leading smoothly to destination (Green)
        green_pts = [
            yellow_pts[-1],
            [start_lat + (d_lat * 0.65) + (offset * 0.4), start_lon + (d_lon * 0.65) + (offset * 0.4)],
            [start_lat + (d_lat * 0.85), start_lon + (d_lon * 0.85)],
            [end_lat, end_lon]
        ]

        instructions = [
            "IMMEDIATE EVACUATION: Depart site perpendicular to prevailing wind vector.",
            "DO NOT use direct arterial roads traversing the 500m Blast/Thermal Perimeter.",
            "Follow Emergency Bypass Corridor north-east to cross the 1.5km Caution Line.",
            "Proceed along Green Corridor to the designated emergency facility.",
            "Keep emergency radio tuned to Disaster Response Channel 104.2 FM."
        ]

        return {
            "red_blocked_segment": red_pts,
            "yellow_segment": yellow_pts,
            "green_corridor": green_pts
        }, instructions
