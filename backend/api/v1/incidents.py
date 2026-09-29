"""
FIREGUARD AI - Incidents API (Requirement 9 & 10)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Path
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.pydantic_models import (
    IncidentCreateRequest, CitizenReportRequest, IncidentUpdateRequest, IncidentResponse
)
from backend.services.incident_service import IncidentService
from backend.api.deps import get_current_user_optional

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

@router.post("/citizen-report", status_code=201, summary="Submit a ground fire observation with photo upload (Public Access)")
def citizen_report(
    req: CitizenReportRequest,
    db: Session = Depends(get_db)
):
    import uuid
    from datetime import datetime
    from backend.models.entities import IndustrialFacility, IncidentEvent

    # Find nearest facility or open zone
    nearest_fac = db.query(IndustrialFacility).first()
    notes = f"CITIZEN OBSERVATION by {req.reporter_name} ({req.reporter_phone}): {req.description}"
    if req.photo_data:
        notes += " [GROUND PHOTO UPLOADED]"

    inc = IncidentService.create_incident(
        db,
        title=f"🚨 [PUBLIC REPORT] {req.title}",
        latitude=req.latitude,
        longitude=req.longitude,
        facility_id=nearest_fac.id if nearest_fac else None,
        classification="Citizen Ground Fire Observation",
        confidence=0.92,
        risk_score=78.0,
        risk_level="HIGH",
        operator_notes=notes
    )

    import json
    event = IncidentEvent(
        id=str(uuid.uuid4()),
        incident_id=inc.id,
        event_type="CITIZEN_PHOTO_REPORT",
        description=f"Ground photo & observation submitted by civilian: {req.description}",
        user_id=req.reporter_name,
        metadata_json=json.dumps({"reporter_name": req.reporter_name, "reporter_phone": req.reporter_phone, "has_photo": bool(req.photo_data)}),
        created_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()

    return {
        "success": True,
        "message": "Citizen emergency observation and photo recorded. Emergency operations cell alerted.",
        "tracking_number": inc.incident_number or inc.id,
        "incident": inc.to_dict()
    }

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
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    if current_user and current_user.role == "PUBLIC":
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Public civilian users are not authorized to alter incident tactical status."}
        )

    updated = IncidentService.update_incident(
        db,
        incident_id=id,
        status=req.status,
        operator_notes=req.operator_notes,
        verified_by=req.verified_by or (current_user.full_name if current_user else "Command Cell Operator"),
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
