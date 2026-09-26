"""
FIREGUARD AI - Explainable AI Risk Scoring Engine (0-100)
Calculates multi-dimensional risk scores and produces clear, human-readable
causal justifications for emergency managers and authorities.
"""
from typing import Dict, Any, Tuple

class RiskScorer:
    @classmethod
    def calculate_risk(
        cls,
        hotspot: Dict[str, Any],
        facility: Dict[str, Any] = None,
        distance_to_facility_m: float = None,
        classification_code: str = "UNKNOWN",
        is_persistent: bool = False,
        near_population_km: float = 1.8,
        near_critical_infra: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates an explainable risk score (0 - 100) with detailed factor attribution.
        """
        frp = float(hotspot.get("frp_mw", 15.0))
        brightness = float(hotspot.get("brightness_k", 320.0))
        confidence = int(hotspot.get("confidence", 70))
        
        # 1. Proximity & Hazard Tier of Industrial Facility (Weight: 30 pts)
        pts_facility = 0.0
        reason_fac = ""
        if distance_to_facility_m is not None:
            fac_hazard = facility.get("hazard_category", "STANDARD") if facility else "STANDARD"
            fac_name = facility.get("name", "Industrial Site") if facility else "Facility"
            
            if distance_to_facility_m <= 250:
                mult = 1.0 if fac_hazard == "HAZMAT_TIER_1" else 0.85
                pts_facility = 30.0 * mult
                reason_fac = f"Thermal source located directly within {int(distance_to_facility_m)}m perimeter of high-hazard asset ({fac_name})"
            elif distance_to_facility_m <= 750:
                pts_facility = 22.0
                reason_fac = f"Thermal source detected {int(distance_to_facility_m)}m from industrial facility ({fac_name})"
            elif distance_to_facility_m <= 2000:
                pts_facility = 12.0
                reason_fac = f"Moderate proximity ({round(distance_to_facility_m/1000, 1)} km) to industrial zone"
            else:
                pts_facility = 4.0
                reason_fac = f"Isolated location > 2 km from nearest registered plant ({round(distance_to_facility_m/1000, 1)} km)"
        else:
            pts_facility = 5.0
            reason_fac = "No immediate registered industrial facility within 3km"

        # 2. Thermal Intensity & Energy Release (Weight: 25 pts)
        pts_intensity = 0.0
        reason_int = ""
        if frp >= 90.0:
            pts_intensity = 25.0
            reason_int = f"Extreme Fire Radiative Power ({round(frp, 1)} MW) represents severe, runaway thermal release"
        elif frp >= 50.0:
            pts_intensity = 20.0
            reason_int = f"High Fire Radiative Power ({round(frp, 1)} MW) exceeds standard industrial thermal baselines"
        elif frp >= 25.0:
            pts_intensity = 13.0
            reason_int = f"Moderate radiative power ({round(frp, 1)} MW)"
        else:
            pts_intensity = 6.0
            reason_int = f"Low thermal radiative energy ({round(frp, 1)} MW)"

        # 3. NASA FIRMS Observation Confidence (Weight: 15 pts)
        pts_confidence = (confidence / 100.0) * 15.0
        reason_conf = f"Satellite detection confidence rated at {confidence}%"

        # 4. Proximity to Population / Habitation (Weight: 10 pts)
        pts_population = 0.0
        reason_pop = ""
        if near_population_km <= 1.0:
            pts_population = 10.0
            reason_pop = f"Dense civilian population within {round(near_population_km, 1)} km; high exposure risk"
        elif near_population_km <= 3.0:
            pts_population = 6.5
            reason_pop = f"Civilian settlements located {round(near_population_km, 1)} km downwind"
        else:
            pts_population = 2.0
            reason_pop = f"Sparse or distant population buffer (> 3 km)"

        # 5. Critical Infrastructure Exposure (Weight: 10 pts)
        pts_infra = 0.0
        reason_infra = ""
        if near_critical_infra and pts_facility > 10.0:
            pts_infra = 10.0
            reason_infra = "Critical infrastructure (pipelines, power substations, or arterial highway) adjacent to site"
        elif near_critical_infra:
            pts_infra = 5.0
            reason_infra = "Secondary transport or electrical corridor in vicinity"
        else:
            pts_infra = 1.0
            reason_infra = "No critical lifeline infrastructure in immediate proximity"

        # 6. Classification & Persistence Delta (Weight: 10 pts)
        pts_persistence = 0.0
        reason_persist = ""
        if classification_code == "INDUSTRIAL_FIRE":
            pts_persistence = 10.0
            reason_persist = "Classified as active Industrial Fire emergency"
        elif classification_code in ["PERSISTENT_IND", "GAS_FLARE"]:
            pts_persistence = 3.0  # Controlled routine emissions carry lower risk
            reason_persist = "Documented persistent source / routine flare under ongoing monitoring"
        elif classification_code == "FALSE_POS":
            pts_persistence = 0.0
            reason_persist = "Flagged as potential false positive / reflection"
        else:
            pts_persistence = 5.0
            reason_persist = f"Classified as {classification_code}"

        # Total Composite Calculation
        raw_total = (pts_facility + pts_intensity + pts_confidence +
                     pts_population + pts_infra + pts_persistence)
        
        # Override for explicit false positives
        if classification_code == "FALSE_POS":
            total_score = min(22.0, raw_total * 0.3)
        else:
            total_score = min(100.0, max(5.0, raw_total))

        # Risk Tier Mapping
        if total_score >= 80.0:
            risk_tier = "CRITICAL"
        elif total_score >= 60.0:
            risk_tier = "HIGH"
        elif total_score >= 30.0:
            risk_tier = "MODERATE"
        else:
            risk_tier = "LOW"

        breakdown = {
            "facility_proximity_pts": round(pts_facility, 1),
            "thermal_intensity_pts": round(pts_intensity, 1),
            "satellite_confidence_pts": round(pts_confidence, 1),
            "population_exposure_pts": round(pts_population, 1),
            "critical_infrastructure_pts": round(pts_infra, 1),
            "classification_factor_pts": round(pts_persistence, 1)
        }

        reasons = [r for r in [reason_fac, reason_int, reason_conf, reason_pop, reason_infra, reason_persist] if r]

        why_text = f"Risk evaluated as {risk_tier} ({round(total_score, 1)}/100):\n" + "\n".join(f"• {r}" for r in reasons)

        return {
            "total_score": round(total_score, 1),
            "risk_tier": risk_tier,
            "factor_breakdown": breakdown,
            "why_explanation": why_text,
            "bullet_reasons": reasons
        }
