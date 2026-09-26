"""
FIREGUARD AI - AI Classification API (Requirement 6)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.schemas.pydantic_models import AIClassifyRequest, AIClassifyResponse
from backend.services.ai_service import AIClassificationService

router = APIRouter(prefix="/ai", tags=["AI Classification"])

@router.post("/classify", response_model=AIClassifyResponse, summary="Classify thermal anomaly into 8 classes with XAI factors")
def classify_thermal_source(
    req: AIClassifyRequest,
    db: Session = Depends(get_db)
):
    """
    Requirement 6:
    8 Classes:
    - Industrial Fire
    - Forest/Vegetation Fire
    - Agricultural/Bush Fire
    - Gas Flare
    - Persistent Industrial Thermal Source
    - Waste Burning
    - Possible False Positive
    - Unknown
    Returns classification, confidence, and explainable AI factors.
    """
    if req.hotspot_id:
        return AIClassificationService.classify_hotspot(db, req.hotspot_id)

    features = req.features or {}
    return AIClassificationService.classify(features)
