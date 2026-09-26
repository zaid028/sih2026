"""
FIREGUARD AI - DemoService (Requirement 25)
Executes the full 12-step end-to-end simulation pipeline for live SIH demonstration.
"""
from datetime import datetime
import json
import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.models.entities import (
    ThermalHotspot, IndustrialFacility, Incident, IncidentEvent,
    AIPrediction, RiskAssessment, Alert, Route, PersistentSource
)
from backend.services.ai_service import AIClassificationService
from backend.services.risk_service import RiskAssessmentService
from backend.services.persistent_service import PersistentDetectorService
from backend.services.osm_service import OSMService
from backend.services.routing_service import RoutingService
from backend.services.notification_service import NotificationService

class DemoService:
    """Orchestrates 12-step complete end-to-end demonstration flow."""

    @staticmethod
    def run_sih_pipeline(db: Session, broadcast_callback=None) -> Dict[str, Any]:
        """
        Step 1: Generate/select thermal hotspot
        Step 2: Process hotspot
        Step 3: Match OSM facility
        Step 4: Run AI classification
        Step 5: Detect persistence
        Step 6: Calculate risk
        Step 7: Create incident
        Step 8: Find emergency services
        Step 9: Generate safety routes
        Step 10: Create alert
        Step 11: Send WebSocket updates
        Step 12: Return complete incident result
        """
        # Step 1: High-intensity thermal hotspot at Reliance Jamnagar Refinery Polypropylene Unit
        sim_lat = 22.4721
        sim_lon = 70.0592
        sim_frp = 96.5  # High MW
        sim_brightness = 384.2
        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        hotspot_id = f"demo-sih-{uuid.uuid4().hex[:8]}"

        # Step 2 & 3: Match OSM facility
        facility = db.query(IndustrialFacility).filter(
            IndustrialFacility.name.like("%Jamnagar%")
        ).first()

        if not facility:
            facility = db.query(IndustrialFacility).first()

        fac_id = facility.id if facility else None
        fac_name = facility.name if facility else "Reliance Jamnagar Complex"
        dist_km = 0.18

        hotspot = ThermalHotspot(
            id=hotspot_id,
            latitude=sim_lat,
            longitude=sim_lon,
            brightness=sim_brightness,
            scan=0.38,
            track=0.36,
            acq_date=datetime.utcnow().strftime("%Y-%m-%d"),
            acq_time=datetime.utcnow().strftime("%H%M"),
            timestamp=timestamp_str,
            satellite="SNPP",
            instrument="VIIRS",
            confidence=98.0,
            version="2.0NRT",
            bright_t31=306.4,
            frp=sim_frp,
            daynight="D",
            source="NASA FIRMS (Demonstration Ingestion)",
            nearest_facility_id=fac_id,
            distance_to_facility_km=dist_km,
            classification="Pending",
            risk_score=0.0,
            risk_level="CRITICAL",
            status="ACTIVE"
        )
        db.add(hotspot)

        # Step 4: Run AI Classification
        ai_res = AIClassificationService.classify({
            "frp": sim_frp,
            "brightness": sim_brightness,
            "distance_to_facility_km": dist_km,
            "facility_type": "Refinery",
            "recurrence_count": 18,
            "confidence": 98.0,
            "is_spike": True
        })
        hotspot.classification = ai_res["classification"]

        # Step 5: Detect Persistence & 2.5σ Anomaly
        persist_res = PersistentDetectorService.evaluate_persistence(db, sim_lat, sim_lon, sim_frp)

        # Step 6: Calculate Multi-factor Risk Score
        risk_res = RiskAssessmentService.calculate_risk(
            classification=ai_res["classification"],
            confidence=ai_res["confidence"],
            frp=sim_frp,
            brightness=sim_brightness,
            distance_to_facility_km=dist_km,
            hazmat_level=facility.hazmat_level if facility else "LEVEL-4",
            recurrence_count=persist_res["detection_count"],
            population_exposure=3800
        )
        hotspot.risk_score = risk_res["risk_score"]
        hotspot.risk_level = risk_res["risk_level"]

        # Step 7: Create Incident
        inc_id = str(uuid.uuid4())
        inc_num = f"SIH-DEMO-{datetime.utcnow().strftime('%H%M%S')}"
        incident = Incident(
            id=inc_id,
            incident_number=inc_num,
            hotspot_id=hotspot_id,
            facility_id=fac_id,
            title=f"CRITICAL FIRE EVENT: {fac_name} Olefins Processing Area",
            status="DETECTED",
            risk_level=risk_res["risk_level"],
            risk_score=risk_res["risk_score"],
            classification=ai_res["classification"],
            confidence=ai_res["confidence"],
            latitude=sim_lat,
            longitude=sim_lon,
            operator_notes="End-to-End automated SIH pipeline triggered. Awaiting tactical operator verification before dispatch.",
            dispatch_status="PENDING_OPERATOR_VERIFICATION",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(incident)

        # Add AI prediction record
        ai_record = AIPrediction(
            id=str(uuid.uuid4()),
            hotspot_id=hotspot_id,
            incident_id=inc_id,
            classification=ai_res["classification"],
            confidence=ai_res["confidence"],
            factors_json=json.dumps(ai_res["factors"]),
            model_version=ai_res["model_version"],
            inference_time_ms=8.4
        )
        db.add(ai_record)

        # Add Risk Assessment record
        risk_record = RiskAssessment(
            id=str(uuid.uuid4()),
            hotspot_id=hotspot_id,
            incident_id=inc_id,
            risk_score=risk_res["risk_score"],
            risk_level=risk_res["risk_level"],
            factor_breakdown_json=json.dumps(risk_res["factors"]),
            explanation=risk_res["explanation"]
        )
        db.add(risk_record)

        # Step 8: Find Emergency Services (Hospitals, Fire, Police)
        emergency_data = OSMService.analyze_location(db, sim_lat, sim_lon, radius_km=25.0)

        # Step 9: Generate Safety Routes
        # Route to nearest hospital
        nearest_hosp = emergency_data["nearby_hospitals"][0] if emergency_data["nearby_hospitals"] else None
        hosp_lat = nearest_hosp["latitude"] if nearest_hosp else 22.4680
        hosp_lon = nearest_hosp["longitude"] if nearest_hosp else 70.0750
        hosp_name = nearest_hosp.get("name", "Jamnagar Civil Hospital") if nearest_hosp else "Jamnagar Civil Hospital"

        routing_res = RoutingService.calculate_safe_route(
            origin_lat=sim_lat,
            origin_lon=sim_lon,
            dest_lat=hosp_lat,
            dest_lon=hosp_lon,
            incident_lat=sim_lat,
            incident_lon=sim_lon,
            danger_radius_m=1500
        )

        route_record = Route(
            id=str(uuid.uuid4()),
            incident_id=inc_id,
            name="Primary Emergency Evacuation Corridor (North Gate Bypass)",
            route_type="EVACUATION",
            distance_km=routing_res["distance"],
            estimated_time_minutes=routing_res["estimated_time"],
            danger_radius_m=500,
            is_safe=True,
            waypoints_json=json.dumps(routing_res["recommended_route"]["waypoints"]),
            hazards_json=json.dumps(routing_res["hazards"]),
            avoided_zones_json=json.dumps(routing_res["avoided_incident_zones"]),
            destination_name=hosp_name
        )
        db.add(route_record)

        # Step 10: Create Tactical Alert
        alert_id = str(uuid.uuid4())
        alert_record = Alert(
            id=alert_id,
            incident_id=inc_id,
            severity="CRITICAL",
            alert_type="INDUSTRIAL_FIRE",
            title=f"CRITICAL FIRE THREAT: {fac_name}",
            message=f"Satellite thermal detection ({sim_frp} MW FRP, {sim_brightness} K) classified as {ai_res['classification']} at {fac_name}. Risk Score: {risk_res['risk_score']}/100. Operator action required.",
            channels_json=json.dumps(["DASHBOARD", "SMS", "EMAIL", "PUSH"]),
            read_status=False,
            acknowledged=False
        )
        db.add(alert_record)

        # Dispatch simulated notification
        NotificationService.dispatch_alert(
            alert_title=alert_record.title,
            alert_message=alert_record.message,
            channels=["DASHBOARD", "SMS", "EMAIL"]
        )

        # Record timeline event
        event = IncidentEvent(
            id=str(uuid.uuid4()),
            incident_id=inc_id,
            event_type="DISPATCH_PREPARED",
            description="Emergency services identified and safe routing corridor generated. Tactical dispatch payload staged."
        )
        db.add(event)

        db.commit()

        # Step 11: WebSocket Broadcast
        event_payload = {
            "type": "NEW_CRITICAL_INCIDENT",
            "incident_id": inc_id,
            "incident_number": inc_num,
            "title": incident.title,
            "risk_score": incident.risk_score,
            "risk_level": incident.risk_level,
            "latitude": sim_lat,
            "longitude": sim_lon,
            "timestamp": timestamp_str
        }
        if broadcast_callback:
            try:
                broadcast_callback(event_payload)
            except Exception:
                pass

        # Step 12: Return complete incident result
        return {
            "status": "COMPLETE",
            "pipeline_step_count": 12,
            "incident": incident.to_dict(),
            "classification": ai_res,
            "risk": risk_res,
            "facility": facility.to_dict() if facility else {"name": fac_name},
            "persistent_source": persist_res,
            "emergency_services": {
                "hospitals": emergency_data["nearby_hospitals"],
                "fire_stations": emergency_data["nearby_fire_stations"],
                "police": emergency_data["nearby_police"]
            },
            "routes": routing_res,
            "alerts": alert_record.to_dict(),
            "websocket_broadcasted": True
        }
