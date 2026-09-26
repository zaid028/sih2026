"""
FIREGUARD AI - Location Analysis & Correlation API (Requirement 5 & 13)
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.pydantic_models import (
    LocationAnalyzeRequest, LocationAnalyzeResponse
)
from backend.services.osm_service import OSMService

router = APIRouter(tags=["Geospatial Correlation"])

@router.post("/analyze/location", response_model=LocationAnalyzeResponse, summary="Analyze coordinates for facilities, emergency assets, and hazards")
def analyze_location(
    req: LocationAnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Requirement 5:
    Correlates latitude/longitude against:
    - Nearest industrial facility & distance
    - Nearby hospitals
    - Nearby fire stations
    - Nearby police
    - Nearby arterial roads
    - Population & workforce context
    """
    return OSMService.analyze_location(db, req.latitude, req.longitude, req.radius_km or 25.0)

@router.get("/location/nearby", summary="Get nearby assets for user or incident coordinates")
def get_location_nearby(
    latitude: float = Query(..., example=22.4707),
    longitude: float = Query(..., example=70.0577),
    radius_km: float = Query(15.0, example=15.0),
    db: Session = Depends(get_db)
):
    return OSMService.analyze_location(db, latitude, longitude, radius_km)

@router.post("/location/analyze", response_model=LocationAnalyzeResponse, summary="Alias for analyze/location")
def post_location_analyze(
    req: LocationAnalyzeRequest,
    db: Session = Depends(get_db)
):
    return OSMService.analyze_location(db, req.latitude, req.longitude, req.radius_km or 25.0)
