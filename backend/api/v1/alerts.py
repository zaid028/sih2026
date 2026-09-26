"""
FIREGUARD AI - Alerts API (Requirement 15)
"""
from typing import List
import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.models.entities import Alert
from backend.schemas.pydantic_models import AlertCreateRequest, AlertResponse
from backend.services.notification_service import NotificationService

router = APIRouter(prefix="/alerts", tags=["Tactical Alerts"])

@router.get("", response_model=List[AlertResponse], summary="List tactical alerts")
def list_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    return [a.to_dict() for a in alerts]

@router.post("", response_model=AlertResponse, status_code=201, summary="Generate tactical alert")
def create_alert(
    req: AlertCreateRequest,
    db: Session = Depends(get_db)
):
    channels = req.channels or ["DASHBOARD", "SMS", "EMAIL"]
    alert = Alert(
        id=str(uuid.uuid4()),
        incident_id=req.incident_id,
        severity=req.severity,
        alert_type=req.alert_type,
        title=req.title,
        message=req.message,
        channels_json=json.dumps(channels),
        read_status=False,
        acknowledged=False
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    # Dispatch notification
    NotificationService.dispatch_alert(alert.title, alert.message, channels)
    return alert.to_dict()

@router.patch("/{id}/read", response_model=AlertResponse, summary="Mark alert as read / acknowledged")
def mark_alert_read(
    id: str = Path(..., example="alert-01"),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(
            status_code=404,
            detail={"code": "ALERT_NOT_FOUND", "message": f"Alert '{id}' not found"}
        )
    alert.read_status = True
    alert.acknowledged = True
    db.commit()
    db.refresh(alert)
    return alert.to_dict()
