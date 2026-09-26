"""
FIREGUARD AI - SQLAlchemy Data Models
Models for Industrial Facilities, Thermal Hotspots, Incidents, AI Classifications,
Risk Scores, Emergency Infrastructure, Routing, and Audit Logs.
"""
from datetime import datetime
import json
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=True, default="")
    hashed_password = Column(String(256), nullable=True, default="")
    full_name = Column(String(120), nullable=False)
    role = Column(String(32), default="analyst")  # admin, operator, facility_manager, analyst, public
    organization = Column(String(120), default="Government / Disaster Management Authority")
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
            "full_name": self.full_name,
            "role": self.role,
            "organization": self.organization,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class IndustrialFacility(Base):
    __tablename__ = "industrial_facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, index=True)
    facility_type = Column(String(64), nullable=False)  # refinery, chemical_plant, power_plant, steel_mill, warehouse, flaring_stack
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    hazard_category = Column(String(32), default="HAZMAT_TIER_1")  # HAZMAT_TIER_1, TIER_2, STANDARD_INDUSTRIAL
    address = Column(String(255))
    district = Column(String(80), index=True)
    state = Column(String(80), index=True)
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(50))
    polygon_coords = Column(Text, default="[]")  # JSON string of polygon boundary coordinates
    created_at = Column(DateTime, default=datetime.utcnow)

    hotspots = relationship("ThermalHotspot", back_populates="facility")
    incidents = relationship("Incident", back_populates="facility")

    def to_dict(self):
        coords = []
        try:
            coords = json.loads(self.polygon_coords) if self.polygon_coords else []
        except Exception:
            coords = []
        return {
            "id": self.id,
            "name": self.name,
            "facility_type": self.facility_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hazard_category": self.hazard_category,
            "address": self.address,
            "district": self.district,
            "state": self.state,
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "polygon_coords": coords,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ThermalHotspot(Base):
    __tablename__ = "thermal_hotspots"

    id = Column(Integer, primary_key=True, index=True)
    source_satellite = Column(String(32), default="VIIRS_SNPP")  # MODIS_Terra, MODIS_Aqua, VIIRS_SNPP, VIIRS_NOAA20
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    brightness_k = Column(Float, nullable=False)  # Kelvin (e.g. 340.5 K)
    frp_mw = Column(Float, nullable=False)        # Fire Radiative Power (MW)
    confidence = Column(Integer, default=80)      # 0 - 100 percentage
    acquisition_date = Column(String(10), index=True)  # YYYY-MM-DD
    acquisition_time = Column(String(10))         # HHMM (UTC)
    daynight = Column(String(1), default="D")     # 'D' or 'N'
    facility_id = Column(Integer, ForeignKey("industrial_facilities.id"), nullable=True)
    distance_to_facility_m = Column(Float, nullable=True)
    is_persistent = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)

    facility = relationship("IndustrialFacility", back_populates="hotspots")
    incident = relationship("Incident", back_populates="hotspot", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "source_satellite": self.source_satellite,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "brightness_k": round(self.brightness_k, 2),
            "frp_mw": round(self.frp_mw, 2),
            "confidence": self.confidence,
            "acquisition_date": self.acquisition_date,
            "acquisition_time": self.acquisition_time,
            "daynight": self.daynight,
            "facility_id": self.facility_id,
            "facility_name": self.facility.name if self.facility else None,
            "distance_to_facility_m": round(self.distance_to_facility_m, 1) if self.distance_to_facility_m else None,
            "is_persistent": self.is_persistent,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None
        }

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(32), primary_key=True, index=True)  # INC-2026-XXXX
    hotspot_id = Column(Integer, ForeignKey("thermal_hotspots.id"), nullable=True)
    facility_id = Column(Integer, ForeignKey("industrial_facilities.id"), nullable=True)
    title = Column(String(180), nullable=False)
    fire_class = Column(String(40), default="UNKNOWN")  # INDUSTRIAL_FIRE, PERSISTENT_IND, GAS_FLARE, FOREST_FIRE, etc.
    risk_score = Column(Float, default=50.0)             # 0 - 100
    risk_level = Column(String(20), default="MODERATE") # LOW, MODERATE, HIGH, CRITICAL
    status = Column(String(30), default="REPORTED")     # REPORTED, VERIFIED, DISPATCH_REQUIRED, IN_PROGRESS, RESOLVED, FALSE_ALARM
    reported_by = Column(String(64), default="AI_FIRMS_DETECTOR")
    response_notes = Column(Text, default="")
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    hotspot = relationship("ThermalHotspot", back_populates="incident")
    facility = relationship("IndustrialFacility", back_populates="incidents")
    ai_classification = relationship("AIClassification", back_populates="incident", uselist=False)
    risk_score_rel = relationship("RiskScore", back_populates="incident", uselist=False)
    alerts = relationship("Alert", back_populates="incident")
    routes = relationship("Route", back_populates="incident")

    def to_dict(self):
        return {
            "id": self.id,
            "hotspot_id": self.hotspot_id,
            "facility_id": self.facility_id,
            "facility_name": self.facility.name if self.facility else "Unmapped Facility / Open Area",
            "title": self.title,
            "fire_class": self.fire_class,
            "risk_score": round(self.risk_score, 1),
            "risk_level": self.risk_level,
            "status": self.status,
            "reported_by": self.reported_by,
            "response_notes": self.response_notes,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "hotspot": self.hotspot.to_dict() if self.hotspot else None,
            "facility": self.facility.to_dict() if self.facility else None,
            "ai_classification": self.ai_classification.to_dict() if self.ai_classification else None,
            "risk_breakdown": self.risk_score_rel.to_dict() if self.risk_score_rel else None
        }

class AIClassification(Base):
    __tablename__ = "ai_classifications"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(32), ForeignKey("incidents.id"), nullable=False)
    primary_class = Column(String(40), nullable=False)
    confidence_pct = Column(Float, nullable=False)
    top_factors = Column(Text, default="[]")  # JSON array of strings
    explanation_text = Column(Text, default="")
    recommended_response = Column(Text, default="")
    evaluated_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="ai_classification")

    def to_dict(self):
        factors = []
        try:
            factors = json.loads(self.top_factors) if self.top_factors else []
        except Exception:
            factors = []
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "primary_class": self.primary_class,
            "confidence_pct": round(self.confidence_pct, 1),
            "top_factors": factors,
            "explanation_text": self.explanation_text,
            "recommended_response": self.recommended_response,
            "evaluated_at": self.evaluated_at.isoformat() if self.evaluated_at else None
        }

class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(32), ForeignKey("incidents.id"), nullable=False)
    total_score = Column(Float, nullable=False)
    risk_tier = Column(String(20), nullable=False)  # LOW, MODERATE, HIGH, CRITICAL
    factor_breakdown = Column(Text, default="{}")  # JSON dict of score contributions
    why_explanation = Column(Text, default="")
    calculated_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="risk_score_rel")

    def to_dict(self):
        breakdown = {}
        try:
            breakdown = json.loads(self.factor_breakdown) if self.factor_breakdown else {}
        except Exception:
            breakdown = {}
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "total_score": round(self.total_score, 1),
            "risk_tier": self.risk_tier,
            "factor_breakdown": breakdown,
            "why_explanation": self.why_explanation,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None
        }

class EmergencyFacility(Base):
    __tablename__ = "emergency_facilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    facility_type = Column(String(40), nullable=False)  # hospital, fire_station, police_station, shelter
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String(50))
    address = Column(String(255))
    bed_capacity = Column(Integer, default=0)

    routes = relationship("Route", back_populates="target_facility")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "facility_type": self.facility_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "phone": self.phone,
            "address": self.address,
            "bed_capacity": self.bed_capacity
        }

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    agency_name = Column(String(120), nullable=False)
    contact_type = Column(String(50), nullable=False)  # NDRF, FIRE_DEPARTMENT, POLICE, AMBULANCE, FACILITY_MGR, SDMA
    phone = Column(String(50), nullable=False)
    email = Column(String(100))
    district = Column(String(80))
    state = Column(String(80))
    is_primary = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "agency_name": self.agency_name,
            "contact_type": self.contact_type,
            "phone": self.phone,
            "email": self.email,
            "district": self.district,
            "state": self.state,
            "is_primary": self.is_primary
        }

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, index=True)  # UUID or ALT-XXXX
    incident_id = Column(String(32), ForeignKey("incidents.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)  # INDUSTRIAL_FIRE, CRITICAL_HOTSPOT, PERSISTENT_SOURCE, SPIKE
    severity = Column(String(20), default="HIGH")    # CRITICAL, HIGH, MODERATE, INFO
    message = Column(Text, nullable=False)
    is_acknowledged = Column(Boolean, default=False)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)

    incident = relationship("Incident", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "is_acknowledged": self.is_acknowledged,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None
        }

class Route(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, index=True)
    incident_id = Column(String(32), ForeignKey("incidents.id"), nullable=False)
    target_facility_id = Column(Integer, ForeignKey("emergency_facilities.id"), nullable=False)
    route_type = Column(String(30), default="SAFE_EVACUATION")  # SAFE_EVACUATION, CAUTION_PERIMETER, DANGER_ZONE
    distance_km = Column(Float, nullable=False)
    estimated_time_min = Column(Integer, nullable=False)
    waypoints_json = Column(Text, default="[]")  # GeoJSON LineString coordinates
    avoids_hazard_zone = Column(Boolean, default=True)

    incident = relationship("Incident", back_populates="routes")
    target_facility = relationship("EmergencyFacility", back_populates="routes")

    def to_dict(self):
        pts = []
        try:
            pts = json.loads(self.waypoints_json) if self.waypoints_json else []
        except Exception:
            pts = []
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "target_facility_id": self.target_facility_id,
            "target_facility": self.target_facility.to_dict() if self.target_facility else None,
            "route_type": self.route_type,
            "distance_km": round(self.distance_km, 2),
            "estimated_time_min": self.estimated_time_min,
            "waypoints": pts,
            "avoids_hazard_zone": self.avoids_hazard_zone
        }

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(64), nullable=False)
    target_type = Column(String(40))
    target_id = Column(String(64))
    details = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else "SYSTEM",
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
