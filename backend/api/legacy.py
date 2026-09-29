"""
FIREGUARD AI - Legacy Frontend Compatibility Router
Mirrors /api/* endpoints so existing frontend UI functions seamlessly with the FastAPI backend.
"""
from datetime import datetime
import json
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.session import get_db
from backend.config.settings import settings
from backend.models.entities import (
    IndustrialFacility, ThermalHotspot, Incident, IncidentEvent, Alert, PersistentSource,
    EmergencyContact, Route
)
from backend.services.firms_service import FIRMSService
from backend.services.incident_service import IncidentService
from backend.services.routing_service import RoutingService
from backend.services.demo_service import DemoService
from backend.api.deps import get_current_user_optional

legacy_router = APIRouter(prefix="/api", tags=["Frontend Compatibility Layer"])

@legacy_router.get("/system/status")
def legacy_system_status(db: Session = Depends(get_db)):
    active_incidents = db.query(Incident).filter(Incident.status.notin_(["RESOLVED", "FALSE_ALARM"])).count()
    total_incidents = db.query(Incident).count()
    critical_threats = db.query(Incident).filter(Incident.risk_level == "CRITICAL").count()
    active_hotspots = db.query(ThermalHotspot).count()
    facilities_count = db.query(IndustrialFacility).count()

    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "demo_mode": settings.DEMO_MODE,
        "nasa_firms_connected": FIRMSService.is_live_configured(),
        "system_time_utc": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "active_incidents": active_incidents,
        "total_incidents": total_incidents,
        "critical_threats": critical_threats,
        "active_hotspots": active_hotspots,
        "monitored_facilities": facilities_count,
        "problem_statement": settings.PROBLEM_STATEMENT,
        "data_pipeline": [
            "NASA FIRMS MODIS & VIIRS Ingestion",
            "OSM Overpass Geospatial Buffering",
            "Spatiotemporal Recurrence Clustering",
            "8-Class AI Fire Classifier",
            "Multi-Factor ISO31000 Risk Scorer",
            "Dynamic Safe Routing Engine",
            "Multi-Agency Alert Dispatcher"
        ]
    }

@legacy_router.get("/hotspots")
def legacy_get_hotspots(
    source: Optional[str] = Query(None),
    min_confidence: Optional[float] = Query(None),
    classification: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    satellite: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ThermalHotspot)
    if min_confidence: query = query.filter(ThermalHotspot.confidence >= min_confidence)
    if risk_level: query = query.filter(ThermalHotspot.risk_level == risk_level.upper())
    if classification: query = query.filter(ThermalHotspot.classification == classification)
    if source: query = query.filter(ThermalHotspot.source.ilike(f"%{source}%"))
    if satellite: query = query.filter(ThermalHotspot.satellite.ilike(f"%{satellite}%"))
    hotspots = query.order_by(ThermalHotspot.created_at.desc()).all()
    return [h.to_dict() for h in hotspots]

@legacy_router.post("/hotspots/sync")
def legacy_sync_hotspots(db: Session = Depends(get_db), current_user = Depends(get_current_user_optional)):
    if current_user and current_user.role == "PUBLIC":
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Public civilian users are not authorized to trigger satellite sweeps."}
        )
    res = FIRMSService.ingest_observations(db)
    return {
        "success": True,
        "ingested_count": res["ingested_count"],
        "source": res["source"]
    }

@legacy_router.get("/incidents")
def legacy_get_incidents(
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return IncidentService.get_all(db, status=status, risk_level=risk_level)

@legacy_router.get("/incidents/{id}")
def legacy_get_incident(id: str = Path(...), db: Session = Depends(get_db)):
    inc = IncidentService.get_by_id(db, id)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return inc

@legacy_router.patch("/incidents/{id}/status")
def legacy_patch_status(
    id: str = Path(...),
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    role = (current_user.role if current_user else payload.get("role", "")).upper()
    if role == "PUBLIC":
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Public civilian users are not authorized to alter tactical incident status. Please contact emergency operations or submit a citizen photo observation."}
        )
    status_val = payload.get("status")
    notes = payload.get("notes", "")
    actor_name = current_user.full_name if current_user else payload.get("verified_by", "Command Cell Operator")
    updated = IncidentService.update_incident(db, id, status=status_val, operator_notes=notes, verified_by=actor_name)
    if not updated:
        raise HTTPException(status_code=404, detail="Incident not found")
    return updated

@legacy_router.post("/citizen-report")
def legacy_citizen_report(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    import uuid
    title = payload.get("title", "Ground Fire Observation")
    lat = float(payload.get("latitude", 22.4707))
    lon = float(payload.get("longitude", 70.0577))
    desc = payload.get("description", "Ground observation submitted by civilian.")
    photo = payload.get("photo_data")
    rep_name = payload.get("reporter_name", "Citizen Observer")
    rep_phone = payload.get("reporter_phone", "+91 99999 88888")

    nearest_fac = db.query(IndustrialFacility).first()
    notes = f"CITIZEN OBSERVATION by {rep_name} ({rep_phone}): {desc}"
    if photo:
        notes += " [GROUND PHOTO UPLOADED]"

    inc = IncidentService.create_incident(
        db,
        title=f"🚨 [PUBLIC REPORT] {title}",
        latitude=lat,
        longitude=lon,
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
        description=f"Ground photo & observation submitted by civilian: {desc}",
        user_id=rep_name,
        metadata_json=json.dumps({"reporter_name": rep_name, "reporter_phone": rep_phone, "has_photo": bool(photo)}),
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

@legacy_router.get("/facilities")
def legacy_get_facilities(db: Session = Depends(get_db)):
    facilities = db.query(IndustrialFacility).all()
    return [f.to_dict() for f in facilities]

@legacy_router.get("/facilities/{id}")
def legacy_get_facility(id: str = Path(...), db: Session = Depends(get_db)):
    fac = db.query(IndustrialFacility).filter(IndustrialFacility.id == id).first()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")
    data = fac.to_dict()
    data["persistent_sources"] = [p.to_dict() for p in fac.persistent_sources]
    return data

@legacy_router.get("/persistent-sources")
def legacy_get_persistent_sources(db: Session = Depends(get_db)):
    sources = db.query(PersistentSource).all()
    dicts = [s.to_dict() for s in sources]
    spikes = sum(1 for s in sources if s.is_anomalous_spike)
    return {
        "sources": dicts,
        "total": len(dicts),
        "abnormal_spikes_detected": spikes
    }

@legacy_router.get("/routes/{incident_id}")
def legacy_get_routes(incident_id: str = Path(...), db: Session = Depends(get_db)):
    routes = db.query(Route).filter(Route.incident_id == incident_id).all()
    if routes:
        return [r.to_dict() for r in routes]
    # Fallback compute
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    lat = inc.latitude if inc else 22.4707
    lon = inc.longitude if inc else 70.0577
    route_data = RoutingService.calculate_safe_route(lat, lon, lat + 0.05, lon + 0.05, lat, lon)
    return [route_data]

@legacy_router.get("/emergency/contacts")
def legacy_emergency_contacts(db: Session = Depends(get_db)):
    contacts = db.query(EmergencyContact).all()
    return {
        "contacts": [c.to_dict() for c in contacts],
        "total": len(contacts)
    }

@legacy_router.post("/emergency/dispatch-sim")
def legacy_dispatch_sim(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    role = (current_user.role if current_user else payload.get("role", "")).upper()
    if role in ["PUBLIC", "ANALYST"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": f"Role '{role}' is not authorized to trigger tactical multi-agency dispatches. Please use direct emergency calling (101/108/112)."}
        )
    inc_id = payload.get("incident_id")
    inc = db.query(Incident).filter(Incident.id == inc_id).first() if inc_id else None
    fac_name = inc.facility.name if (inc and inc.facility) else "Industrial Complex"
    disp_id = f"DISP-2026-{datetime.utcnow().strftime('%H%M%S')}"
    channels = [
        "District Fire & Emergency Services (101 Dispatch)",
        "Regional Hazmat Foam Operations Unit",
        "Civil Hospital Burn & Trauma Critical Care (108)",
        "Industrial Security Force (CISF Command Net)",
        "District Magistrate Disaster Control Cell"
    ]
    formatted_msg = (
        f"🚨 [FIREGUARD AI] IMMEDIATE MULTI-AGENCY DISPATCH DIRECTIVE\n"
        f"DISPATCH ID: {disp_id}\n"
        f"INCIDENT: {inc.title if inc else 'CRITICAL INDUSTRIAL FIRE'}\n"
        f"TARGET ASSET: {fac_name}\n"
        f"COORDINATES: {inc.latitude if inc else 22.4707:.5f}°N, {inc.longitude if inc else 70.0577:.5f}°E\n"
        f"SEVERITY: {inc.risk_level if inc else 'CRITICAL'} (Score: {inc.risk_score if inc else 88}/100)\n"
        f"PROTOCOL: Stage 500m thermal exclusion perimeter. Divert all non-emergency transit to Green Corridors.\n"
        f"BROADCAST CHANNELS: 5 Tactical Nodes Activated"
    )
    payload_obj = {
        "dispatch_id": disp_id,
        "incident_id": inc_id,
        "facility": fac_name,
        "status": "DISPATCH_PAYLOAD_STAGED",
        "formatted_dispatch_message": formatted_msg,
        "simulated_broadcast_channels": channels,
        "units_alerted": channels,
        "evacuation_corridors_opened": 2,
        "message": "Tactical multi-agency dispatch successfully staged and transmitted to field responder terminals."
    }
    return {
        "success": True,
        "payload": payload_obj,
        **payload_obj
    }

@legacy_router.get("/analytics/kpis")
def legacy_analytics_kpis(db: Session = Depends(get_db)):
    active_inc = db.query(Incident).filter(Incident.status.notin_(["RESOLVED", "FALSE_ALARM"])).count()
    total_hs = db.query(ThermalHotspot).count()
    critical_inc = db.query(Incident).filter(Incident.risk_level.in_(["CRITICAL", "HIGH"])).count()
    fac_count = db.query(IndustrialFacility).count()
    persistent_count = db.query(PersistentSource).count()
    industrial_fires = db.query(ThermalHotspot).filter(ThermalHotspot.classification.ilike("%industrial%")).count()
    if industrial_fires == 0:
        industrial_fires = db.query(Incident).filter(Incident.classification.ilike("%industrial%")).count() or active_inc
    return {
        "active_incidents": active_inc,
        "total_hotspots": total_hs,
        "critical_threats": critical_inc,
        "high_risk_incidents": critical_inc,
        "industrial_fires": industrial_fires,
        "persistent_sources": persistent_count,
        "monitored_facilities": fac_count,
        "avg_response_time_min": 14.2
    }

@legacy_router.get("/analytics/charts")
def legacy_analytics_charts(db: Session = Depends(get_db)):
    # 1. Classification distribution
    classes = db.query(ThermalHotspot.classification, func.count(ThermalHotspot.id)).group_by(ThermalHotspot.classification).all()
    class_labels = [c or "Unknown" for c, _ in classes] or ["Industrial Fire", "Gas Flare", "Persistent Source"]
    class_values = [v for _, v in classes] or [14, 8, 6]

    # 2. Risk distribution
    risks = db.query(Incident.risk_level, func.count(Incident.id)).group_by(Incident.risk_level).all()
    risk_dict = {r: c for r, c in risks}

    return {
        "classification": {
            "labels": class_labels,
            "data": class_values
        },
        "risk_tiers": {
            "labels": ["CRITICAL", "HIGH", "MODERATE", "LOW"],
            "data": [
                risk_dict.get("CRITICAL", 0),
                risk_dict.get("HIGH", 0),
                risk_dict.get("MODERATE", 0),
                risk_dict.get("LOW", 0)
            ]
        },
        "timeline": {
            "labels": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"],
            "data": [3, 5, 8, 14, 11, 7]
        }
    }

@legacy_router.get("/alerts")
def legacy_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).all()
    return [a.to_dict() for a in alerts]

@legacy_router.patch("/alerts/{id}/ack")
def legacy_ack_alert(id: str = Path(...), db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if alert:
        alert.acknowledged = True
        alert.read_status = True
        db.commit()
        return alert.to_dict()
    raise HTTPException(status_code=404, detail="Alert not found")

@legacy_router.get("/settings")
def legacy_get_settings():
    return {
        "demo_mode": settings.DEMO_MODE,
        "firms_map_key_set": bool(settings.effective_firms_key),
        "firms_map_key_masked": f"{settings.effective_firms_key[:4]}...{settings.effective_firms_key[-4:]}" if settings.effective_firms_key else "",
        "default_source": settings.FIRMS_DEFAULT_SOURCE,
        "default_country": settings.FIRMS_DEFAULT_COUNTRY,
        "overpass_endpoint": settings.effective_osm_url
    }

@legacy_router.post("/settings")
def legacy_save_settings(data: Dict[str, Any] = Body(...), current_user = Depends(get_current_user_optional)):
    role = (current_user.role if current_user else data.get("role", "")).upper()
    if role and role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Only NDMA Administrators are authorized to alter global system parameters and API keys."}
        )
    if "demo_mode" in data:
        settings.DEMO_MODE = bool(data["demo_mode"])
    if "firms_map_key" in data and data["firms_map_key"]:
        settings.FIRMS_MAP_KEY = data["firms_map_key"].strip()
    if "overpass_endpoint" in data and data["overpass_endpoint"]:
        settings.OVERPASS_ENDPOINT = data["overpass_endpoint"].strip()
    return {
        "success": True,
        "message": "Configuration updated successfully",
        "demo_mode": settings.DEMO_MODE,
        "firms_map_key_set": bool(settings.effective_firms_key),
        "overpass_endpoint": settings.effective_osm_url
    }

@legacy_router.post("/auth/demo-switch")
def legacy_auth_switch(payload: Dict[str, Any] = Body(...)):
    role = payload.get("role", "OPERATOR")
    token = f"demo_token_{role.lower()}_sih2026"
    return {
        "success": True,
        "role": role,
        "token": token,
        "user": {
            "username": f"demo_{role.lower()}",
            "role": role,
            "full_name": f"Tactical {role.replace('_', ' ').title()}"
        }
    }
