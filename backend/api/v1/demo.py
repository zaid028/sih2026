"""
FIREGUARD AI - End-to-End Demo Simulation API (Requirement 25)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.pydantic_models import EndToEndDemoResponse
from backend.services.demo_service import DemoService
from backend.api.v1.websocket import broadcast_realtime_event

router = APIRouter(prefix="/demo", tags=["SIH Live Demonstration Flow"])

@router.post("/run", response_model=EndToEndDemoResponse, summary="Execute complete 12-step end-to-end simulation for SIH live evaluation")
def run_demo_pipeline(db: Session = Depends(get_db)):
    """
    SIH Judging Demonstration Endpoint:
    Triggers complete automated lifecycle:
    1. Thermal hotspot generation
    2. Hotspot normalization & processing
    3. OSM facility spatial correlation
    4. 8-Class AI classification with XAI factors
    5. Spatiotemporal recurrence & 2.5σ anomaly detection
    6. Multi-factor ISO31000 risk score calculation
    7. Incident triage creation & event log
    8. Nearest emergency services lookup
    9. Dynamic safety routing with danger perimeter avoidance
    10. Multi-agency tactical alert generation
    11. WebSocket real-time broadcast to connected command displays
    12. Return complete incident result payload
    """
    def broadcast_callback(payload):
        broadcast_realtime_event("DEMO_INCIDENT_CREATED", payload)

    return DemoService.run_sih_pipeline(db, broadcast_callback=broadcast_callback)
