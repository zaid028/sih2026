"""
FIREGUARD AI - Emergency Alert & Multi-Agency Dispatch System
Manages real-time alert notifications and constructs standardized emergency dispatch payloads
for NDRF, State Disaster Management Authorities (SDMA), Fire Services, and Plant Safety Officers.
"""
from datetime import datetime
from typing import Dict, Any
import uuid

class AlertService:
    @classmethod
    def create_incident_alert_payload(cls, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a structured, standardized emergency alert message payload for multi-agency dispatch.
        """
        inc_id = incident.get("id", "INC-XXXX")
        fac_name = incident.get("facility_name", "Unregistered Industrial Asset")
        risk_tier = incident.get("risk_level", "HIGH")
        risk_score = incident.get("risk_score", 75.0)
        fire_class = incident.get("fire_class", "INDUSTRIAL_FIRE")
        detected_at = incident.get("detected_at", datetime.utcnow().isoformat())
        
        hotspot = incident.get("hotspot") or {}
        lat = hotspot.get("latitude", 0.0)
        lon = hotspot.get("longitude", 0.0)
        frp = hotspot.get("frp_mw", 0.0)
        sat = hotspot.get("source_satellite", "VIIRS")

        rec_response = incident.get("ai_classification", {}).get("recommended_response") if isinstance(incident.get("ai_classification"), dict) else (
            "Initiate immediate Tier-1 Hazmat response and deploy containment perimeter."
        )

        dispatch_text = (
            f"🚨 [FIREGUARD AI EMERGENCY ALERT] 🚨\n"
            f"INCIDENT ID: {inc_id}\n"
            f"SEVERITY: {risk_tier} (Score: {risk_score}/100)\n"
            f"FACILITY: {fac_name}\n"
            f"CLASSIFICATION: {fire_class.replace('_', ' ')}\n"
            f"COORDINATES: {lat:.5f}, {lon:.5f}\n"
            f"SATELLITE TELEMETRY: {sat} | FRP: {frp:.1f} MW\n"
            f"TIME OF DETECTION: {detected_at}\n"
            f"RECOMMENDED PROTOCOL: {rec_response}\n"
            f"ACTION REQUIRED: Immediate validation & responder mobilization."
        )

        return {
            "dispatch_id": f"DSP-{uuid.uuid4().hex[:8].upper()}",
            "incident_id": inc_id,
            "facility_name": fac_name,
            "coordinates": {"latitude": lat, "longitude": lon},
            "risk_tier": risk_tier,
            "risk_score": risk_score,
            "fire_class": fire_class,
            "satellite_telemetry": {
                "source": sat,
                "frp_mw": frp
            },
            "detection_timestamp": detected_at,
            "recommended_response": rec_response,
            "formatted_dispatch_message": dispatch_text,
            "simulated_broadcast_channels": [
                "National Disaster Response Force (NDRF) Tactical Ops Center",
                "State Disaster Management Authority (SDMA) Command Cell",
                "District Industrial Emergency Response Center",
                "Petrochemical Plant On-Site Incident Commander",
                "State Fire Services & Hazmat Unit #4"
            ]
        }
