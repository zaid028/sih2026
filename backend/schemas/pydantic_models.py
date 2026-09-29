"""
FIREGUARD AI - Pydantic Request & Response Schemas
SIH Problem Statement SIH26162
Complies with FastAPI OpenAPI specs and all 27 user requirements.
"""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

try:
    import email_validator  # noqa: F401
    from pydantic import EmailStr
except ImportError:
    EmailStr = str  # Fallback to standard string if email-validator package is absent

# Standard Error Response (Requirement 22)
class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code", example="FIRMS_API_UNAVAILABLE")
    message: str = Field(..., description="Human-readable error description", example="NASA FIRMS data is temporarily unavailable.")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Optional diagnostic details")

class StandardErrorResponse(BaseModel):
    success: bool = Field(default=False)
    error: ErrorDetail

# Generic Success
class StandardSuccessResponse(BaseModel):
    success: bool = Field(default=True)
    message: str = Field(default="Operation completed successfully")
    data: Optional[Dict[str, Any]] = None

# 1. Hotspot Schemas (Requirement 2 & 3)
class HotspotResponse(BaseModel):
    id: str = Field(..., example="viirs-ind-20260926-001")
    latitude: float = Field(..., example=22.4707)
    longitude: float = Field(..., example=70.0577)
    timestamp: str = Field(..., example="2026-09-26 10:45:00 UTC")
    confidence: float = Field(..., example=94.0)
    brightness: float = Field(..., example=368.5)
    bright_t31: Optional[float] = Field(default=301.2)
    frp: Optional[float] = Field(default=68.4)
    satellite: str = Field(..., example="SNPP")
    instrument: Optional[str] = Field(default="VIIRS")
    source: str = Field(default="NASA FIRMS", example="NASA FIRMS")
    classification: Optional[str] = Field(default="Industrial Fire", example="Industrial Fire")
    risk_score: Optional[float] = Field(default=88.0, example=88.0)
    risk_level: Optional[str] = Field(default="CRITICAL", example="CRITICAL")
    distance_to_facility_km: Optional[float] = Field(default=0.25)
    nearest_facility_id: Optional[str] = None
    status: Optional[str] = Field(default="ACTIVE")

class HotspotIngestResponse(BaseModel):
    success: bool = True
    ingested_count: int
    source: str
    message: str
    sample_hotspots: Optional[List[HotspotResponse]] = None

# 2. Location & Analyze Schemas (Requirement 5 & 13)
class LocationCoordinates(BaseModel):
    latitude: float = Field(..., example=22.4707)
    longitude: float = Field(..., example=70.0577)

class LocationAnalyzeRequest(BaseModel):
    latitude: float = Field(..., example=22.4707)
    longitude: float = Field(..., example=70.0577)
    radius_km: Optional[float] = Field(default=25.0, example=25.0)

class FacilityContext(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = "Reliance Jamnagar Refinery"
    facility_type: Optional[str] = "Refinery"
    hazmat_level: Optional[str] = "LEVEL-4"
    state: Optional[str] = "Gujarat"
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class LocationAnalyzeResponse(BaseModel):
    nearest_facility: Optional[Dict[str, Any]] = None
    distance_to_facility: float = Field(..., description="Distance in kilometers", example=0.35)
    nearby_hospitals: List[Dict[str, Any]] = Field(default_factory=list)
    nearby_fire_stations: List[Dict[str, Any]] = Field(default_factory=list)
    nearby_police: List[Dict[str, Any]] = Field(default_factory=list)
    nearby_roads: List[Dict[str, Any]] = Field(default_factory=list)
    population_context: Dict[str, Any] = Field(default_factory=dict)

# 3. AI Classification Schemas (Requirement 6)
class AIClassifyRequest(BaseModel):
    hotspot_id: Optional[str] = Field(default=None, example="hs-jamnagar-01")
    features: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        example={
            "frp": 68.4,
            "brightness": 368.5,
            "distance_to_facility_km": 0.25,
            "facility_type": "Refinery",
            "recurrence_count": 18,
            "confidence": 94.0
        }
    )

class AIClassifyResponse(BaseModel):
    classification: str = Field(..., example="Industrial Fire")
    confidence: float = Field(..., example=0.87)
    factors: List[str] = Field(
        ...,
        example=[
            "Industrial facility within 350m buffer",
            "High thermal intensity (FRP: 68.4 MW)",
            "Thermal persistence anomaly exceeds 2.5σ baseline"
        ]
    )
    model_version: Optional[str] = Field(default="FireGuard-XAI-v2.1")
    inference_time_ms: Optional[float] = Field(default=8.5)

# 4. Risk Assessment Schemas (Requirement 8)
class RiskCalculateRequest(BaseModel):
    hotspot_id: Optional[str] = Field(default=None, example="hs-001")
    classification: str = Field(default="Industrial Fire", example="Industrial Fire")
    confidence: float = Field(default=0.87, example=0.87)
    features: Optional[Dict[str, Any]] = Field(default_factory=dict)

class RiskCalculateResponse(BaseModel):
    risk_score: float = Field(..., example=86.0)
    risk_level: str = Field(..., example="CRITICAL", description="LOW (0-25), MODERATE (26-50), HIGH (51-75), CRITICAL (76-100)")
    factors: Dict[str, Any] = Field(
        ...,
        example={
            "thermal_intensity": {"score": 92.0, "weight": 0.25},
            "industrial_proximity": {"score": 95.0, "weight": 0.25},
            "confidence_reliability": {"score": 94.0, "weight": 0.15},
            "population_hazard": {"score": 78.0, "weight": 0.15},
            "infrastructure_vulnerability": {"score": 85.0, "weight": 0.10},
            "persistence_anomaly": {"score": 60.0, "weight": 0.10}
        }
    )
    explanation: str = Field(
        ...,
        example="Critical risk due to high thermal intensity (68.4 MW) within 250m of LEVEL-4 Hazmat facility."
    )

# 5. Persistent Thermal Source Schemas (Requirement 7)
class PersistentSourceResponse(BaseModel):
    id: str
    facility_id: Optional[str] = None
    facility_name: Optional[str] = None
    name: str
    latitude: float
    longitude: float
    detection_count: int
    detection_frequency: float
    first_detection: Optional[str] = None
    latest_detection: Optional[str] = None
    avg_frp: Optional[float] = None
    average_intensity: Optional[float] = None
    persistence_score: float
    is_anomalous_spike: bool
    anomaly_z_score: Optional[float] = 0.0
    status: str
    nearby_facility: Optional[Dict[str, Any]] = None

# 6. Incident Management Schemas (Requirement 9 & 10)
class IncidentCreateRequest(BaseModel):
    title: str = Field(..., example="Thermal Anomaly Spike - Jamnagar Refinery North Tank Farm")
    hotspot_id: Optional[str] = None
    facility_id: Optional[str] = None
    latitude: float = Field(..., example=22.4707)
    longitude: float = Field(..., example=70.0577)
    risk_score: Optional[float] = Field(default=85.0)
    risk_level: Optional[str] = Field(default="CRITICAL")
    classification: Optional[str] = Field(default="Industrial Fire")
    confidence: Optional[float] = Field(default=0.88)
    operator_notes: Optional[str] = Field(default="Automated ingestion alert triggered")

class CitizenReportRequest(BaseModel):
    title: str = Field(..., example="Dense Black Smoke near Chemical Terminal")
    latitude: float = Field(..., example=22.4707)
    longitude: float = Field(..., example=70.0577)
    description: str = Field(..., example="High visible flame and acrid chemical odor observed from perimeter.")
    photo_data: Optional[str] = Field(default=None, description="Base64 encoded image or photo link")
    reporter_name: Optional[str] = Field(default="Concerned Citizen")
    reporter_phone: Optional[str] = Field(default="+91 99999 88888")

class IncidentUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, example="VERIFIED", description="DETECTED, UNDER_REVIEW, VERIFIED, ESCALATED, DISPATCH_REQUIRED, RESOLVED, FALSE_ALARM")
    operator_notes: Optional[str] = Field(None, example="Verified via on-site thermal sensor.")
    verified_by: Optional[str] = Field(None, example="Commander Sharma")
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    dispatch_status: Optional[str] = None

class IncidentResponse(BaseModel):
    id: str
    incident_number: Optional[str] = None
    hotspot_id: Optional[str] = None
    facility_id: Optional[str] = None
    facility_name: Optional[str] = None
    title: str
    status: str
    risk_level: str
    risk_score: float
    classification: str
    confidence: float
    latitude: float
    longitude: float
    operator_notes: Optional[str] = ""
    verified_by: Optional[str] = ""
    dispatch_status: Optional[str] = "PENDING"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    timeline: Optional[List[Dict[str, Any]]] = None

# 7. Emergency Services Schemas (Requirement 11)
class EmergencyServiceResponse(BaseModel):
    id: str
    name: str
    service_type: str = Field(..., example="hospital", description="hospital, fire_station, police, shelter, emergency_center")
    latitude: float
    longitude: float
    address: Optional[str] = None
    phone: Optional[str] = None
    distance_km: Optional[float] = None
    distance: Optional[float] = None
    capacity: Optional[str] = None
    operating_status: Optional[str] = None
    source: Optional[str] = "OpenStreetMap"

# 8. Safe Routing Schemas (Requirement 12)
class RouteSafeRequest(BaseModel):
    origin: LocationCoordinates
    destination: LocationCoordinates
    incident_id: Optional[str] = None
    avoid_radius_m: Optional[int] = Field(default=1500)

class RouteSafeResponse(BaseModel):
    recommended_route: Dict[str, Any]
    alternative_routes: List[Dict[str, Any]] = Field(default_factory=list)
    distance: float = Field(..., description="Distance in kilometers", example=12.4)
    estimated_time: int = Field(..., description="Estimated time in minutes", example=18)
    hazards: List[Dict[str, Any]] = Field(default_factory=list)
    avoided_incident_zones: List[Dict[str, Any]] = Field(default_factory=list)
    disclaimer: str = "Route recommendations are dynamically computed based on thermal hazard zones. Always obey local emergency management instructions."

# 9. Emergency Contacts Schemas (Requirement 14)
class EmergencyContactCreateRequest(BaseModel):
    category: str = Field(..., example="Fire Department", description="Fire Department, Police, Ambulance, Disaster Management, Facility Emergency Manager, Personal Emergency Contact")
    name: str = Field(..., example="District Chief Fire Officer")
    agency: Optional[str] = Field(default="Gujarat Fire & Emergency Services")
    designation: Optional[str] = Field(default="Chief Fire Officer")
    phone: str = Field(..., example="+91 288 255 0101")
    email: Optional[str] = Field(default="cfo.jamnagar@gujarat.gov.in")
    state: Optional[str] = Field(default="Gujarat")
    district: Optional[str] = Field(default="Jamnagar")
    is_primary: Optional[bool] = Field(default=True)

class EmergencyContactResponse(BaseModel):
    id: str
    category: str
    name: str
    agency: Optional[str] = None
    designation: Optional[str] = None
    phone: str
    email: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    is_primary: bool

# 10. Alerts Schemas (Requirement 15)
class AlertCreateRequest(BaseModel):
    incident_id: Optional[str] = None
    severity: str = Field(..., example="CRITICAL", description="INFO, WARNING, HIGH, CRITICAL")
    alert_type: str = Field(..., example="INDUSTRIAL_FIRE", description="NEW_HOTSPOT, INDUSTRIAL_FIRE, PERSISTENT_SOURCE, HIGH_RISK, NEAR_POPULATION, NEAR_CRITICAL_INFRASTRUCTURE")
    title: str = Field(..., example="CRITICAL FIRE ALERT: Refinery Flare Over-temperature")
    message: str = Field(..., example="Satellite detected 68.4 MW thermal hotspot within Jamnagar Refinery perimeter.")
    channels: Optional[List[str]] = Field(default=["DASHBOARD", "SMS", "EMAIL"])

class AlertResponse(BaseModel):
    id: str
    incident_id: Optional[str] = None
    severity: str
    alert_type: str
    title: str
    message: str
    channels: List[str]
    read_status: bool
    acknowledged: bool
    created_at: Optional[str] = None

# 11. Auth Schemas (Requirement 19)
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, example="commander_rao")
    email: EmailStr = Field(..., example="rao@disaster.gov.in")
    password: str = Field(..., min_length=6, example="FireGuard#2026")
    full_name: str = Field(..., example="Dr. K. S. Rao")
    agency: Optional[str] = Field(default="National Disaster Management Authority")
    role: Optional[str] = Field(default="OPERATOR", description="ADMIN, OPERATOR, ANALYST, FACILITY_MANAGER, PUBLIC")
    phone: Optional[str] = Field(default="+91 98765 43210")

class UserLoginRequest(BaseModel):
    username: str = Field(..., example="operator")
    password: str = Field(..., example="operator123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    user_id: str
    expires_in: int = 86400

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    full_name: str
    agency: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool

# 12. Health Monitor Schema (Requirement 26)
class HealthStatusResponse(BaseModel):
    status: str = Field(default="OPERATIONAL", example="OPERATIONAL")
    demo_mode: bool = False
    timestamp: str
    components: Dict[str, str] = Field(
        ...,
        example={
            "backend": "ONLINE",
            "database": "ONLINE",
            "nasa_firms": "ONLINE",
            "osm": "ONLINE",
            "ai_engine": "ONLINE",
            "routing": "ONLINE",
            "notification_service": "ONLINE"
        }
    )
    version: str = "2.0.0"
    active_incidents: int = 9
    active_hotspots: int = 37

# 13. End-to-End Demo Flow Schema (Requirement 25)
class EndToEndDemoResponse(BaseModel):
    status: str = "COMPLETE"
    pipeline_step_count: int = 12
    incident: Dict[str, Any]
    classification: Dict[str, Any]
    risk: Dict[str, Any]
    facility: Dict[str, Any]
    persistent_source: Dict[str, Any]
    emergency_services: Dict[str, Any]
    routes: Dict[str, Any]
    alerts: Dict[str, Any]
    websocket_broadcasted: bool = True
