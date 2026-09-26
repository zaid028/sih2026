"""
FIREGUARD AI - Incidents API (Requirement 9 & 10)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.pydantic_models import (
    IncidentCreateRequest, IncidentUpdateRequest, IncidentResponse
)
from backend.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incident Management"])

@router.get("", response_model=List[IncidentResponse], summary="List incidents with triage filters")
def list_incidents(
    status: Optional[str] = Query(None, description="DETECTED, UNDER_REVIEW, VERIFIED, ESCALATED, DISPATCH_REQUIRED, RESOLVED, FALSE_ALARM"),
    risk_level: Optional[str] = Query(None, description="CRITICAL, HIGH, MODERATE, LOW"),
    facility_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return IncidentService.get_all(db, status=status, risk_level=risk_level, facility_id=facility_id)

@router.post("", response_model=IncidentResponse, status_code=201, summary="Create a new incident")
def create_incident(
    req: IncidentCreateRequest,
    db: Session = Depends(get_db)
):
    inc = IncidentService.create_incident(
        db,
        title=req.title,
        latitude=req.latitude,
        longitude=req.longitude,
        hotspot_id=req.hotspot_id,
        facility_id=req.facility_id,
        classification=req.classification or "Industrial Fire",
        confidence=req.confidence or 0.85,
        risk_score=req.risk_score or 80.0,
        risk_level=req.risk_level or "HIGH",
        operator_notes=req.operator_notes or ""
    )
    return inc.to_dict()

@router.get("/{id}", response_model=IncidentResponse, summary="Get incident dossier and timeline")
def get_incident(
    id: str = Path(..., example="inc-jamnagar-01"),
    db: Session = Depends(get_db)
):
    incident = IncidentService.get_by_id(db, id)
    if not incident:
        raise HTTPException(
            status_code=404,
            detail={"code": "INCIDENT_NOT_FOUND", "message": f"Incident '{id}' not found"}
        )
    return incident

@router.patch("/{id}", response_model=IncidentResponse, summary="Update incident status, notes, or verification")
def update_incident(
    req: IncidentUpdateRequest,
    id: str = Path(..., example="inc-jamnagar-01"),
    db: Session = Depends(get_db)
):
    updated = IncidentService.update_incident(
        db,
        incident_id=id,
        status=req.status,
        operator_notes=req.operator_notes,
        verified_by=req.verified_by,
        risk_level=req.risk_level,
        risk_score=req.risk_score,
        dispatch_status=req.dispatch_status
    )
    if not updated:
        raise HTTPException(
            status_code=404,
            detail={"code": "INCIDENT_NOT_FOUND", "message": f"Incident '{id}' not found"}
        )
    return updated

@router.delete("/{id}", summary="Delete an incident record")
def delete_incident(
    id: str = Path(..., example="inc-jamnagar-01"),
    db: Session = Depends(get_db)
):
    deleted = IncidentService.delete_incident(db, id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={"code": "INCIDENT_NOT_FOUND", "message": f"Incident '{id}' not found"}
        )
    return {"success": True, "message": f"Incident '{id}' deleted successfully"}
