"""
FIREGUARD AI - Risk Assessment API (Requirement 8)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.pydantic_models import RiskCalculateRequest, RiskCalculateResponse
from backend.services.risk_service import RiskAssessmentService

router = APIRouter(prefix="/risk", tags=["Risk Engine"])

@router.post("/calculate", response_model=RiskCalculateResponse, summary="Calculate explainable risk score (0-100)")
def calculate_risk(
    req: RiskCalculateRequest,
    db: Session = Depends(get_db)
):
    """
    Requirement 8:
    Multi-dimensional risk scoring:
    0–25 = LOW
    26–50 = MODERATE
    51–75 = HIGH
    76–100 = CRITICAL
    Returns composite score, level, factor weights, and plain-language explanation.
    """
    if req.hotspot_id:
        return RiskAssessmentService.calculate_for_hotspot(
            db, req.hotspot_id, req.classification, req.confidence
        )

    features = req.features or {}
    return RiskAssessmentService.calculate_risk(
        classification=req.classification,
        confidence=req.confidence,
        frp=float(features.get("frp", 35.0)),
        brightness=float(features.get("brightness", 320.0)),
        distance_to_facility_km=float(features.get("distance_to_facility_km", 5.0)),
        hazmat_level=str(features.get("hazmat_level", "LEVEL-2")),
        recurrence_count=int(features.get("recurrence_count", 1)),
        population_exposure=int(features.get("population_exposure", 500))
    )
