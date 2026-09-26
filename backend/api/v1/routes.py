"""
FIREGUARD AI - Safe Routing API (Requirement 12)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import Incident
from backend.schemas.pydantic_models import RouteSafeRequest, RouteSafeResponse
from backend.services.routing_service import RoutingService

router = APIRouter(prefix="/routes", tags=["Safety Routing"])

@router.post("/safe", response_model=RouteSafeResponse, summary="Compute safe evacuation corridors avoiding danger perimeters")
def get_safe_route(
    req: RouteSafeRequest,
    db: Session = Depends(get_db)
):
    """
    Requirement 12:
    Computes recommended and alternative routes avoiding thermal radiation zones (500m)
    and perimeter buffer zones (1500m).
    """
    incident_lat = req.origin.latitude
    incident_lon = req.origin.longitude

    if req.incident_id:
        inc = db.query(Incident).filter(Incident.id == req.incident_id).first()
        if inc:
            incident_lat = inc.latitude
            incident_lon = inc.longitude

    return RoutingService.calculate_safe_route(
        origin_lat=req.origin.latitude,
        origin_lon=req.origin.longitude,
        dest_lat=req.destination.latitude,
        dest_lon=req.destination.longitude,
        incident_lat=incident_lat,
        incident_lon=incident_lon,
        danger_radius_m=req.avoid_radius_m or 1500
    )
