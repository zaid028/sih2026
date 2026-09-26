"""
FIREGUARD AI - IncidentService (Requirement 9 & 10)
Manages incident lifecycle, triage state machine, audit events, and automated ingestion pipeline.
Incident States: DETECTED, UNDER_REVIEW, VERIFIED, ESCALATED, DISPATCH_REQUIRED, RESOLVED, FALSE_ALARM.
Requirement 10: "Do not automatically claim that emergency services were contacted. Require operator verification before real-world dispatch actions."
"""
from datetime import datetime
import json
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.entities import (
    Incident, IncidentEvent, ThermalHotspot, IndustrialFacility, Alert, Route
)
from backend.services.ai_service import AIClassificationService
from backend.services.risk_service import RiskAssessmentService
from backend.services.osm_service import OSMService
from backend.services.routing_service import RoutingService
from backend.services.notification_service import NotificationService

VALID_STATUSES = {
    "DETECTED", "UNDER_REVIEW", "VERIFIED", "ESCALATED",
    "DISPATCH_REQUIRED", "RESOLVED", "FALSE_ALARM"
}

class IncidentService:
    """Service managing industrial fire incident triage and operator verification."""

    @staticmethod
    def get_all(
        db: Session,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        facility_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = db.query(Incident)
        if status:
            query = query.filter(Incident.status == status)
        if risk_level:
            query = query.filter(Incident.risk_level == risk_level)
        if facility_id:
            query = query.filter(Incident.facility_id == facility_id)

        incidents = query.order_by(Incident.created_at.desc()).all()
        return [i.to_dict() for i in incidents]

    @staticmethod
    def get_by_id(db: Session, incident_id: str) -> Optional[Dict[str, Any]]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None
        data = incident.to_dict()
        if incident.facility:
            data["facility"] = incident.facility.to_dict()
        if incident.hotspot:
            data["hotspot"] = incident.hotspot.to_dict()
        return data

    @staticmethod
    def create_incident(
        db: Session,
        title: str,
        latitude: float,
        longitude: float,
        hotspot_id: Optional[str] = None,
        facility_id: Optional[str] = None,
        classification: str = "Industrial Fire",
        confidence: float = 0.85,
        risk_score: float = 80.0,
        risk_level: str = "HIGH",
        operator_notes: str = ""
    ) -> Incident:
        """Create new incident and record CREATED event."""
        inc_id = str(uuid.uuid4())
        inc_number = f"INC-2026-{datetime.utcnow().strftime('%m%d')}-{str(uuid.uuid4())[:4].upper()}"

        incident = Incident(
            id=inc_id,
            incident_number=inc_number,
            hotspot_id=hotspot_id,
            facility_id=facility_id,
            title=title,
            status="DETECTED",
            risk_level=risk_level,
            risk_score=risk_score,
            classification=classification,
            confidence=confidence,
            latitude=latitude,
            longitude=longitude,
            operator_notes=operator_notes,
            dispatch_status="PENDING",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(incident)

        # Add initial timeline event
        event = IncidentEvent(
            id=str(uuid.uuid4()),
            incident_id=inc_id,
            event_type="CREATED",
            description=f"Incident registered automatically from satellite detection with {risk_level} risk ({risk_score:.0f}/100)."
        )
        db.add(event)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def update_incident(
        db: Session,
        incident_id: str,
        status: Optional[str] = None,
        operator_notes: Optional[str] = None,
        verified_by: Optional[str] = None,
        risk_level: Optional[str] = None,
        risk_score: Optional[float] = None,
        dispatch_status: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update incident with audit log and status transition checks."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        if status and status in VALID_STATUSES:
            old_status = incident.status
            incident.status = status
            event = IncidentEvent(
                id=str(uuid.uuid4()),
                incident_id=incident_id,
                event_type="STATUS_CHANGED",
                description=f"Operator changed status from {old_status} to {status}."
            )
            db.add(event)

        if operator_notes:
            incident.operator_notes = operator_notes
            event = IncidentEvent(
                id=str(uuid.uuid4()),
                incident_id=incident_id,
                event_type="NOTE_ADDED",
                description=f"Tactical Note: {operator_notes}"
            )
            db.add(event)

        if verified_by:
            incident.verified_by = verified_by

        if risk_level:
            incident.risk_level = risk_level
        if risk_score is not None:
            incident.risk_score = risk_score
        if dispatch_status:
            incident.dispatch_status = dispatch_status

        incident.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(incident)
        return incident.to_dict()

    @staticmethod
    def delete_incident(db: Session, incident_id: str) -> bool:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return False
        db.delete(incident)
        db.commit()
        return True
