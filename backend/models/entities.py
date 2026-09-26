"""
FIREGUARD AI - SQLAlchemy Entity Models
SIH Problem Statement SIH26162
All 13 requirement tables with spatial columns, relationships, foreign keys & indexes.
"""
from datetime import datetime
import json
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    password_hash = Column(String(256), nullable=True, default="")
    role = Column(String(32), default="OPERATOR", index=True)  # ADMIN, OPERATOR, ANALYST, FACILITY_MANAGER, PUBLIC
    full_name = Column(String(128), nullable=False)
    agency = Column(String(128), default="Disaster Management Authority")
    phone = Column(String(32), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    audit_logs = relationship("AuditLog", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "agency": self.agency,
            "phone": self.phone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class IndustrialFacility(Base):
    __tablename__ = "facilities"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(256), nullable=False, index=True)
    facility_type = Column(String(64), nullable=False, index=True)  # Refinery, Chemical Plant, Petrochemical, Steel, Power Plant, Fertilizer
    industry_sector = Column(String(64), default="Oil & Gas")
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(String(512), default="")
    state = Column(String(64), default="Gujarat")
    district = Column(String(64), default="")
    hazmat_level = Column(String(32), default="LEVEL-3")  # LEVEL-1, LEVEL-2, LEVEL-3, LEVEL-4
    active_units = Column(Integer, default=12)
    flaring_authorized = Column(Boolean, default=True)
    normal_flaring_frp_mw = Column(Float, default=25.0)
    emergency_contact = Column(String(128), default="Safety Officer")
    emergency_phone = Column(String(32), default="+91 22 1234 5678")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hotspots = relationship("ThermalHotspot", back_populates="facility")
    incidents = relationship("Incident", back_populates="facility")
    persistent_sources = relationship("PersistentSource", back_populates="facility")

    __table_args__ = (
        Index("idx_facility_lat_lon", "latitude", "longitude"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "facility_type": self.facility_type,
            "industry_sector": self.industry_sector,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "state": self.state,
            "district": self.district,
            "hazmat_level": self.hazmat_level,
            "hazard_category": self.hazmat_level or "HAZMAT_TIER_1",
            "active_units": self.active_units,
            "flaring_authorized": self.flaring_authorized,
            "normal_flaring_frp_mw": self.normal_flaring_frp_mw,
            "emergency_contact": self.emergency_contact,
            "emergency_contact_name": self.emergency_contact,
            "emergency_phone": self.emergency_phone,
            "emergency_contact_phone": self.emergency_phone
        }


class ThermalHotspot(Base):
    __tablename__ = "hotspots"

    id = Column(String(64), primary_key=True, index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    brightness = Column(Float, default=320.0)
    scan = Column(Float, default=0.5)
    track = Column(Float, default=0.5)
    acq_date = Column(String(16), default="")
    acq_time = Column(String(8), default="")
    timestamp = Column(String(32), default="")
    satellite = Column(String(32), default="SNPP")
    instrument = Column(String(32), default="VIIRS")
    confidence = Column(Float, default=85.0)
    version = Column(String(16), default="2.0NRT")
    bright_t31 = Column(Float, default=295.0)
    frp = Column(Float, default=45.0)  # Fire Radiative Power (MW)
    daynight = Column(String(4), default="D")
    source = Column(String(64), default="NASA FIRMS")

    # Geospatial correlation & AI fields
    nearest_facility_id = Column(String(36), ForeignKey("facilities.id"), nullable=True)
    distance_to_facility_km = Column(Float, default=999.0)
    classification = Column(String(64), default="Unknown")
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String(16), default="LOW")
    status = Column(String(32), default="ACTIVE")  # ACTIVE, REVIEWED, RESOLVED, DISMISSED

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    facility = relationship("IndustrialFacility", back_populates="hotspots")
    incidents = relationship("Incident", back_populates="hotspot")

    __table_args__ = (
        Index("idx_hotspot_lat_lon", "latitude", "longitude"),
        Index("idx_hotspot_timestamp", "acq_date", "acq_time"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp or f"{self.acq_date} {self.acq_time}",
            "confidence": self.confidence,
            "brightness": self.brightness,
            "bright_t31": self.bright_t31,
            "frp": self.frp,
            "satellite": self.satellite,
            "instrument": self.instrument,
            "source": self.source,
            "classification": self.classification,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "distance_to_facility_km": self.distance_to_facility_km,
            "nearest_facility_id": self.nearest_facility_id,
            "status": self.status
        }


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, index=True)
    incident_number = Column(String(32), unique=True, index=True)
    hotspot_id = Column(String(64), ForeignKey("hotspots.id"), nullable=True)
    facility_id = Column(String(36), ForeignKey("facilities.id"), nullable=True)
    title = Column(String(256), nullable=False)
    status = Column(String(32), default="DETECTED", index=True)
    # DETECTED, UNDER_REVIEW, VERIFIED, ESCALATED, DISPATCH_REQUIRED, RESOLVED, FALSE_ALARM
    risk_level = Column(String(16), default="HIGH", index=True)  # CRITICAL, HIGH, MODERATE, LOW
    risk_score = Column(Float, default=75.0)
    classification = Column(String(64), default="Industrial Fire")
    confidence = Column(Float, default=0.85)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    operator_notes = Column(Text, default="")
    verified_by = Column(String(64), default="")
    dispatch_status = Column(String(32), default="PENDING")
    dispatch_details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    hotspot = relationship("ThermalHotspot", back_populates="incidents")
    facility = relationship("IndustrialFacility", back_populates="incidents")
    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan")
    ai_predictions = relationship("AIPrediction", back_populates="incident", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="incident", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="incident", cascade="all, delete-orphan")
    routes = relationship("Route", back_populates="incident", cascade="all, delete-orphan")

    def to_dict(self):
        latest_risk = self.risk_assessments[-1].to_dict() if self.risk_assessments else None
        fac_name = self.facility.name if self.facility else "Unassigned / Open Zone"
        return {
            "id": self.id,
            "incident_number": self.incident_number,
            "hotspot_id": self.hotspot_id,
            "facility_id": self.facility_id,
            "facility_name": fac_name,
            "title": self.title,
            "status": self.status,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "classification": self.classification,
            "fire_class": self.classification,
            "confidence": self.confidence,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "operator_notes": self.operator_notes,
            "verified_by": self.verified_by,
            "dispatch_status": self.dispatch_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "timeline": [e.to_dict() for e in self.events] if self.events else [],
            "hotspot": self.hotspot.to_dict() if self.hotspot else None,
            "facility": self.facility.to_dict() if self.facility else None,
            "risk_breakdown": {
                "risk_score": self.risk_score,
                "risk_level": self.risk_level,
                "factor_breakdown": latest_risk["factors"] if latest_risk else {
                    "facility_proximity_pts": round(self.risk_score * 0.32, 1),
                    "thermal_intensity_pts": round(self.risk_score * 0.28, 1),
                    "satellite_confidence_pts": round(self.risk_score * 0.16, 1),
                    "population_exposure_pts": round(self.risk_score * 0.12, 1),
                    "critical_infrastructure_pts": round(self.risk_score * 0.12, 1),
                },
                "why_explanation": latest_risk["explanation"] if latest_risk and latest_risk["explanation"] else f"High thermal signature detected within immediate operational proximity of {fac_name}. Radiative power exceeds emergency containment threshold."
            }
        }


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(String(36), primary_key=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    event_type = Column(String(64), nullable=False)  # CREATED, STATUS_CHANGED, NOTE_ADDED, DISPATCH_REQUESTED, VERIFIED, RESOLVED
    description = Column(Text, nullable=False)
    user_id = Column(String(36), nullable=True)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    incident = relationship("Incident", back_populates="events")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "event_type": self.event_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": json.loads(self.metadata_json) if self.metadata_json else {}
        }


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(String(36), primary_key=True, index=True)
    hotspot_id = Column(String(64), nullable=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=True)
    classification = Column(String(64), nullable=False)
    confidence = Column(Float, nullable=False)
    factors_json = Column(Text, default="[]")  # Explainable AI factors
    model_version = Column(String(32), default="FireGuard-XAI-v2.1")
    inference_time_ms = Column(Float, default=12.4)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="ai_predictions")

    def to_dict(self):
        factors = []
        if self.factors_json:
            try:
                factors = json.loads(self.factors_json)
            except Exception:
                factors = []
        return {
            "id": self.id,
            "hotspot_id": self.hotspot_id,
            "incident_id": self.incident_id,
            "classification": self.classification,
            "confidence": self.confidence,
            "factors": factors,
            "model_version": self.model_version,
            "inference_time_ms": self.inference_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String(36), primary_key=True, index=True)
    hotspot_id = Column(String(64), nullable=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=True)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(16), nullable=False)  # LOW, MODERATE, HIGH, CRITICAL
    factor_breakdown_json = Column(Text, default="{}")
    explanation = Column(Text, default="")
    formula_version = Column(String(32), default="MultiFactor-ISO31000-v2")
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="risk_assessments")

    def to_dict(self):
        breakdown = {}
        if self.factor_breakdown_json:
            try:
                breakdown = json.loads(self.factor_breakdown_json)
            except Exception:
                pass
        return {
            "id": self.id,
            "hotspot_id": self.hotspot_id,
            "incident_id": self.incident_id,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "factors": breakdown,
            "explanation": self.explanation,
            "formula_version": self.formula_version,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class PersistentSource(Base):
    __tablename__ = "persistent_sources"

    id = Column(String(36), primary_key=True, index=True)
    facility_id = Column(String(36), ForeignKey("facilities.id"), nullable=True)
    name = Column(String(256), nullable=False)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    detection_count = Column(Integer, default=15)
    detection_frequency = Column(Float, default=0.85)  # detections per day / window
    first_detected = Column(String(32), default="")
    latest_detected = Column(String(32), default="")
    avg_frp = Column(Float, default=35.0)
    avg_brightness = Column(Float, default=325.0)
    persistence_score = Column(Float, default=88.5)
    is_anomalous_spike = Column(Boolean, default=False)
    anomaly_z_score = Column(Float, default=0.0)
    status = Column(String(32), default="MONITORED")  # MONITORED, ANOMALOUS_SPIKE, MITIGATED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    facility = relationship("IndustrialFacility", back_populates="persistent_sources")

    def to_dict(self):
        return {
            "id": self.id,
            "facility_id": self.facility_id,
            "facility_name": self.facility.name if self.facility else "Industrial Zone",
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "detection_count": self.detection_count,
            "detection_frequency": self.detection_frequency,
            "first_detection": self.first_detected,
            "latest_detection": self.latest_detected,
            "avg_frp": self.avg_frp,
            "avg_brightness": self.avg_brightness,
            "average_intensity": self.avg_frp,
            "persistence_score": self.persistence_score,
            "is_anomalous_spike": self.is_anomalous_spike,
            "anomaly_z_score": self.anomaly_z_score,
            "status": self.status
        }


class EmergencyService(Base):
    __tablename__ = "emergency_services"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    service_type = Column(String(32), nullable=False, index=True)  # hospital, fire_station, police, shelter, emergency_center
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    address = Column(String(512), default="")
    phone = Column(String(32), default="+91 100")
    distance_km = Column(Float, default=5.0)
    capacity = Column(String(64), default="50 beds")
    operating_status = Column(String(32), default="24x7 Operational")
    source = Column(String(64), default="OpenStreetMap Overpass")
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "service_type": self.service_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "phone": self.phone,
            "distance_km": self.distance_km,
            "distance": self.distance_km,
            "capacity": self.capacity,
            "operating_status": self.operating_status,
            "source": self.source
        }


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(String(36), primary_key=True, index=True)
    category = Column(String(64), nullable=False, index=True)
    # Fire Department, Police, Ambulance, Disaster Management, Facility Emergency Manager, Personal Emergency Contact
    name = Column(String(128), nullable=False)
    agency = Column(String(128), default="")
    designation = Column(String(128), default="")
    phone = Column(String(32), nullable=False)
    email = Column(String(128), default="")
    state = Column(String(64), default="National")
    district = Column(String(64), default="")
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "name": self.name,
            "agency": self.agency,
            "designation": self.designation,
            "phone": self.phone,
            "email": self.email,
            "state": self.state,
            "district": self.district,
            "is_primary": self.is_primary
        }


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=True, index=True)
    severity = Column(String(16), nullable=False, index=True)  # INFO, WARNING, HIGH, CRITICAL
    alert_type = Column(String(64), nullable=False, index=True)
    # NEW_HOTSPOT, INDUSTRIAL_FIRE, PERSISTENT_SOURCE, HIGH_RISK, NEAR_POPULATION, NEAR_CRITICAL_INFRASTRUCTURE
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    channels_json = Column(Text, default='["DASHBOARD","SMS","EMAIL"]')
    read_status = Column(Boolean, default=False, index=True)
    acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    incident = relationship("Incident", back_populates="alerts")

    def to_dict(self):
        channels = []
        if self.channels_json:
            try:
                channels = json.loads(self.channels_json)
            except Exception:
                channels = []
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "severity": self.severity,
            "alert_type": self.alert_type,
            "title": self.title,
            "message": self.message,
            "channels": channels,
            "read_status": self.read_status,
            "acknowledged": self.acknowledged,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Route(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, index=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    name = Column(String(128), default="Primary Evacuation Corridor")
    route_type = Column(String(32), default="EVACUATION")  # EVACUATION, RESPONSE, CIVILLIAN_SAFE
    distance_km = Column(Float, default=12.4)
    estimated_time_minutes = Column(Integer, default=18)
    danger_radius_m = Column(Integer, default=500)
    is_safe = Column(Boolean, default=True)
    waypoints_json = Column(Text, default="[]")
    hazards_json = Column(Text, default="[]")
    avoided_zones_json = Column(Text, default="[]")
    destination_name = Column(String(256), default="Nearest District General Hospital")
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="routes")

    def to_dict(self):
        waypoints = []
        hazards = []
        avoided_zones = []
        try:
            if self.waypoints_json: waypoints = json.loads(self.waypoints_json)
            if self.hazards_json: hazards = json.loads(self.hazards_json)
            if self.avoided_zones_json: avoided_zones = json.loads(self.avoided_zones_json)
        except Exception:
            pass

        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "name": self.name,
            "route_type": self.route_type,
            "distance_km": self.distance_km,
            "distance": self.distance_km,
            "estimated_time_minutes": self.estimated_time_minutes,
            "estimated_time": self.estimated_time_minutes,
            "danger_radius_m": self.danger_radius_m,
            "is_safe": self.is_safe,
            "destination_name": self.destination_name,
            "recommended_route": {
                "name": self.name,
                "distance_km": self.distance_km,
                "eta_minutes": self.estimated_time_minutes,
                "waypoints": waypoints
            },
            "waypoints": waypoints,
            "hazards": hazards,
            "avoided_incident_zones": avoided_zones,
            "alternative_routes": [
                {
                    "name": "Secondary Bypass Route (via State Highway)",
                    "distance_km": round(self.distance_km * 1.25, 2),
                    "eta_minutes": int(self.estimated_time_minutes * 1.3),
                    "is_safe": True
                }
            ]
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(64), nullable=False)
    target_type = Column(String(64), nullable=False)
    target_id = Column(String(64), nullable=True)
    details_json = Column(Text, default="{}")
    ip_address = Column(String(64), default="127.0.0.1")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")

    def to_dict(self):
        details = {}
        if self.details_json:
            try:
                details = json.loads(self.details_json)
            except Exception:
                pass
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "details": details,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
