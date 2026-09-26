"""
FIREGUARD AI - Roads API (Requirement 4)
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Query
from backend.services.osm_service import OSMService

router = APIRouter(prefix="/roads", tags=["Transportation Infrastructure (OSM)"])

@router.get("/nearby", summary="Get arterial roads and evacuation routes near coordinates")
def get_nearby_roads(
    latitude: float = Query(..., example=22.4707),
    longitude: float = Query(..., example=70.0577),
    radius_km: float = Query(5.0, example=5.0)
) -> List[Dict[str, Any]]:
    return OSMService.get_nearby_roads(latitude, longitude, radius_km)
