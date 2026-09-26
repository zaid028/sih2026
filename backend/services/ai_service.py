"""
FIREGUARD AI - AIClassificationService (Requirement 6)
Integrates AI classification engine into the application service layer.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.entities import ThermalHotspot, IndustrialFacility
from backend.ai.classifier import classifier_engine

class AIClassificationService:
    """Service wrapping AI classification and factor attribution."""

    @staticmethod
    def classify(features: Dict[str, Any]) -> Dict[str, Any]:
        """Classify given extracted features."""
        return classifier_engine.classify(features)

    @staticmethod
    def classify_hotspot(db: Session, hotspot_id: str) -> Dict[str, Any]:
        """Fetch hotspot from DB, extract context features, and classify."""
        hs = db.query(ThermalHotspot).filter(ThermalHotspot.id == hotspot_id).first()
        if not hs:
            return classifier_engine.classify({})

        fac_type = ""
        dist = hs.distance_to_facility_km
        if hs.nearest_facility_id:
            fac = db.query(IndustrialFacility).filter(IndustrialFacility.id == hs.nearest_facility_id).first()
            if fac:
                fac_type = fac.facility_type

        features = {
            "frp": hs.frp,
            "brightness": hs.brightness,
            "bright_t31": hs.bright_t31,
            "distance_to_facility_km": dist,
            "facility_type": fac_type,
            "recurrence_count": 12 if dist < 1.0 else 1,
            "confidence": hs.confidence
        }
        res = classifier_engine.classify(features)
        hs.classification = res["classification"]
        db.commit()
        return res
