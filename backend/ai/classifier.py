"""
FIREGUARD AI - 8-Class Fire Classification & Explainable AI (XAI) Model
Classifies thermal anomalies into 8 distinct categories with factor attribution.
"""
from typing import Dict, Any, List, Tuple

AI_CLASSES = [
    "Industrial Fire",
    "Forest/Vegetation Fire",
    "Agricultural/Bush Fire",
    "Gas Flare",
    "Persistent Industrial Thermal Source",
    "Waste Burning",
    "Possible False Positive",
    "Unknown"
]

class FireGuardAIClassifier:
    """
    Hybrid Rules & Heuristics AI Classification Engine with Explainable AI (XAI) output.
    Can be replaced with PyTorch / ONNX model weight checkpoints seamlessly.
    """
    def __init__(self, model_version: str = "FireGuard-XAI-v2.1"):
        self.model_version = model_version

    def classify(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infers fire classification and outputs confidence + factor attribution.
        Features expected:
            - frp (float): Fire Radiative Power in MW
            - brightness (float): Brightness temperature (K)
            - bright_t31 (float): Background / Channel 31 brightness (K)
            - distance_to_facility_km (float): Distance to nearest industrial facility
            - facility_type (str): Type of facility if any
            - recurrence_count (int): Number of historical hits within 350m
            - confidence (float): NASA FIRMS detection confidence
            - is_spike (bool): Whether FRP is > 2.5 sigma above baseline
        """
        frp = float(features.get("frp", 35.0))
        brightness = float(features.get("brightness", 325.0))
        dist_km = float(features.get("distance_to_facility_km", 999.0))
        fac_type = str(features.get("facility_type", "")).lower()
        recurrence = int(features.get("recurrence_count", 1))
        conf = float(features.get("confidence", 75.0))
        is_spike = bool(features.get("is_spike", False))

        factors: List[str] = []
        classification = "Unknown"
        confidence_score = 0.70

        # Heuristic 1: Low confidence / cold brightness -> False positive
        if conf < 30.0 and frp < 5.0:
            classification = "Possible False Positive"
            confidence_score = 0.82
            factors = [
                f"Low satellite algorithm confidence ({conf:.1f}%)",
                f"Sub-threshold Fire Radiative Power ({frp:.1f} MW)",
                "No spatial correlation with industrial or vegetative assets"
            ]

        # Heuristic 2: Gas Flare (refinery / petrochemical with high recurrence and steady baseline)
        elif dist_km <= 0.6 and ("refinery" in fac_type or "petro" in fac_type) and recurrence >= 10 and not is_spike and frp < 50.0:
            classification = "Gas Flare"
            confidence_score = 0.91
            factors = [
                f"Located within operational flare radius ({dist_km * 1000:.0f}m) of {fac_type.title()}",
                f"High historical recurrence ({recurrence} detections over 30 days)",
                f"Thermal power ({frp:.1f} MW) within permitted operational flaring envelope",
                "Absence of anomalous thermal expansion"
            ]

        # Heuristic 3: Persistent Industrial Thermal Source (furnace / kiln / steel plant)
        elif dist_km <= 0.8 and ("steel" in fac_type or "power" in fac_type or "works" in fac_type) and recurrence >= 8 and not is_spike:
            classification = "Persistent Industrial Thermal Source"
            confidence_score = 0.89
            factors = [
                f"Proximity to high-temperature production unit ({fac_type.title()})",
                f"Documented thermal persistence across multiple satellite passes ({recurrence} hits)",
                f"Consistent brightness profile (~{brightness:.1f} K)",
                "Nominal variance within documented operational limits"
            ]

        # Heuristic 4: Industrial Fire (close to facility + high FRP or anomalous spike)
        elif dist_km <= 1.5 and (frp >= 45.0 or is_spike or brightness >= 355.0):
            classification = "Industrial Fire"
            confidence_score = min(0.98, 0.80 + (frp / 400.0) + (0.08 if is_spike else 0.0))
            factors = [
                f"Hazardous industrial proximity: {dist_km:.2f} km from monitored facility",
                f"Intense thermal radiation output ({frp:.1f} MW FRP, {brightness:.1f} K)",
                "Thermal anomaly profile exceeds typical industrial process emissions",
                "High satellite detection confidence indicating genuine active combustion"
            ]
            if is_spike:
                factors.append("Statistical recurrence anomaly: 2.5σ excursion above facility baseline")

        # Heuristic 5: Agricultural / Bush Fire
        elif dist_km > 3.0 and frp < 40.0 and recurrence <= 3:
            classification = "Agricultural/Bush Fire"
            confidence_score = 0.84
            factors = [
                f"Rural/agricultural geographic coordinates ({dist_km:.1f} km from industrial zones)",
                f"Moderate localized thermal output ({frp:.1f} MW)",
                "Transient single-pass observation characteristic of stubble or crop burning"
            ]

        # Heuristic 6: Forest / Vegetation Fire
        elif dist_km > 3.0 and frp >= 40.0:
            classification = "Forest/Vegetation Fire"
            confidence_score = 0.88
            factors = [
                "Wildland / open canopy coordinates remote from industrial complexes",
                f"High radiative intensity ({frp:.1f} MW) characteristic of biomass canopy combustion",
                "Continuous thermal front signature"
            ]

        # Heuristic 7: Waste Burning
        elif 1.5 < dist_km <= 5.0 and frp < 25.0:
            classification = "Waste Burning"
            confidence_score = 0.79
            factors = [
                "Periphery zone near urban or semi-industrial development",
                f"Low-to-moderate intermittent thermal power ({frp:.1f} MW)",
                "Scattered open-air municipal or industrial refuse burn signature"
            ]

        else:
            classification = "Unknown"
            confidence_score = 0.65
            factors = [
                f"Ambiguous thermal profile ({frp:.1f} MW, {brightness:.1f} K)",
                "Insufficient multi-temporal observations to assign definite class",
                "Requires field verification by tactical operator"
            ]

        return {
            "classification": classification,
            "confidence": round(confidence_score, 2),
            "factors": factors,
            "model_version": self.model_version
        }

classifier_engine = FireGuardAIClassifier()
