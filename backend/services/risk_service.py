"""
FIREGUARD AI - RiskAssessmentService (Requirement 8)
Computes 0-100 explainable multi-factor risk scores with configurable thresholds:
0–25 = LOW, 26–50 = MODERATE, 51–75 = HIGH, 76–100 = CRITICAL.
"""
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from backend.config.settings import settings
from backend.models.entities import ThermalHotspot, IndustrialFacility

class RiskAssessmentService:
    """Service computing multi-dimensional risk scores according to industrial disaster standards."""

    @staticmethod
    def calculate_risk(
        classification: str,
        confidence: float,
        frp: float = 35.0,
        brightness: float = 320.0,
        distance_to_facility_km: float = 5.0,
        hazmat_level: str = "LEVEL-2",
        recurrence_count: int = 1,
        population_exposure: int = 500
    ) -> Dict[str, Any]:
        """
        Calculates risk score (0-100) and produces factor breakdown and explanation.
        """
        # Factor 1: Thermal Intensity (FRP & Brightness) - 25%
        # FRP of 100+ MW yields 100 score
        raw_frp_score = min(100.0, (frp / 100.0) * 80.0 + max(0.0, (brightness - 310.0) * 0.5))
        frp_score = round(max(5.0, raw_frp_score), 1)

        # Factor 2: Industrial Proximity - 25%
        # Closer than 250m = 100, 1km = 75, > 5km = 10
        if distance_to_facility_km <= 0.25:
            prox_score = 98.0
        elif distance_to_facility_km <= 0.50:
            prox_score = 88.0
        elif distance_to_facility_km <= 1.0:
            prox_score = 75.0
        elif distance_to_facility_km <= 3.0:
            prox_score = 45.0
        else:
            prox_score = 15.0

        # Factor 3: FIRMS Confidence - 15%
        conf_score = round(confidence * 100.0 if confidence <= 1.0 else confidence, 1)

        # Factor 4: Population & Workforce Exposure - 15%
        pop_score = min(100.0, 30.0 + (population_exposure / 50.0))

        # Factor 5: Critical Infrastructure & Hazmat Level - 10%
        hazmat_weights = {"LEVEL-4": 95.0, "LEVEL-3": 80.0, "LEVEL-2": 60.0, "LEVEL-1": 40.0}
        infra_score = hazmat_weights.get(hazmat_level, 50.0)

        # Factor 6: Persistence & Recurrence Anomaly - 10%
        persist_score = min(95.0, 20.0 + recurrence_count * 5.0)

        # Classification multiplier
        multiplier = 1.0
        if classification == "Industrial Fire":
            multiplier = 1.25
        elif classification == "Gas Flare":
            multiplier = 0.65  # Controlled flare is lower risk
            prox_score *= 0.6
        elif classification == "Possible False Positive":
            multiplier = 0.20
        elif classification == "Waste Burning":
            multiplier = 0.50

        # Weighted aggregate
        composite = (
            (frp_score * 0.25) +
            (prox_score * 0.25) +
            (conf_score * 0.15) +
            (pop_score * 0.15) +
            (infra_score * 0.10) +
            (persist_score * 0.10)
        ) * multiplier

        final_score = round(min(100.0, max(0.0, composite)), 1)

        # Determine level based on configurable settings
        if final_score >= settings.RISK_THRESHOLD_CRITICAL_MIN:
            risk_level = "CRITICAL"
        elif final_score >= 51.0:
            risk_level = "HIGH"
        elif final_score >= 26.0:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"

        explanation = (
            f"Evaluated as {risk_level} risk ({final_score}/100) due to "
            f"FRP {frp:.1f} MW ({frp_score}/100), distance {distance_to_facility_km:.2f} km ({prox_score}/100) "
            f"under class '{classification}'."
        )

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "factors": {
                "thermal_intensity": {"score": frp_score, "weight": 0.25},
                "industrial_proximity": {"score": prox_score, "weight": 0.25},
                "satellite_confidence": {"score": conf_score, "weight": 0.15},
                "population_exposure": {"score": pop_score, "weight": 0.15},
                "infrastructure_vulnerability": {"score": infra_score, "weight": 0.10},
                "persistence_anomaly": {"score": persist_score, "weight": 0.10}
            },
            "explanation": explanation
        }

    @staticmethod
    def calculate_for_hotspot(db: Session, hotspot_id: str, classification: str, confidence: float) -> Dict[str, Any]:
        """Calculates risk for a specific database hotspot."""
        hs = db.query(ThermalHotspot).filter(ThermalHotspot.id == hotspot_id).first()
        dist = hs.distance_to_facility_km if hs else 5.0
        frp = hs.frp if hs else 35.0
        brightness = hs.brightness if hs else 320.0
        hazmat = "LEVEL-3"

        if hs and hs.nearest_facility_id:
            fac = db.query(IndustrialFacility).filter(IndustrialFacility.id == hs.nearest_facility_id).first()
            if fac:
                hazmat = fac.hazmat_level

        res = RiskAssessmentService.calculate_risk(
            classification=classification,
            confidence=confidence,
            frp=frp,
            brightness=brightness,
            distance_to_facility_km=dist,
            hazmat_level=hazmat
        )

        if hs:
            hs.risk_score = res["risk_score"]
            hs.risk_level = res["risk_level"]
            db.commit()

        return res
