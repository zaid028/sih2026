"""
FIREGUARD AI - FIRMSService (Requirement 2, 3 & 10)
Fetches, validates, normalizes, deduplicates, and ingests satellite observations into database.
Executes the full automated pipeline:
NASA FIRMS -> Validate/Normalize -> Facility Matching -> AI Classification -> Risk Calculation -> Auto-incident & Alert Creation.
"""
from datetime import datetime, timezone
import json
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.models.entities import (
    ThermalHotspot, IndustrialFacility, Incident, IncidentEvent,
    AIPrediction, RiskAssessment, Alert
)
from backend.integrations.firms_client import firms_client
from backend.utils.geo import haversine_distance_km
from backend.services.ai_service import AIClassificationService
from backend.services.risk_service import RiskAssessmentService

class FIRMSService:
    """Service handling NASA FIRMS thermal hotspot lifecycle & auto-incident pipeline."""

    @staticmethod
    def is_live_configured() -> bool:
        return firms_client.is_live_configured()

    @staticmethod
    def fetch_and_normalize(country: str = "IND", day_range: int = 1) -> List[Dict[str, Any]]:
        """Fetch normalized observation records."""
        return firms_client.fetch_observations(country=country, day_range=day_range)

    @staticmethod
    def ingest_observations(
        db: Session,
        records: Optional[List[Dict[str, Any]]] = None,
        broadcast_fn=None
    ) -> Dict[str, Any]:
        """
        Ingests observations into database.
        - Deduplicates by coordinates & acquisition timestamp
        - Correlates with nearest industrial facility
        - Runs AI classification & explainable factor attribution
        - Calculates ISO31000 risk score (0-100)
        - Auto-creates Incident and Alert if risk threshold exceeded (Requirement 10)
        - Never auto-claims emergency dispatch; requires operator verification
        """
        if records is None:
            records = FIRMSService.fetch_and_normalize()

        facilities = db.query(IndustrialFacility).all()
        ingested_count = 0
        updated_count = 0
        incidents_created = 0
        now_utc = datetime.now(timezone.utc)

        for r in records:
            lat = float(r["latitude"])
            lon = float(r["longitude"])
            acq_date = str(r.get("acq_date", now_utc.strftime("%Y-%m-%d")))
            acq_time = str(r.get("acq_time", "1200")).zfill(4)
            frp = float(r.get("frp", 35.0))
            brightness = float(r.get("brightness", 320.0))
            confidence = float(r.get("confidence", 80.0))

            # Find nearest facility
            nearest_fac = None
            min_dist = 9999.0
            for f in facilities:
                dist = haversine_distance_km(lat, lon, f.latitude, f.longitude)
                if dist < min_dist:
                    min_dist = dist
                    nearest_fac = f

            # Check existing observation
            hotspot_id = f"hs-{lat:.3f}-{lon:.3f}-{acq_date.replace('-', '')}-{acq_time}"
            existing = db.query(ThermalHotspot).filter(
                ThermalHotspot.id == hotspot_id
            ).first()

            if not existing:
                # Also check proximity duplicate within 200m on same day
                existing = db.query(ThermalHotspot).filter(
                    ThermalHotspot.acq_date == acq_date,
                    ThermalHotspot.latitude.between(lat - 0.002, lat + 0.002),
                    ThermalHotspot.longitude.between(lon - 0.002, lon + 0.002)
                ).first()

            target_hs = existing

            if existing:
                # Update existing record
                existing.brightness = brightness
                existing.frp = frp
                existing.confidence = confidence
                existing.updated_at = now_utc
                updated_count += 1
            else:
                new_hs = ThermalHotspot(
                    id=hotspot_id,
                    latitude=lat,
                    longitude=lon,
                    brightness=brightness,
                    scan=float(r.get("scan", 0.4)),
                    track=float(r.get("track", 0.4)),
                    acq_date=acq_date,
                    acq_time=acq_time,
                    timestamp=f"{acq_date} {acq_time[:2]}:{acq_time[2:]}:00 UTC",
                    satellite=str(r.get("satellite", "SNPP")),
                    instrument=str(r.get("instrument", "VIIRS")),
                    confidence=confidence,
                    version=str(r.get("version", "2.0NRT")),
                    bright_t31=float(r.get("bright_t31", 295.0)),
                    frp=frp,
                    daynight=str(r.get("daynight", "D")),
                    source=str(r.get("source", "NASA FIRMS")),
                    nearest_facility_id=nearest_fac.id if (nearest_fac and min_dist <= 50.0) else None,
                    distance_to_facility_km=round(min_dist, 3) if min_dist < 9999.0 else 999.0,
                    classification="Pending",
                    risk_score=0.0,
                    risk_level="LOW",
                    status="ACTIVE",
                    created_at=now_utc,
                    updated_at=now_utc
                )
                db.add(new_hs)
                target_hs = new_hs
                ingested_count += 1

            # Run AI classification for target hotspot
            fac_type = nearest_fac.facility_type if nearest_fac else ""
            hazmat = nearest_fac.hazmat_level if nearest_fac else "LEVEL-2"
            ai_res = AIClassificationService.classify({
                "frp": frp,
                "brightness": brightness,
                "distance_to_facility_km": min_dist,
                "facility_type": fac_type,
                "recurrence_count": 12 if min_dist < 1.0 else 1,
                "confidence": confidence,
                "is_spike": bool(frp >= 60.0 and min_dist <= 1.0)
            })

            target_hs.classification = ai_res["classification"]

            # Run Risk Assessment
            risk_res = RiskAssessmentService.calculate_risk(
                classification=ai_res["classification"],
                confidence=confidence,
                frp=frp,
                brightness=brightness,
                distance_to_facility_km=min_dist,
                hazmat_level=hazmat,
                recurrence_count=12 if min_dist < 1.0 else 1,
                population_exposure=3500 if min_dist < 1.0 else 400
            )

            target_hs.risk_score = risk_res["risk_score"]
            target_hs.risk_level = risk_res["risk_level"]

            # Requirement 10: Auto-create incident if risk threshold exceeded
            if target_hs.risk_score >= 70.0 or target_hs.risk_level in ("HIGH", "CRITICAL"):
                existing_inc = db.query(Incident).filter(
                    Incident.hotspot_id == target_hs.id
                ).first()

                if not existing_inc:
                    fac_name = nearest_fac.name if nearest_fac else "Monitored Industrial Corridor"
                    inc_id = str(uuid.uuid4())
                    inc_number = f"INC-AUTO-{now_utc.strftime('%m%d')}-{str(uuid.uuid4())[:4].upper()}"

                    incident = Incident(
                        id=inc_id,
                        incident_number=inc_number,
                        hotspot_id=target_hs.id,
                        facility_id=nearest_fac.id if nearest_fac else None,
                        title=f"{target_hs.risk_level} ALERT: {ai_res['classification']} at {fac_name}",
                        status="DETECTED",
                        risk_level=target_hs.risk_level,
                        risk_score=target_hs.risk_score,
                        classification=ai_res["classification"],
                        confidence=ai_res["confidence"],
                        latitude=lat,
                        longitude=lon,
                        operator_notes="Automatically registered via satellite ingestion. Requires operator verification prior to dispatch confirmation.",
                        verified_by="",
                        dispatch_status="PENDING_OPERATOR_VERIFICATION",
                        created_at=now_utc,
                        updated_at=now_utc
                    )
                    db.add(incident)

                    # Add event log
                    event = IncidentEvent(
                        id=str(uuid.uuid4()),
                        incident_id=inc_id,
                        event_type="AUTO_CREATED",
                        description=f"Satellite thermal detection exceeded risk threshold ({target_hs.risk_score}/100). Status: DETECTED.",
                        created_at=now_utc
                    )
                    db.add(event)

                    # Add Alert record
                    alert = Alert(
                        id=str(uuid.uuid4()),
                        incident_id=inc_id,
                        severity=target_hs.risk_level,
                        alert_type="INDUSTRIAL_FIRE" if "Industrial" in ai_res["classification"] else "HIGH_RISK",
                        title=f"AUTO SATELLITE ALERT: {ai_res['classification']} ({target_hs.risk_score}/100)",
                        message=f"Hotspot ({frp:.1f} MW FRP, {brightness:.1f} K) detected near {fac_name}. Awaiting operator review.",
                        channels_json=json.dumps(["DASHBOARD", "SMS"]),
                        read_status=False,
                        acknowledged=False,
                        created_at=now_utc
                    )
                    db.add(alert)
                    incidents_created += 1

                    if broadcast_fn:
                        try:
                            broadcast_fn({
                                "type": "NEW_SATELLITE_INCIDENT",
                                "incident_id": inc_id,
                                "incident_number": inc_number,
                                "title": incident.title,
                                "risk_score": target_hs.risk_score,
                                "risk_level": target_hs.risk_level,
                                "latitude": lat,
                                "longitude": lon
                            })
                        except Exception:
                            pass

        db.commit()
        source_name = "NASA FIRMS (Live)" if FIRMSService.is_live_configured() else "NASA FIRMS (Demo Feed)"
        return {
            "success": True,
            "ingested_count": ingested_count,
            "updated_count": updated_count,
            "incidents_created": incidents_created,
            "source": source_name,
            "total_processed": len(records)
        }
