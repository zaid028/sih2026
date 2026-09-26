"""
FIREGUARD AI - Facilities API (Requirement 4)
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import IndustrialFacility
from backend.services.osm_service import OSMService

router = APIRouter(prefix="/facilities", tags=["Industrial Facilities (OSM)"])

@router.get("", summary="List all monitored industrial complexes")
def list_facilities(db: Session = Depends(get_db)):
    facilities = db.query(IndustrialFacility).all()
    return [f.to_dict() for f in facilities]

@router.get("/nearby", summary="Find industrial facilities near coordinates")
def get_nearby_facilities(
    latitude: float = Query(..., example=22.4707),
    longitude: float = Query(..., example=70.0577),
    radius_km: float = Query(25.0, example=25.0),
    db: Session = Depends(get_db)
):
    return OSMService.get_nearby_facilities(db, latitude, longitude, radius_km=radius_km)

@router.get("/{facility_id}", summary="Get detailed profile for an industrial facility")
def get_facility_detail(
    facility_id: str = Path(..., example="fac-jamnagar-01"),
    db: Session = Depends(get_db)
):
    facility = db.query(IndustrialFacility).filter(IndustrialFacility.id == facility_id).first()
    if not facility:
        raise HTTPException(
            status_code=404,
            detail={"code": "FACILITY_NOT_FOUND", "message": f"Facility '{facility_id}' not found"}
        )
    data = facility.to_dict()
    data["active_hotspots_count"] = len([h for h in facility.hotspots if h.status == "ACTIVE"])
    data["persistent_sources"] = [p.to_dict() for p in facility.persistent_sources]
    return data
