"""
FIREGUARD AI - Emergency Services API (Requirement 4 & 11)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import EmergencyService
from backend.schemas.pydantic_models import EmergencyServiceResponse
from backend.services.osm_service import OSMService

router = APIRouter(prefix="/emergency-services", tags=["Emergency Services"])

@router.get("", response_model=List[EmergencyServiceResponse], summary="List emergency service facilities")
def list_emergency_services(
    service_type: Optional[str] = Query(None, description="hospital, fire_station, police, shelter, emergency_center", example="hospital"),
    db: Session = Depends(get_db)
):
    query = db.query(EmergencyService)
    if service_type:
        query = query.filter(EmergencyService.service_type == service_type)
    return [s.to_dict() for s in query.all()]

@router.get("/nearby", response_model=List[EmergencyServiceResponse], summary="Find emergency services near coordinates")
def get_nearby_emergency_services(
    latitude: float = Query(..., example=22.4707),
    longitude: float = Query(..., example=70.0577),
    radius_km: float = Query(30.0, example=30.0),
    service_type: Optional[str] = Query(None, example="fire_station"),
    db: Session = Depends(get_db)
):
    return OSMService.get_nearby_emergency_services(db, latitude, longitude, radius_km, service_type)

@router.get("/nearest", response_model=EmergencyServiceResponse, summary="Find nearest emergency service of specified type")
def get_nearest_service(
    latitude: float = Query(..., example=22.4707),
    longitude: float = Query(..., example=70.0577),
    service_type: str = Query("hospital", example="hospital"),
    db: Session = Depends(get_db)
):
    nearest = OSMService.get_nearest_emergency_service(db, latitude, longitude, service_type=service_type)
    if not nearest:
        raise HTTPException(
            status_code=404,
            detail={"code": "SERVICE_NOT_FOUND", "message": f"No {service_type} found within response radius"}
        )
    return nearest
